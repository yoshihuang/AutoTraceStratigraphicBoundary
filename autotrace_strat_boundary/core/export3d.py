# -*- coding: utf-8 -*-
"""3D CAD exports: DXF (polyface meshes), Wavefront OBJ + MTL, binary STL.

meshes: list of dict(name, color "#rrggbb", verts (n, 3), faces (m, 3))
Coordinates are written in the map CRS (absolute values, metres).
"""
import colorsys
import os
import re
import struct

import numpy as np


def hex_rgb(c):
    c = (c or "#bbbbbb").lstrip("#")
    if len(c) < 6:
        c = "bbbbbb"
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def safe_name(name):
    s = re.sub(r"[^0-9A-Za-z_\-一-鿿]+", "_", str(name)).strip("_")
    return s or "layer"


# ----------------------------------------------------------------------------- OBJ
def write_obj(path, meshes):
    mtl = os.path.splitext(path)[0] + ".mtl"
    with open(mtl, "w", encoding="utf-8") as fh:
        for m in meshes:
            r, g, b = (v / 255.0 for v in hex_rgb(m["color"]))
            fh.write("newmtl %s\nKd %.4f %.4f %.4f\nKa 0 0 0\nd %.3f\nillum 1\n\n" % (
                safe_name(m["name"]), r, g, b, m.get("opacity", 1.0)))
    base = 1
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# AutoTrace Stratigraphic Boundary - 3D geological model\n")
        fh.write("mtllib %s\n" % os.path.basename(mtl))
        for m in meshes:
            v, f = m["verts"], m["faces"]
            fh.write("o %s\ng %s\nusemtl %s\n" % ((safe_name(m["name"]),) * 3))
            fh.write("".join("v %.3f %.3f %.3f\n" % tuple(p) for p in v))
            fh.write("".join("f %d %d %d\n" % tuple(t) for t in (f + base)))
            base += len(v)
    return [path, mtl]


