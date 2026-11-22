# -*- coding: utf-8 -*-
"""Implicit 3D geological model (potential-field method), numpy only.

Same approach as the geomap-workbench web app (yoshihuang.github.io/geomap-workbench):

* Units are grouped into *series* (conformable packages); a younger series lies
  above an unconformity (its *base*).
* For every series a scalar potential field f(x, y, z) is interpolated with a
  cubic radial basis function (kernel r^3) from
    - interface points: contacts between stratigraphically adjacent units,
      sampled on the geological map and given the DEM elevation; every contact
      of the series is an iso-value of f whose level is solved as an unknown;
    - gradient constraints: bedding attitudes (unit normal vectors, pointing to
      the younger side; overturned beds are flipped);
    - one drift term per fault (indicator of the hanging-wall side), which lets
      the field jump across the fault plane.
* A point belongs to the youngest series whose field is above that series'
  base level, and to the unit whose level interval contains the field value.
* Igneous (kind = "ign") map polygons are extruded vertically.
"""
import math

import numpy as np

NUG = 1e-7
AIR = -1
NONE = -2


class Unit(object):
    def __init__(self, code, name=None, order=0, series=1, thick=None, kind="sed", color=None):
        self.code = code
        self.name = name or code
        self.order = order
        self.series = series
        self.thick = thick
        self.kind = "ign" if str(kind or "").lower().startswith("ign") else "sed"
        self.color = color or "#bbbbbb"


# ----------------------------------------------------------------------------- topography
class Topography(object):
    """Bilinear sampler on a DEM array (row 0 = north). NaN holes are filled."""

    def __init__(self, arr, gt):
        a = np.array(arr, dtype=np.float64)
        self.arr = fill_nan(a)
        self.gt = gt
        self.min = float(np.nanmin(self.arr))
        self.max = float(np.nanmax(self.arr))

    def __call__(self, x, y):
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        ny, nx = self.arr.shape
        fc = np.clip((x - self.gt[0]) / self.gt[1] - 0.5, 0, nx - 1.000001)
        fr = np.clip((y - self.gt[3]) / self.gt[5] - 0.5, 0, ny - 1.000001)
        c0 = np.minimum(fc.astype(int), nx - 2) if nx > 1 else np.zeros_like(fc, dtype=int)
        r0 = np.minimum(fr.astype(int), ny - 2) if ny > 1 else np.zeros_like(fr, dtype=int)
        tc, tr = fc - c0, fr - r0
        a = self.arr
        c1 = np.minimum(c0 + 1, nx - 1)
        r1 = np.minimum(r0 + 1, ny - 1)
        return (a[r0, c0] * (1 - tc) * (1 - tr) + a[r0, c1] * tc * (1 - tr)
                + a[r1, c0] * (1 - tc) * tr + a[r1, c1] * tc * tr)


def fill_nan(a, max_iter=500):
    """Fill NaN cells by iterative averaging of valid neighbours."""
    a = a.copy()
    if not np.isnan(a).any():
        return a
    if np.isnan(a).all():
        return np.zeros_like(a)
    for _ in range(max_iter):
        m = np.isnan(a)
        if not m.any():
            break
        p = np.pad(a, 1, mode="edge")
        stack = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        valid = ~np.isnan(stack)
        cnt = valid.sum(axis=0)
        s = np.where(valid, stack, 0).sum(axis=0)
        upd = m & (cnt > 0)
        a[upd] = s[upd] / cnt[upd]
    a[np.isnan(a)] = np.nanmean(a)
    return a


# ----------------------------------------------------------------------------- faults
def az_vec(az):
    r = math.radians(az)
    return math.sin(r), math.cos(r)


