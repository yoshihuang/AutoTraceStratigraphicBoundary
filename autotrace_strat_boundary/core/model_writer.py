# -*- coding: utf-8 -*-
"""Write model results: GeoPackage layers, section sheet, viewer HTML."""
import base64
import json
import math
import os

import numpy as np
from osgeo import gdal, ogr

from qgis.core import (QgsCoordinateTransformContext, QgsFeature, QgsFields, QgsGeometry, QgsLineString,
                       QgsPoint, QgsPointXY, QgsPolygon, QgsVectorFileWriter)
from qgis.PyQt.QtCore import QBuffer, QByteArray, QIODevice
from qgis.PyQt.QtGui import QImage

from .. import compat
from .model3d import AIR
from .model_outputs import nice_interval

VIEWER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "viewer3d")

_TRI_DT = np.dtype([("bo", "u1"), ("t", "<u4"), ("nr", "<u4"), ("np", "<u4"), ("c", "<f8", (12,))])


def triangles_wkb(verts, faces):
    """MultiPolygonZ WKB (ISO) of triangles."""
    T = verts[faces]
    rec = np.zeros(len(T), dtype=_TRI_DT)
    rec["bo"] = 1
    rec["t"] = 1003
    rec["nr"] = 1
    rec["np"] = 4
    ring = np.concatenate([T, T[:, :1]], axis=1).reshape(len(T), 12)
    rec["c"] = ring
    head = np.zeros(1, dtype=np.dtype([("bo", "u1"), ("t", "<u4"), ("n", "<u4")]))
    head["bo"], head["t"], head["n"] = 1, 1006, len(T)
    return head.tobytes() + rec.tobytes()


def geom_from_wkb(wkb):
    g = QgsGeometry()
    g.fromWkb(wkb)
    return g


def _fields(spec):
    f = QgsFields()
    make = {"s": compat.field_string, "i": compat.field_int, "d": compat.field_double}
    for name, t in spec:
        f.append(make[t](name))
    return f


class GpkgWriter(object):
    def __init__(self, path, crs):
        self.path = path
        self.crs = crs
        self.first = True
        self.layers = []
        if os.path.exists(path):
            os.remove(path)

    def add(self, name, wkb_type, spec, rows, crs=None):
        """rows: list of (QgsGeometry or None, [attrs])."""
        fields = _fields(spec)
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = name
        opts.fileEncoding = "UTF-8"
        opts.actionOnExistingFile = compat._enum(
            "QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile" if self.first
            else "QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer",
            "QgsVectorFileWriter.CreateOrOverwriteFile" if self.first else "QgsVectorFileWriter.CreateOrOverwriteLayer")
        w = QgsVectorFileWriter.create(self.path, fields, wkb_type, crs if crs is not None else self.crs,
                                       QgsCoordinateTransformContext(), opts)
        if w.hasError() != compat._enum("QgsVectorFileWriter.WriterError.NoError", "QgsVectorFileWriter.NoError"):
            raise IOError("GeoPackage layer %s: %s" % (name, w.errorMessage()))
        for geom, attrs in rows:
            f = QgsFeature(fields)
            if geom is not None:
                f.setGeometry(geom)
            f.setAttributes(list(attrs))
            w.addFeature(f)
        del w
        self.first = False
        self.layers.append(name)


WKB = {
    "mpz": ("Qgis.WkbType.MultiPolygonZ", "QgsWkbTypes.MultiPolygonZ"),
    "mp": ("Qgis.WkbType.MultiPolygon", "QgsWkbTypes.MultiPolygon"),
    "ls": ("Qgis.WkbType.LineString", "QgsWkbTypes.LineString"),
    "lsz": ("Qgis.WkbType.LineStringZ", "QgsWkbTypes.LineStringZ"),
    "pt": ("Qgis.WkbType.Point", "QgsWkbTypes.Point"),
    "none": ("Qgis.WkbType.NoGeometry", "QgsWkbTypes.NoGeometry"),
}


