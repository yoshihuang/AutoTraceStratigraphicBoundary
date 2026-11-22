# -*- coding: utf-8 -*-
"""Geometry from a GeoModel: unit solids, horizons, fault planes, terrain, sections."""
import math
import re

import numpy as np

from .mesh import Grid, grid_surface, isosurface
from .model3d import AIR


def nice_interval(rng, target=8):
    r = rng / float(target)
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000):
        if s >= r:
            return s
    return 10000


def model_grid(model, cell):
    """Cell-centred grid with one node row outside the model box on every side.

    The box faces then lie half-way between two node rows, so the contacts on the
    faces are interpolated smoothly (no stair steps) and the solids close on the box.
    """
    x0, y0, x1, y1 = model.extent
    nx = max(2, int(round((x1 - x0) / cell)))
    ny = max(2, int(round((y1 - y0) / cell)))
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    ztop = model.topo.max + cell
    dz = max(cell * 0.5, (ztop - model.zbase) / 60.0)
    nz = int(math.ceil((ztop - model.zbase) / dz))
    return Grid(x0 - dx / 2.0, y0 - dy / 2.0, model.zbase - dz / 2.0, dx, dy, dz, nx + 2, ny + 2, nz + 2)


def unit_solids(model, cell, progress=None):
    """{unit index: (verts, faces)} closed meshes clipped by topography and the model box."""
    grid = model_grid(model, cell)
    X, Y, Z = grid.nodes()
    x0, y0, x1, y1 = model.extent
    box = np.minimum.reduce([X - x0, x1 - X, Y - y0, y1 - Y, Z - model.zbase])
    ground = model.topo(X.ravel(), Y.ravel()).reshape(X.shape) - Z
    clip = np.minimum(box, ground)
    out = {}
    for n, ui in enumerate(range(len(model.units))):
        if progress:
            progress(n / float(len(model.units)))
        g = model.unit_inside(ui, X.ravel(), Y.ravel(), Z.ravel()).reshape(X.shape)
        g = np.minimum(g, clip)
        if not (g > 0).any():
            continue
        verts, faces = isosurface(grid, g, 0.0)
        if len(faces):
            out[ui] = (verts, faces)
    return out


def horizons(model, cell):
    """[(series id, unit below, unit above, level, verts, faces)] below the ground surface."""
    grid = model_grid(model, cell)
    X, Y, Z = grid.nodes()
    x0, y0, x1, y1 = model.extent
    inside = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= model.zbase)
    inside &= Z <= model.topo(X.ravel(), Y.ravel()).reshape(X.shape)
    res = []
    for S in model.series:
        if S.field is None:
            continue
        f = model.field_value(S, X.ravel(), Y.ravel(), Z.ravel()).reshape(X.shape)
        valid = inside.copy()
        for T in model.series:
            if T.sid > S.sid and T.field is not None:
                valid &= model.field_value(T, X.ravel(), Y.ravel(), Z.ravel()).reshape(X.shape) < T.levels[0]
        start = 1 if S.is_base else 0
        for k in range(start, len(S.levels)):
            below = S.units[k - 1] if k > 0 else None
            above = S.units[k] if k < len(S.units) else None
            if S.is_base:
                below, above = S.units[k - 1], S.units[k]
            v = np.where(valid, f - S.levels[k], np.nan)
            verts, faces = isosurface(grid, v, 0.0)
            if len(faces):
                res.append((S.sid, below, above, S.levels[k], verts, faces))
    return res


def fault_planes(model, step):
    """[(Fault, verts, faces)]: each trace projected down-dip to the model base."""
    out = []
    for flt in model.faults:
        tr = np.array(flt.trace)
        pts = [tr[0]]
        for a, b in zip(tr[:-1], tr[1:]):
            n = max(1, int(math.ceil(np.hypot(*(b - a)) / step)))
            for i in range(1, n + 1):
                pts.append(a + (b - a) * i / n)
        pts = np.array(pts)
        zt = model.topo(pts[:, 0], pts[:, 1])
        horiz = (zt - model.zbase) / max(math.tan(math.radians(flt.dip)), 1e-3)
        bot = pts + np.outer(horiz, flt.dip_vec)
        n = len(pts)
        verts = np.vstack([np.column_stack([pts, zt]), np.column_stack([bot, np.full(n, model.zbase)])])
        i = np.arange(n - 1)
        faces = np.concatenate([np.column_stack([i, i + 1, n + i + 1]), np.column_stack([i, n + i + 1, n + i])])
        out.append((flt, verts, faces))
    return out