class Fault(object):
    """Fault surface = its map trace projected down-dip (planar dip, curved trace)."""

    def __init__(self, name, trace, dip, dipdir, topo):
        self.name = name
        self.trace = [(float(x), float(y)) for x, y in trace]
        self.dip = float(dip)
        self.topo = topo
        a = np.array(self.trace[:-1])
        b = np.array(self.trace[1:])
        d = b - a
        L = np.hypot(d[:, 0], d[:, 1])
        L[L == 0] = 1.0
        self.a, self.L = a, L
        self.u = d / L[:, None]
        self.r = np.stack([self.u[:, 1], -self.u[:, 0]], axis=1)  # right normal
        sx, sy = (self.r * L[:, None]).sum(axis=0)
        D = az_vec(dipdir if dipdir is not None else 0.0)
        if dipdir is None:  # unknown: dip to the right of the trace direction
            self.side = 1.0
        else:
            self.side = 1.0 if sx * D[0] + sy * D[1] >= 0 else -1.0
        self.cd = math.cos(math.radians(self.dip))
        self.sd = math.sin(math.radians(self.dip))
        ex, ey = sx * self.side, sy * self.side
        n = math.hypot(ex, ey) or 1.0
        self.dip_vec = (ex / n, ey / n)  # effective horizontal dip direction

    def value(self, X, Y, Z):
        """> 0 on the hanging-wall side, 0 on the fault surface."""
        X = np.asarray(X, dtype=np.float64).ravel()
        Y = np.asarray(Y, dtype=np.float64).ravel()
        Z = np.asarray(Z, dtype=np.float64).ravel()
        nseg = len(self.L)
        best = np.full(X.shape, np.inf)
        dval = np.zeros(X.shape)
        nx_ = np.zeros(X.shape)
        ny_ = np.zeros(X.shape)
        for i in range(nseg):
            px, py = X - self.a[i, 0], Y - self.a[i, 1]
            t = px * self.u[i, 0] + py * self.u[i, 1]
            tc = t
            if i > 0:
                tc = np.maximum(tc, 0)
            if i < nseg - 1:
                tc = np.minimum(tc, self.L[i])
            ex, ey = px - tc * self.u[i, 0], py - tc * self.u[i, 1]
            dist = np.hypot(ex, ey)
            sel = dist < best
            best[sel] = dist[sel]
            dval[sel] = ((px * self.r[i, 0] + py * self.r[i, 1]) * self.side)[sel]
            tt = np.clip(t, 0, self.L[i])
            nx_[sel] = (self.a[i, 0] + tt * self.u[i, 0])[sel]
            ny_[sel] = (self.a[i, 1] + tt * self.u[i, 1])[sel]
        zt = self.topo(nx_, ny_)
        return dval * self.sd - (zt - Z) * self.cd


# ----------------------------------------------------------------------------- RBF field
class RbfField(object):
    def __init__(self, ox, oy, oz, L, cv, alpha, cg, beta, c):
        self.ox, self.oy, self.oz, self.L = ox, oy, oz, L
        self.cv, self.alpha, self.cg, self.beta, self.c = cv, alpha, cg, beta, c

    def __call__(self, X, Y, Z, chunk=4000):
        X = (np.asarray(X, dtype=np.float64).ravel() - self.ox) / self.L
        Y = (np.asarray(Y, dtype=np.float64).ravel() - self.oy) / self.L
        Z = (np.asarray(Z, dtype=np.float64).ravel() - self.oz) / self.L
        out = np.empty(X.shape)
        for s in range(0, len(X), chunk):
            x, y, z = X[s:s + chunk], Y[s:s + chunk], Z[s:s + chunk]
            f = self.c[0] + self.c[1] * x + self.c[2] * y + self.c[3] * z
            if len(self.alpha):
                dx = x[:, None] - self.cv[None, :, 0]
                dy = y[:, None] - self.cv[None, :, 1]
                dz = z[:, None] - self.cv[None, :, 2]
                r = np.sqrt(dx * dx + dy * dy + dz * dz)
                f = f + (r * r * r) @ self.alpha
            if len(self.beta):
                dx = x[:, None] - self.cg[None, :, 0]
                dy = y[:, None] - self.cg[None, :, 1]
                dz = z[:, None] - self.cg[None, :, 2]
                r = np.sqrt(dx * dx + dy * dy + dz * dz)
                f = f - 3.0 * (r * (dx * self.beta[None, :, 0] + dy * self.beta[None, :, 1]
                                    + dz * self.beta[None, :, 2])).sum(axis=1)
            out[s:s + chunk] = f
        return out * self.L


