# -*- coding: utf-8 -*-
"""Isosurface extraction on a regular grid (marching tetrahedra, numpy only)."""
import numpy as np

# cube corners (i, j, k offsets) and the 6 tetrahedra sharing the diagonal 0-6
CORNERS = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                    (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)])
TETS = [(0, 5, 1, 6), (0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6)]


class Grid(object):
    """Regular grid: x0 + i*dx, y0 + j*dy, z0 + k*dz; arrays are indexed [k, j, i]."""

    def __init__(self, x0, y0, z0, dx, dy, dz, nx, ny, nz):
        self.x0, self.y0, self.z0 = x0, y0, z0
        self.dx, self.dy, self.dz = dx, dy, dz
        self.nx, self.ny, self.nz = nx, ny, nz

    def nodes(self):
        zs = self.z0 + np.arange(self.nz) * self.dz
        ys = self.y0 + np.arange(self.ny) * self.dy
        xs = self.x0 + np.arange(self.nx) * self.dx
        Z, Y, X = np.meshgrid(zs, ys, xs, indexing="ij")
        return X, Y, Z


def isosurface(grid, values, level=0.0):
    """Triangles of the surface values == level.

    values: (nz, ny, nx) array, NaN = no data (cells touching NaN are skipped).
    Triangles are oriented with normals pointing to the side where values < level.
    Returns (verts (n, 3), faces (m, 3)).
    """
    v = np.asarray(values, dtype=np.float64) - level
    nz, ny, nx = v.shape
    if min(nx, ny, nz) < 2:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
    corner_vals = np.stack([v[dk:nz - 1 + dk, dj:ny - 1 + dj, di:nx - 1 + di] for di, dj, dk in CORNERS], axis=-1)
    valid = ~np.isnan(corner_vals).any(axis=-1)
    pos = corner_vals > 0
    anyp, allp = pos.any(axis=-1), pos.all(axis=-1)
    sel = valid & anyp & ~allp
    kk, jj, ii = np.nonzero(sel)
    if len(kk) == 0:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
    cv = corner_vals[kk, jj, ii]  # (C, 8)
    cp = np.empty((len(kk), 8, 3))
    for c, (di, dj, dk) in enumerate(CORNERS):
        cp[:, c, 0] = grid.x0 + (ii + di) * grid.dx
        cp[:, c, 1] = grid.y0 + (jj + dj) * grid.dy
        cp[:, c, 2] = grid.z0 + (kk + dk) * grid.dz
    tris = []
    for tet in TETS:
        tv = cv[:, tet]  # (C, 4)
        tp = cp[:, tet]  # (C, 4, 3)
        inside = tv > 0
        cnt = inside.sum(axis=1)
        for n_in in (1, 2, 3):
            m = cnt == n_in
            if not m.any():
                continue
            vals, pts, ins = tv[m], tp[m], inside[m]
            # sort corners so the "odd" group comes first
            key = ins if n_in in (1, 2) else ~ins
            order = np.argsort(~key, axis=1, kind="stable")
            vals = np.take_along_axis(vals, order, axis=1)
            pts = np.take_along_axis(pts, order[:, :, None], axis=1)

            def edge(a, b):
                va, vb = vals[:, a], vals[:, b]
                t = (va / (va - vb))[:, None]
                return pts[:, a] + t * (pts[:, b] - pts[:, a])

            ins_sorted = np.take_along_axis(ins, order, axis=1)
            cin = (pts * ins_sorted[:, :, None]).sum(axis=1) / np.maximum(ins_sorted.sum(axis=1), 1)[:, None]
            cout = (pts * (~ins_sorted)[:, :, None]).sum(axis=1) / np.maximum((~ins_sorted).sum(axis=1), 1)[:, None]
            outward = cout - cin
            if n_in in (1, 3):
                t = np.stack([edge(0, 1), edge(0, 2), edge(0, 3)], axis=1)
                tris.append(_orient(t, outward))
            else:
                p02, p03, p13, p12 = edge(0, 2), edge(0, 3), edge(1, 3), edge(1, 2)
                tris.append(_orient(np.stack([p02, p03, p13], axis=1), outward))
                tris.append(_orient(np.stack([p02, p13, p12], axis=1), outward))
    T = np.concatenate(tris, axis=0)
    return weld(T, min(grid.dx, grid.dy, grid.dz) * 1e-4)


def _orient(t, outward):
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    flip = (n * outward).sum(axis=1) < 0
    t[flip] = t[flip][:, [0, 2, 1]]
    return t


def weld(T, tol):
    """(m, 3, 3) triangles -> unique verts + faces; drops degenerate triangles."""
    P = T.reshape(-1, 3)
    key = np.round(P / tol).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    verts = P[first]
    faces = inv.reshape(-1, 3)
    good = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    return verts, faces[good]


def grid_surface(xs, ys, Z, mask=None):
    """Triangulate a height grid Z[j, i] (NaN or mask False = hole)."""
    ny, nx = Z.shape
    X, Y = np.meshgrid(xs, ys)
    verts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    idx = np.arange(nx * ny).reshape(ny, nx)
    a, b = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel()
    c, d = idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    faces = np.concatenate([np.column_stack([a, b, c]), np.column_stack([a, c, d])])
    ok = ~np.isnan(verts[faces][:, :, 2]).any(axis=1)
    if mask is not None:
        mflat = mask.ravel()
        ok &= mflat[faces].all(axis=1)
    return verts, faces[ok]


def face_values(face_centroids_fn, verts, faces):
    cen = verts[faces].mean(axis=1)
    return face_centroids_fn(cen[:, 0], cen[:, 1], cen[:, 2])