# ----------------------------------------------------------------------------- STL
def write_stl(path, meshes):
    """One binary STL per mesh: <path base>_<name>.stl. Returns the file list."""
    out = []
    root = os.path.splitext(path)[0]
    for m in meshes:
        p = "%s_%s.stl" % (root, safe_name(m["name"]))
        T = m["verts"][m["faces"]].astype(np.float64)
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ln[ln == 0] = 1
        n = n / ln[:, None]
        rec = np.zeros(len(T), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
        rec["n"] = n
        rec["v"] = T
        with open(p, "wb") as fh:
            fh.write(struct.pack("<80sI", ("AutoTrace model %s" % safe_name(m["name"])).encode("ascii", "replace")[:80],
                                 len(T)))
            fh.write(rec.tobytes())
        out.append(p)
    return out


# ----------------------------------------------------------------------------- DXF
def _aci_palette():
    pal = {1: (255, 0, 0), 2: (255, 255, 0), 3: (0, 255, 0), 4: (0, 255, 255), 5: (0, 0, 255),
           6: (255, 0, 255), 7: (255, 255, 255), 8: (128, 128, 128), 9: (192, 192, 192)}
    vals = [1.0, 1.0, 0.65, 0.65, 0.5, 0.5, 0.3, 0.3, 0.15, 0.15]
    for aci in range(10, 250):
        h = ((aci - 10) // 10) * 15 / 360.0
        k = aci % 10
        s = 1.0 if k % 2 == 0 else 0.5
        r, g, b = colorsys.hsv_to_rgb(h, s, vals[k])
        pal[aci] = (int(r * 255), int(g * 255), int(b * 255))
    for i, aci in enumerate(range(250, 256)):
        v = int(51 + i * 40.8)
        pal[aci] = (v, v, v)
    return pal


_ACI = _aci_palette()


def nearest_aci(color):
    r, g, b = hex_rgb(color)
    sat = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
    keys = [k for k in _ACI if sat < 0.12 or k not in (7, 8, 9, 250, 251, 252, 253, 254, 255)]
    return min(keys, key=lambda k: (_ACI[k][0] - r) ** 2 + (_ACI[k][1] - g) ** 2 + (_ACI[k][2] - b) ** 2)


def _chunks(verts, faces, limit=32000):
    """Split a mesh into pieces of at most *limit* vertices (R12 polyface limit 32767)."""
    if len(verts) <= limit:
        yield verts, faces
        return
    start = 0
    while start < len(faces):
        used = {}
        end = start
        while end < len(faces):
            new = [v for v in faces[end] if v not in used]
            if len(used) + len(new) > limit:
                break
            for v in new:
                used[v] = len(used)
            end += 1
        sub = np.array([[used[v] for v in f] for f in faces[start:end]])
        order = np.empty(len(used), dtype=np.int64)
        for v, k in used.items():
            order[k] = v
        yield verts[order], sub
        start = end


def write_dxf(path, meshes, polylines=None):
    """DXF R12 (AC1009): every mesh is a POLYFACE MESH on its own layer; polylines = [(layer, color, pts3d)]."""
    polylines = polylines or []
    layers = []
    for m in meshes:
        layers.append((safe_name(m["name"]), nearest_aci(m["color"])))
    for name, color, _ in polylines:
        if safe_name(name) not in [n for n, _ in layers]:
            layers.append((safe_name(name), nearest_aci(color)))
    allv = [m["verts"] for m in meshes if len(m["verts"])]
    lo = np.min([v.min(axis=0) for v in allv], axis=0) if allv else np.zeros(3)
    hi = np.max([v.max(axis=0) for v in allv], axis=0) if allv else np.zeros(3)
    with open(path, "w", encoding="ascii", errors="replace") as fh:
        w = fh.write
        w("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n")
        w("9\n$EXTMIN\n10\n%.3f\n20\n%.3f\n30\n%.3f\n" % tuple(lo))
        w("9\n$EXTMAX\n10\n%.3f\n20\n%.3f\n30\n%.3f\n0\nENDSEC\n" % tuple(hi))
        w("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n%d\n" % (len(layers) + 1))
        w("0\nLAYER\n2\n0\n70\n0\n62\n7\n6\nCONTINUOUS\n")
        for name, aci in layers:
            w("0\nLAYER\n2\n%s\n70\n0\n62\n%d\n6\nCONTINUOUS\n" % (name.encode("ascii", "replace").decode(), aci))
        w("0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n")
        for m in meshes:
            lay = safe_name(m["name"]).encode("ascii", "replace").decode()
            for verts, faces in _chunks(m["verts"], m["faces"]):
                w("0\nPOLYLINE\n8\n%s\n66\n1\n10\n0\n20\n0\n30\n0\n70\n64\n71\n%d\n72\n%d\n"
                  % (lay, len(verts), len(faces)))
                w("".join("0\nVERTEX\n8\n%s\n10\n%.2f\n20\n%.2f\n30\n%.2f\n70\n192\n" % (lay, p[0], p[1], p[2])
                          for p in verts))
                w("".join("0\nVERTEX\n8\n%s\n10\n0\n20\n0\n30\n0\n70\n128\n71\n%d\n72\n%d\n73\n%d\n"
                          % (lay, f[0] + 1, f[1] + 1, f[2] + 1) for f in faces))
                w("0\nSEQEND\n8\n%s\n" % lay)
        for name, color, pts in polylines:
            lay = safe_name(name).encode("ascii", "replace").decode()
            w("0\nPOLYLINE\n8\n%s\n66\n1\n70\n8\n" % lay)
            for p in pts:
                w("0\nVERTEX\n8\n%s\n10\n%.3f\n20\n%.3f\n30\n%.3f\n70\n32\n" % (lay, p[0], p[1], p[2]))
            w("0\nSEQEND\n8\n%s\n" % lay)
        w("0\nENDSEC\n0\nEOF\n")
    return [path]