def solve_field(pts, grads, faults, n_iface, ref, fixed_levels, center, L):
    """Port of geomap-workbench solveField (cubic RBF co-kriging with fault drifts).

    pts: (n, 4) x, y, z, interface index;  grads: (m, 6) x, y, z, nx, ny, nz
    Returns (RbfField, levels, fault_drifts{name: d}).
    """
    ox, oy, oz = center
    P = np.zeros((0, 4)) if len(pts) == 0 else np.array(pts, dtype=np.float64)
    G = np.zeros((0, 6)) if len(grads) == 0 else np.array(grads, dtype=np.float64)
    Pn = np.column_stack([(P[:, 0] - ox) / L, (P[:, 1] - oy) / L, (P[:, 2] - oz) / L]) if len(P) else np.zeros((0, 3))
    Gn = np.column_stack([(G[:, 0] - ox) / L, (G[:, 1] - oy) / L, (G[:, 2] - oz) / L]) if len(G) else np.zeros((0, 3))
    kk = P[:, 3].astype(int) if len(P) else np.zeros(0, dtype=int)

    ifaces = []
    if fixed_levels is None:
        ifaces = [k for k in range(n_iface) if k != ref and np.any(kk == k)]
    used_faults, fl = [], []
    for f in faults:
        ind = (f.value(P[:, 0], P[:, 1], P[:, 2]) > 0).astype(np.float64) if len(P) else np.zeros(0)
        s = ind.sum()
        if 0 < s < len(P):
            used_faults.append(f)
            fl.append(ind)
    nv, ng = len(Pn), len(Gn)
    npoly = 4 + len(used_faults) + len(ifaces)
    N = nv + 3 * ng + npoly
    A = np.zeros((N, N))
    b = np.zeros(N)
    c = nv + 3 * ng
    if nv:
        d = Pn[:, None, :] - Pn[None, :, :]
        r = np.sqrt((d * d).sum(axis=2))
        A[:nv, :nv] = r ** 3 + np.eye(nv) * NUG
    if nv and ng:
        d = Pn[:, None, :] - Gn[None, :, :]
        r = np.sqrt((d * d).sum(axis=2))
        blk = (-3.0 * r[:, :, None] * d).reshape(nv, 3 * ng)
        A[:nv, nv:nv + 3 * ng] = blk
        A[nv:nv + 3 * ng, :nv] = blk.T
    if ng:
        d = Gn[None, :, :] - Gn[:, None, :]  # [g, h] = G_h - G_g
        r = np.sqrt((d * d).sum(axis=2))
        with np.errstate(divide="ignore", invalid="ignore"):
            outer = np.where(r[:, :, None, None] > 1e-12,
                             d[:, :, :, None] * d[:, :, None, :] / r[:, :, None, None], 0.0)
        eye = np.eye(3)[None, None, :, :] * r[:, :, None, None]
        blk = -3.0 * (eye + outer)  # [g, h, a, c]
        A[nv:nv + 3 * ng, nv:nv + 3 * ng] = blk.transpose(0, 2, 1, 3).reshape(3 * ng, 3 * ng)
        A[nv:nv + 3 * ng, nv:nv + 3 * ng] += np.eye(3 * ng) * 1e-9
        for a in range(3):
            rows = nv + 3 * np.arange(ng) + a
            A[rows, c + 1 + a] = 1.0
            A[c + 1 + a, rows] = 1.0
            b[rows] = G[:, 3 + a]
    if nv:
        A[:nv, c] = A[c, :nv] = 1.0
        for a in range(3):
            A[:nv, c + 1 + a] = A[c + 1 + a, :nv] = Pn[:, a]
        for k, ind in enumerate(fl):
            A[:nv, c + 4 + k] = A[c + 4 + k, :nv] = ind
        for q, k in enumerate(ifaces):
            col = np.where(kk == k, -1.0, 0.0)
            A[:nv, c + 4 + len(fl) + q] = A[c + 4 + len(fl) + q, :nv] = col
        if fixed_levels is not None:
            b[:nv] = np.array([fixed_levels[k] for k in kk]) / L
    try:
        x = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        x = np.linalg.lstsq(A, b, rcond=None)[0]
    levels = list(fixed_levels) if fixed_levels is not None else [None] * n_iface
    if fixed_levels is None:
        levels[ref] = 0.0
    for q, k in enumerate(ifaces):
        levels[k] = float(x[c + 4 + len(fl) + q] * L)
    field = RbfField(ox, oy, oz, L, Pn, x[:nv], Gn, x[nv:nv + 3 * ng].reshape(ng, 3), x[c:c + 4])
    drifts = {f.name: float(x[c + 4 + k] * L) for k, f in enumerate(used_faults)}
    return field, levels, drifts