def wkb_type(key):
    return compat._enum(*WKB[key])


# ----------------------------------------------------------------------------- sections
def hex_rgb(c):
    c = (c or "#bbbbbb").lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) if len(c) >= 6 else (187, 187, 187)


def section_polygons(res, sheet_x0, sheet_y0, ve):
    """Unit polygons of a section raster in sheet coordinates: [(unit index, QgsGeometry)]."""
    U = res["U"]
    nrows, ncols = U.shape
    mem = gdal.GetDriverByName("MEM").Create("", ncols, nrows, 1, gdal.GDT_Int32)
    h = (res["ztop"] - res["zbase"]) * ve
    mem.SetGeoTransform((sheet_x0, res["ds"], 0, sheet_y0 + h, 0, -res["dz"] * ve))
    band = mem.GetRasterBand(1)
    band.WriteArray(U.astype(np.int32))
    mask = gdal.GetDriverByName("MEM").Create("", ncols, nrows, 1, gdal.GDT_Byte)
    mask.SetGeoTransform(mem.GetGeoTransform())
    mask.GetRasterBand(1).WriteArray((U >= 0).astype(np.uint8))
    drv = ogr.GetDriverByName("MEM") or ogr.GetDriverByName("Memory")
    vds = drv.CreateDataSource("sec")
    lyr = vds.CreateLayer("p", geom_type=ogr.wkbPolygon)
    lyr.CreateField(ogr.FieldDefn("u", ogr.OFTInteger))
    gdal.Polygonize(band, mask.GetRasterBand(1), lyr, 0, [], callback=None)
    out = []
    for feat in lyr:
        og = feat.GetGeometryRef()
        g = QgsGeometry()
        g.fromWkb(bytes(og.ExportToIsoWkb()))
        out.append((feat.GetField(0), g))
    return out


def sheet_to_world(geom, sec, sheet_x0, sheet_y0, zbase, ve, step):
    """Sheet polygon -> vertical 3D polygon on the section line (PolygonZ list)."""
    out = []
    g = geom.densifyByDistance(step) if step > 0 else geom
    from .geom_utils import polygon_parts
    for part in polygon_parts(g):
        rings = []
        for ring in part.asPolygon():
            xs = np.array([p.x() for p in ring]) - sheet_x0
            zs = (np.array([p.y() for p in ring]) - sheet_y0) / ve + zbase
            wx, wy = sec.at(xs)
            rings.append(QgsLineString([QgsPoint(float(a), float(b), float(c)) for a, b, c in zip(wx, wy, zs)]))
        if not rings:
            continue
        poly = QgsPolygon()
        poly.setExteriorRing(rings[0])
        for r in rings[1:]:
            poly.addInteriorRing(r)
        out.append(QgsGeometry(poly))
    return out


def section_image(res, colors, max_w=1600):
    """RGBA PNG (data URI) of a section raster; air is transparent, unit contacts darkened."""
    U = res["U"]
    nrows, ncols = U.shape
    rgb = np.zeros((nrows, ncols, 4), dtype=np.uint8)
    pal = np.array([hex_rgb(c) for c in colors] + [(255, 255, 255)], dtype=np.uint8)
    idx = np.where(U >= 0, U, len(colors))
    rgb[..., :3] = pal[idx]
    rgb[..., 3] = np.where(U == AIR, 0, 255)
    edge = np.zeros(U.shape, dtype=bool)
    edge[:, :-1] |= (U[:, :-1] != U[:, 1:]) & (U[:, :-1] >= 0) & (U[:, 1:] >= 0)
    edge[:-1, :] |= (U[:-1, :] != U[1:, :]) & (U[:-1, :] >= 0) & (U[1:, :] >= 0)
    rgb[edge, :3] = 40
    data = np.ascontiguousarray(rgb).tobytes()
    img = QImage(data, ncols, nrows, ncols * 4, QImage.Format.Format_RGBA8888).copy()
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    buf.close()
    return "data:image/png;base64," + base64.b64encode(bytes(ba)).decode("ascii")