def terrain(model, n=160):
    """Ground surface mesh and the unit at each face."""
    x0, y0, x1, y1 = model.extent
    s = max(x1 - x0, y1 - y0) / float(n)
    xs = np.linspace(x0, x1, int(round((x1 - x0) / s)) + 1)
    ys = np.linspace(y0, y1, int(round((y1 - y0) / s)) + 1)
    X, Y = np.meshgrid(xs, ys)
    Z = model.topo(X.ravel(), Y.ravel()).reshape(X.shape)
    verts, faces = grid_surface(xs, ys, Z)
    cen = verts[faces].mean(axis=1)
    units = model.unit_index(cen[:, 0], cen[:, 1], cen[:, 2] - 0.5, clip_topo=False)
    return verts, faces, units


# ----------------------------------------------------------------------------- sections
def end_labels(name):
    """'A-A'' / 'A–A'' / 'A A'' -> ('A', "A'"); 'A' -> ('A', "A'")."""
    n = str(name).strip()
    m = re.match(r"^(.+?)\s*[-–—~ ]\s*(.+)$", n)
    if m and m.group(2).rstrip("'’′") == m.group(1).rstrip("'’′"):
        return m.group(1), m.group(2)
    return n, n + "'"


class Section(object):
    def __init__(self, name, pts):
        self.name = name
        self.start, self.end = end_labels(name)
        self.title = "%s–%s" % (self.start, self.end)
        self.pts = np.array(pts, dtype=np.float64)
        seg = np.hypot(*(self.pts[1:] - self.pts[:-1]).T)
        self.cum = np.concatenate([[0.0], np.cumsum(seg)])
        self.length = float(self.cum[-1])

    def at(self, s):
        s = np.clip(np.asarray(s, dtype=np.float64), 0, self.length)
        x = np.interp(s, self.cum, self.pts[:, 0])
        y = np.interp(s, self.cum, self.pts[:, 1])
        return x, y


def section_raster(model, sec, ncols=600, nrows=None):
    """Unit index raster of a section: rows from ztop (row 0) down to the model base."""
    ds = sec.length / ncols
    s = (np.arange(ncols) + 0.5) * ds
    x, y = sec.at(s)
    ground = model.topo(x, y)
    zt = float(ground.max())
    step = nice_interval(zt - model.zbase)
    ztop = math.ceil((zt + 0.05 * (zt - model.zbase)) / step) * step
    if nrows is None:
        nrows = int(max(80, min(600, round((ztop - model.zbase) / ds))))
    dz = (ztop - model.zbase) / nrows
    zc = ztop - (np.arange(nrows) + 0.5) * dz
    S, Zc = np.meshgrid(s, zc)
    Xg, Yg = sec.at(S.ravel())
    U = model.unit_index(Xg, Yg, Zc.ravel(), clip_topo=False).reshape(nrows, ncols)
    U[Zc > np.interp(S, s, ground)] = AIR
    # finer ground profile
    sp = np.linspace(0, sec.length, max(2, ncols * 2 + 1))
    xp, yp = sec.at(sp)
    profile = np.column_stack([sp, model.topo(xp, yp)])
    # fault traces: zero crossings of each fault function in every column
    traces = []
    for flt in model.faults:
        fv = flt.value(Xg, Yg, Zc.ravel()).reshape(nrows, ncols)
        pts = []
        for c in range(ncols):
            col = fv[:, c]
            ch = np.where(np.sign(col[:-1]) != np.sign(col[1:]))[0]
            if len(ch) == 0:
                pts.append(None)
                continue
            r = ch[0]
            t = col[r] / (col[r] - col[r + 1])
            z = zc[r] - t * dz
            pts.append((s[c], z) if z <= ground[c] + 1e-6 else None)
        run = []
        for p in pts + [None]:
            if p is None:
                if len(run) >= 2:
                    traces.append((flt, run))
                run = []
            else:
                run.append(p)
    return dict(U=U, ds=ds, dz=dz, ztop=ztop, zbase=model.zbase, profile=profile, faults=traces, s=s)


def auto_section(model, mean_dipdir=None, name="A"):
    """A straight section through the model centre, perpendicular to the mean strike."""
    x0, y0, x1, y1 = model.extent
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    az = mean_dipdir if mean_dipdir is not None else 90.0
    dx, dy = math.sin(math.radians(az)), math.cos(math.radians(az))
    ts = []
    for v, d, lo, hi in ((cx, dx, x0, x1), (cy, dy, y0, y1)):
        if abs(d) > 1e-9:
            ts.extend([(lo - v) / d, (hi - v) / d])
    tpos = min(t for t in ts if t > 0)
    tneg = max(t for t in ts if t < 0)
    a = (cx + dx * tneg * 0.98, cy + dy * tneg * 0.98)
    b = (cx + dx * tpos * 0.98, cy + dy * tpos * 0.98)
    return Section(name, [a, b])