# ----------------------------------------------------------------------------- series model
class Series(object):
    def __init__(self, sid, units, is_base):
        self.sid = sid
        self.units = units  # old -> young (indices into model.units)
        self.is_base = is_base
        self.levels = []
        self.field = None
        self.grid = None
        self.drifts = []  # (Fault, d)


class GeoModel(object):
    def __init__(self, units, topo, extent, zbase, faults=None, intrusions=None, log=None):
        """units: list[Unit]; extent: (x0, y0, x1, y1); intrusions: {unit index: [rings]}"""
        self.units = units
        self.topo = topo
        self.extent = extent
        self.zbase = float(zbase)
        self.faults = faults or []
        self.intrusions = intrusions or {}
        self.log = log or (lambda m: None)
        self.warnings = []
        sids = sorted({u.series for u in units if u.kind != "ign"})
        self.series = []
        for i, sid in enumerate(sids):
            idx = sorted([k for k, u in enumerate(units) if u.series == sid and u.kind != "ign"],
                         key=lambda k: (units[k].order, units[k].code))
            self.series.append(Series(sid, idx, i == 0))

    def _warn(self, msg):
        self.warnings.append(msg)
        self.log(msg)

    # -- interface keys -------------------------------------------------------------
    def iface_keys(self, S):
        keys = []
        if not S.is_base:
            keys.append((S.sid, "base"))
        for a, b in zip(S.units[:-1], S.units[1:]):
            keys.append((S.sid, a, b))
        return keys

    def contact_key(self, ua, ub):
        """Interface key of a contact between units ua and ub (indices), or None."""
        A, B = self.units[ua], self.units[ub]
        if A.kind == "ign" or B.kind == "ign" or ua == ub:
            return None
        if A.series != B.series:
            return (max(A.series, B.series), "base")
        S = self._series_of(A.series)
        ia, ib = S.units.index(ua), S.units.index(ub)
        if abs(ia - ib) != 1:
            return None
        lo, hi = (ua, ub) if ia < ib else (ub, ua)
        return (S.sid, lo, hi)

    def _series_of(self, sid):
        for S in self.series:
            if S.sid == sid:
                return S
        return None

    # -- build -----------------------------------------------------------------------------
    def build(self, contacts, gradients, use_thickness=False, max_points=450, grid_n=60):
        """contacts: list of (x, y, z, ua, ub); gradients: list of (x, y, z, nx, ny, nz, unit index or None)."""
        x0, y0, x1, y1 = self.extent
        W, H = x1 - x0, y1 - y0
        L = max(W, H)
        zc = (self.topo.min + self.topo.max) / 2.0
        center = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zc)
        by_key = {}
        skipped = 0
        for x, y, z, ua, ub in contacts:
            k = self.contact_key(ua, ub)
            if k is None:
                skipped += 1
                continue
            by_key.setdefault(k, []).append((x, y, z))
        if skipped:
            self._warn("Contacts between non-adjacent units ignored: %d" % skipped)

        for S in self.series:
            keys = self.iface_keys(S)
            pts = []
            for k, key in enumerate(keys):
                for x, y, z in by_key.get(key, []):
                    pts.append((x, y, z, k))
            if len(pts) > max_points:
                step = len(pts) / float(max_points)
                pts = [pts[int(i * step)] for i in range(max_points)]
            grads = [g[:6] for g in gradients
                     if g[6] is not None and self.units[g[6]].series == S.sid and self.units[g[6]].kind != "ign"]
            if not grads:
                for k in range(len(keys)):
                    q = np.array([p[:3] for p in pts if p[3] == k])
                    if len(q) < 3:
                        continue
                    M = np.column_stack([q[:, 0], q[:, 1], np.ones(len(q))])
                    try:
                        a, b2, _ = np.linalg.lstsq(M, q[:, 2], rcond=None)[0]
                    except np.linalg.LinAlgError:
                        continue
                    n = np.array([-a, -b2, 1.0])
                    n /= np.linalg.norm(n)
                    grads.append((q[:, 0].mean(), q[:, 1].mean(), q[:, 2].mean(), n[0], n[1], n[2]))
                if grads:
                    self._warn("Series %s: no attitude data, planes fitted to the contacts" % S.sid)
            if not pts and not grads:
                self._warn("Series %s: no contacts and no attitudes, skipped" % S.sid)
                continue
            if not grads:
                raise ValueError("Series %s needs at least one attitude or three contact points" % S.sid)
            ref = next((k for k in range(len(keys)) if any(p[3] == k for p in pts)), 0)
            fixed = None
            if use_thickness:
                fixed = [0.0]
                for k in range(1, len(keys)):
                    below = self.units[keys[k][1]] if keys[k][1] != "base" else None
                    fixed.append(fixed[-1] + ((below.thick if below and below.thick else None) or 50.0))
            try:
                field, levels, drifts = solve_field(pts, grads, self.faults, len(keys), ref, fixed, center, L)
            except Exception:
                field, levels, drifts = solve_field(pts, grads, [], len(keys), ref, fixed, center, L)
                self._warn("Series %s: solved without faults" % S.sid)
            self._fill_levels(S, keys, levels)
            S.levels = ([-1e12] + levels) if S.is_base else levels
            S.field = field
            S.drifts = [(f, drifts[f.name]) for f in self.faults if abs(drifts.get(f.name, 0.0)) > 1e-6]
            self.log("Series %s: %d contact points, %d attitudes, levels %s" % (
                S.sid, len(pts), len(grads), ", ".join("%.1f" % v for v in levels)))
            self._cache_grid(S, grid_n)

    def _fill_levels(self, S, keys, L):
        def thick(k):
            below = keys[k][1]
            u = self.units[below] if below != "base" else None
            return (u.thick if u is not None and u.thick else None) or 50.0

        for k in range(len(L)):
            if L[k] is not None:
                continue
            j = k - 1
            while j >= 0 and L[j] is None:
                j -= 1
            if j >= 0:
                acc = L[j]
                for q in range(j + 1, k + 1):
                    acc += thick(q)
                L[k] = acc
            else:
                j2 = k + 1
                while j2 < len(L) and L[j2] is None:
                    j2 += 1
                acc = L[j2] if j2 < len(L) else 0.0
                for q in range(j2, k, -1):
                    acc -= thick(min(q, len(L) - 1))
                L[k] = acc
        for k in range(1, len(L)):
            if L[k] <= L[k - 1]:
                self._warn("Series %s: interface %d is not above the one below it (check contacts / attitudes)"
                           % (S.sid, k))

    def _cache_grid(self, S, n):
        x0, y0, x1, y1 = self.extent
        W, H = x1 - x0, y1 - y0
        sp = max(W, H) / float(n)
        nx, ny = int(round(W / sp)) + 1, int(round(H / sp)) + 1
        zlo, zhi = self.zbase - sp, self.topo.max + sp
        nz = int(max(12, min(48, round((zhi - zlo) / sp) + 1)))
        xs = np.linspace(x0, x1, nx)
        ys = np.linspace(y0, y1, ny)
        zs = np.linspace(zlo, zhi, nz)
        Z, Y, X = np.meshgrid(zs, ys, xs, indexing="ij")
        vals = S.field(X.ravel(), Y.ravel(), Z.ravel()).reshape(nz, ny, nx)
        S.grid = (vals, x0, y0, zlo, (x1 - x0) / (nx - 1), (y1 - y0) / (ny - 1), (zhi - zlo) / (nz - 1))

    # -- evaluation ------------------------------------------------------------------------
    def field_value(self, S, X, Y, Z):
        vals, gx, gy, gz, dx, dy, dz = S.grid
        nz, ny, nx = vals.shape
        X = np.asarray(X, dtype=np.float64).ravel()
        Y = np.asarray(Y, dtype=np.float64).ravel()
        Z = np.asarray(Z, dtype=np.float64).ravel()
        fx = np.clip((X - gx) / dx, 0, nx - 1.000001)
        fy = np.clip((Y - gy) / dy, 0, ny - 1.000001)
        fz = np.clip((Z - gz) / dz, 0, nz - 1.000001)
        i, j, k = fx.astype(int), fy.astype(int), fz.astype(int)
        u, v, w = fx - i, fy - j, fz - k
        f = 0.0
        for di in (0, 1):
            for dj in (0, 1):
                for dk in (0, 1):
                    wt = (u if di else 1 - u) * (v if dj else 1 - v) * (w if dk else 1 - w)
                    f = f + wt * vals[k + dk, j + dj, i + di]
        outside = (Z < gz) | (Z > gz + dz * (nz - 1))
        if outside.any():
            f = np.array(f)
            f[outside] = S.field(X[outside], Y[outside], Z[outside])
        for flt, d in S.drifts:
            f = f + np.where(flt.value(X, Y, Z) > 0, d, 0.0)
        return f

    def unit_index(self, X, Y, Z, clip_topo=True):
        """Unit index at points; AIR above the ground, NONE where undetermined."""
        X = np.asarray(X, dtype=np.float64).ravel()
        Y = np.asarray(Y, dtype=np.float64).ravel()
        Z = np.asarray(Z, dtype=np.float64).ravel()
        out = np.full(X.shape, NONE, dtype=np.int32)
        todo = np.ones(X.shape, dtype=bool)
        for ui, rings in self.intrusions.items():
            m = todo & points_in_rings(X, Y, rings)
            out[m] = ui
            todo &= ~m
        for S in reversed(self.series):
            if S.field is None or not todo.any():
                continue
            idx = np.where(todo)[0]
            f = self.field_value(S, X[idx], Y[idx], Z[idx])
            lv = np.array(S.levels)
            inside = np.ones(len(idx), dtype=bool) if S.is_base else f >= lv[0]
            pos = np.clip(np.searchsorted(lv, f, side="right") - 1, 0, len(S.units) - 1)
            sel = idx[inside]
            out[sel] = np.array(S.units)[pos[inside]]
            todo[sel] = False
        if clip_topo:
            out[Z > self.topo(X, Y)] = AIR
        return out

    def unit_inside(self, ui, X, Y, Z):
        """Signed 'inside' function of unit ui (> 0 inside, ~metres), for isosurfaces."""
        X = np.asarray(X, dtype=np.float64).ravel()
        Y = np.asarray(Y, dtype=np.float64).ravel()
        Z = np.asarray(Z, dtype=np.float64).ravel()
        u = self.units[ui]
        big = 1e6
        if u.kind == "ign":
            g = np.where(points_in_rings(X, Y, self.intrusions.get(ui, [])), big, -big)
        else:
            S = self._series_of(u.series)
            if S is None or S.field is None:
                return np.full(X.shape, -big)
            f = self.field_value(S, X, Y, Z)
            k = S.units.index(ui)
            lo = S.levels[k]
            hi = S.levels[k + 1] if k + 1 < len(S.levels) else big
            g = np.minimum(f - lo, hi - f)
            for T in self.series:  # younger series cut this one
                if T.sid > S.sid and T.field is not None:
                    g = np.minimum(g, T.levels[0] - self.field_value(T, X, Y, Z))
            for uj, rings in self.intrusions.items():
                g = np.where(points_in_rings(X, Y, rings), -big, g)
        return g


def points_in_rings(X, Y, rings, chunk=20000):
    """Even-odd point-in-polygon for a list of rings [(n, 2) arrays]."""
    inside = np.zeros(len(X), dtype=bool)
    for ring in rings:
        r = np.asarray(ring, dtype=np.float64)
        if len(r) < 3:
            continue
        xa, ya = r[:, 0], r[:, 1]
        xb, yb = np.roll(xa, -1), np.roll(ya, -1)
        for s in range(0, len(X), chunk):
            x = X[s:s + chunk, None]
            y = Y[s:s + chunk, None]
            cond = (ya[None, :] > y) != (yb[None, :] > y)
            with np.errstate(divide="ignore", invalid="ignore"):
                xc = xa[None, :] + (y - ya[None, :]) * (xb - xa)[None, :] / (yb - ya)[None, :]
            cross = cond & (x < xc)
            inside[s:s + chunk] ^= (cross.sum(axis=1) % 2 == 1)
    return inside