def section_annotations(sec, res, sheet_x0, sheet_y0, ve, label):
    """Frame / tick lines and label points of a section sheet."""
    h = (res["ztop"] - res["zbase"]) * ve
    L = sec.length
    x1, y1 = sheet_x0 + L, sheet_y0 + h
    lines, labels = [], []
    frame = [QgsPointXY(sheet_x0, sheet_y0), QgsPointXY(x1, sheet_y0), QgsPointXY(x1, y1),
             QgsPointXY(sheet_x0, y1), QgsPointXY(sheet_x0, sheet_y0)]
    lines.append((QgsGeometry.fromPolylineXY(frame), "frame"))
    tick = max(L, h) * 0.012
    zi = nice_interval(res["ztop"] - res["zbase"])
    z = math.ceil(res["zbase"] / zi) * zi
    while z <= res["ztop"] + 1e-6:
        y = sheet_y0 + (z - res["zbase"]) * ve
        lines.append((QgsGeometry.fromPolylineXY([QgsPointXY(sheet_x0 - tick, y), QgsPointXY(sheet_x0, y)]), "tick"))
        lines.append((QgsGeometry.fromPolylineXY([QgsPointXY(x1, y), QgsPointXY(x1 + tick, y)]), "tick"))
        labels.append((QgsPointXY(sheet_x0 - tick * 1.5, y), "%g" % z, "elev_l"))
        labels.append((QgsPointXY(x1 + tick * 1.5, y), "%g" % z, "elev_r"))
        z += zi
    di = nice_interval(L)
    d = 0.0
    while d <= L + 1e-6:
        x = sheet_x0 + d
        lines.append((QgsGeometry.fromPolylineXY([QgsPointXY(x, sheet_y0), QgsPointXY(x, sheet_y0 - tick)]), "tick"))
        labels.append((QgsPointXY(x, sheet_y0 - tick * 1.6), "%g" % d, "dist"))
        d += di
    g0 = float(res["profile"][0, 1])
    g1 = float(res["profile"][-1, 1])
    labels.append((QgsPointXY(sheet_x0, sheet_y0 + (g0 - res["zbase"]) * ve + tick * 2), sec.start, "end"))
    labels.append((QgsPointXY(x1, sheet_y0 + (g1 - res["zbase"]) * ve + tick * 2), sec.end, "end"))
    labels.append((QgsPointXY(sheet_x0 + L / 2.0, y1 + tick * 3), label, "title"))
    return lines, labels


# ----------------------------------------------------------------------------- viewer
def _b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode("ascii")


def viewer_mesh(kind, name, color, verts, faces, center, unit=None, face_colors=None):
    cx, cy = center
    if face_colors is not None:  # non-indexed with per-vertex colours
        T = verts[faces].reshape(-1, 3).copy()
        T[:, 0] -= cx
        T[:, 1] -= cy
        col = np.repeat(face_colors, 3, axis=0).astype(np.uint8)
        return dict(kind=kind, name=name, color=color, unit=unit, pos=_b64(T.astype(np.float32)), col=_b64(col))
    V = verts.copy()
    V[:, 0] -= cx
    V[:, 1] -= cy
    return dict(kind=kind, name=name, color=color, unit=unit, pos=_b64(V.astype(np.float32)),
                idx=_b64(faces.astype(np.uint32)))


def write_viewer(path, data):
    def read(name):
        with open(os.path.join(VIEWER_DIR, name), "r", encoding="utf-8") as fh:
            return fh.read()

    page = read("template.html")
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for key, text in (("/*THREE_JS*/", read("three.min.js")), ("/*ORBIT_JS*/", read("OrbitControls.js")),
                      ("/*DATA_JSON*/", js)):
        page = page.replace(key, text.replace("</script", "<\\/script"), 1)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path
