# -*- coding: utf-8 -*-
"""Stratigraphic boundary tracing by the structure-contour principle.

A boundary observed at an outcrop point P0 (x0, y0, z0) with dip d and dip
direction a is a plane

    z_s(x, y) = z0 - tan(d) * [ (x - x0) sin(a) + (y - y0) cos(a) ]

The boundary crops out wherever the plane meets the ground, i.e. on the
zero line of

    F(x, y) = DEM(x, y) - z_s(x, y)

F > 0 : the ground is above the boundary (upper / younger unit at surface)
F < 0 : the ground is below the boundary (lower / older unit at surface)

Several outcrop points of the *same* boundary (same upper & lower unit code)
in the *same* fault block are combined with an inverse-distance weighted
blend of their planes (Shepard blending of linear nodal functions). The
blended surface passes exactly through every point and keeps each point's
own attitude there, so a single zero line runs through all points and joins
them end to end, and it may bend around fold hinges.

The zero line is extracted with GDAL's contour generator, clipped to the
fault block (so it stops on the fault) and split at any fault that does not
fully cut a block.
"""
import math

import numpy as np
from osgeo import gdal, ogr

from qgis.core import QgsGeometry, QgsPointXY, QgsRectangle, QgsSpatialIndex, QgsFeature

from ..compat import GEOM_LINE
from .geom_utils import line_parts, polygon_parts, polygonize_lines, polyline_xy, buffered_rect

# NOTE: gdal.UseExceptions() is deliberately not called: it is process-wide
# and would change GDAL behaviour for QGIS and every other plugin.

NODATA = -1.0e30

METHOD_BLEND = 0
METHOD_INDIVIDUAL = 1


class OutcropPoint(object):
    __slots__ = ("fid", "x", "y", "z", "dip", "dip_dir", "upper", "lower", "overturned", "block")

    def __init__(self, fid, x, y, dip, dip_dir, upper, lower, overturned=False, z=None):
        self.fid = fid
        self.x = float(x)
        self.y = float(y)
        self.dip = float(dip)
        self.dip_dir = float(dip_dir) % 360.0
        self.upper = upper
        self.lower = lower
        self.overturned = bool(overturned)
        self.z = z
        self.block = -1

    def gradient(self):
        """(dz/dx, dz/dy) of the bedding plane."""
        t = math.tan(math.radians(min(max(self.dip, 0.0), 89.9)))
        a = math.radians(self.dip_dir)
        return -t * math.sin(a), -t * math.cos(a)


class TraceResult(object):
    def __init__(self, geom, upper, lower, block, points, upper_side, method):
        self.geom = geom
        self.upper = upper
        self.lower = lower
        self.block = block
        self.points = points
        self.upper_side = upper_side
        self.method = method
        self.joined = False


class DemGrid(object):
    """Window reader / bilinear sampler for a single raster band."""

    def __init__(self, path, band=1):
        self.ds = gdal.Open(path)
        if self.ds is None:
            raise IOError("Cannot open DEM: %s" % path)
        self.band = self.ds.GetRasterBand(band)
        self.gt = self.ds.GetGeoTransform()
        if abs(self.gt[2]) > 1e-12 or abs(self.gt[4]) > 1e-12:
            raise ValueError("Rotated rasters are not supported")
        self.nx = self.ds.RasterXSize
        self.ny = self.ds.RasterYSize
        self.nodata = self.band.GetNoDataValue()
        self.dx = abs(self.gt[1])
        self.dy = abs(self.gt[5])
        self.cell = max(self.dx, self.dy)

    @property
    def extent(self):
        x0, y0 = self.gt[0], self.gt[3]
        x1 = x0 + self.gt[1] * self.nx
        y1 = y0 + self.gt[5] * self.ny
        return QgsRectangle(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def _col_row(self, x, y):
        return (x - self.gt[0]) / self.gt[1], (y - self.gt[3]) / self.gt[5]

    def read_window(self, rect):
        """Return (array[float64 with NaN], window geotransform) covering *rect*."""
        c0, r0 = self._col_row(rect.xMinimum(), rect.yMaximum())
        c1, r1 = self._col_row(rect.xMaximum(), rect.yMinimum())
        cmin, cmax = sorted((c0, c1))
        rmin, rmax = sorted((r0, r1))
        xoff = max(0, int(math.floor(cmin)) - 1)
        yoff = max(0, int(math.floor(rmin)) - 1)
        xend = min(self.nx, int(math.ceil(cmax)) + 1)
        yend = min(self.ny, int(math.ceil(rmax)) + 1)
        if xend - xoff < 2 or yend - yoff < 2:
            return None, None
        arr = self.band.ReadAsArray(xoff, yoff, xend - xoff, yend - yoff).astype(np.float64)
        if self.nodata is not None:
            arr[arr == self.nodata] = np.nan
        gt = (
            self.gt[0] + xoff * self.gt[1],
            self.gt[1],
            0.0,
            self.gt[3] + yoff * self.gt[5],
            0.0,
            self.gt[5],
        )
        return arr, gt

    def sample(self, x, y):
        """Bilinear elevation at (x, y); None outside / on nodata."""
        rect = QgsRectangle(x - 2 * self.dx, y - 2 * self.dy, x + 2 * self.dx, y + 2 * self.dy)
        arr, gt = self.read_window(rect)
        if arr is None:
            return None
        v = bilinear(arr, gt, x, y)
        return None if v is None or not np.isfinite(v) else float(v)


def bilinear(arr, gt, x, y):
    """Bilinear interpolation on cell centres; None outside."""
    fc = (x - gt[0]) / gt[1] - 0.5
    fr = (y - gt[3]) / gt[5] - 0.5
    ny, nx = arr.shape
    if fc < 0 or fr < 0 or fc > nx - 1 or fr > ny - 1:
        return None
    c0 = min(int(math.floor(fc)), nx - 2)
    r0 = min(int(math.floor(fr)), ny - 2)
    tc, tr = fc - c0, fr - r0
    v = (
        arr[r0, c0] * (1 - tc) * (1 - tr)
        + arr[r0, c0 + 1] * tc * (1 - tr)
        + arr[r0 + 1, c0] * (1 - tc) * tr
        + arr[r0 + 1, c0 + 1] * tc * tr
    )
    return float(v)


def blended_surface(X, Y, pts, power=2.0):
    """Inverse-distance weighted blend of the bedding planes of *pts*.

    X, Y may be numpy arrays or scalars. A single point gives its plane.
    """
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    if len(pts) == 1:
        p = pts[0]
        gx, gy = p.gradient()
        return p.z + gx * (X - p.x) + gy * (Y - p.y)
    num = np.zeros(np.broadcast(X, Y).shape)
    den = np.zeros_like(num)
    for p in pts:
        gx, gy = p.gradient()
        plane = p.z + gx * (X - p.x) + gy * (Y - p.y)
        d2 = (X - p.x) ** 2 + (Y - p.y) ** 2
        w = 1.0 / np.power(d2 + 1e-6, power / 2.0)
        num += w * plane
        den += w
    return num / den


def _memory_vector_datasource():
    """In-memory OGR datasource: 'Memory' driver before GDAL 3.11, vector-capable 'MEM' after."""
    for name in ("MEM", "Memory"):
        drv = ogr.GetDriverByName(name)
        if drv is None:
            continue
        try:
            if drv.GetMetadataItem("DCAP_VECTOR") != "YES":
                continue
        except Exception:
            pass
        try:
            ds = drv.CreateDataSource("zero")
        except Exception:
            ds = None
        if ds is not None:
            return ds
    raise RuntimeError("No in-memory OGR driver available")


def zero_contours(field, gt):
    """Lines where *field* == 0 (field: 2-D array, NaN = nodata)."""
    ny, nx = field.shape
    arr = np.where(np.isfinite(field), field, NODATA)
    mem = gdal.GetDriverByName("MEM").Create("", nx, ny, 1, gdal.GDT_Float64)
    mem.SetGeoTransform(gt)
    band = mem.GetRasterBand(1)
    band.SetNoDataValue(NODATA)
    band.WriteArray(arr)
    vds = _memory_vector_datasource()
    lyr = vds.CreateLayer("c", geom_type=ogr.wkbLineString)
    lyr.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))
    lyr.CreateField(ogr.FieldDefn("F", ogr.OFTReal))
    err = gdal.ContourGenerateEx(
        band, lyr, options=["FIXED_LEVELS=0", "ID_FIELD=0", "ELEV_FIELD=1", "NODATA=%g" % NODATA]
    )
    if err not in (0, None):
        raise RuntimeError("GDAL contour generation failed (%s)" % err)
    out = []
    for feat in lyr:
        og = feat.GetGeometryRef()
        if og is None or og.GetPointCount() < 2:
            continue
        g = QgsGeometry()
        g.fromWkb(bytes(og.ExportToIsoWkb()))
        out.append(g)
    return out


def fault_blocks(extent, fault_geoms, snap_tol):
    """Split *extent* into fault blocks. Faults that do not cut through are dangles."""
    blocks = polygonize_lines(fault_geoms, extent, snap_tol)
    if not blocks:
        blocks = [QgsGeometry.fromRect(extent)]
    return blocks


def _upper_side(line, pts, power, arr, gt, offset):
    """'L' / 'R' : side of the line on which the upper unit crops out."""
    vs = polyline_xy(line)
    if len(vs) < 2:
        return ""
    step = max(1, (len(vs) - 1) // 40)
    votes = 0
    for i in range(0, len(vs) - 1, step):
        a, b = vs[i], vs[i + 1]
        dx, dy = b.x() - a.x(), b.y() - a.y()
        n = math.hypot(dx, dy)
        if n == 0:
            continue
        mx, my = (a.x() + b.x()) / 2.0, (a.y() + b.y()) / 2.0
        nx_, ny_ = -dy / n, dx / n  # left normal
        lx, ly = mx + nx_ * offset, my + ny_ * offset
        rx, ry = mx - nx_ * offset, my - ny_ * offset
        zl, zr = bilinear(arr, gt, lx, ly), bilinear(arr, gt, rx, ry)
        if zl is None or zr is None or not (np.isfinite(zl) and np.isfinite(zr)):
            continue
        fl = zl - float(blended_surface(lx, ly, pts, power))
        fr = zr - float(blended_surface(rx, ry, pts, power))
        if fl > fr:
            votes += 1
        elif fl < fr:
            votes -= 1
    if votes == 0:
        return ""
    left_upper = votes > 0
    # overturned beds: the stratigraphically upper unit lies *below* the surface
    if sum(1 for p in pts if p.overturned) * 2 > len(pts):
        left_upper = not left_upper
    return "L" if left_upper else "R"


class BoundaryTracer(object):
    """Trace predicted boundary lines from outcrop points and a DEM."""

    def __init__(
        self,
        dem,
        faults=None,
        method=METHOD_BLEND,
        power=4.0,
        max_distance=0.0,
        connect_gap=0.0,
        keep_all_branches=False,
        min_length=0.0,
        snap_tol=None,
        feedback=None,
    ):
        self.dem = dem
        self.faults = [g for g in (faults or []) if g is not None and not g.isEmpty()]
        self.method = method
        self.power = power
        self.connect_gap = connect_gap
        self.max_distance = max_distance
        self.keep_all = keep_all_branches
        self.min_length = min_length
        self.snap_tol = dem.cell * 0.5 if snap_tol is None else snap_tol
        self.feedback = feedback
        self.messages = []

    # -- helpers ---------------------------------------------------------------------
    def _log(self, msg):
        self.messages.append(msg)
        if self.feedback is not None:
            self.feedback.pushInfo(msg)

    def _cancelled(self):
        return self.feedback is not None and self.feedback.isCanceled()

    def assign_blocks(self, points, blocks):
        idx = QgsSpatialIndex()
        for i, b in enumerate(blocks):
            f = QgsFeature(i)
            f.setGeometry(b)
            idx.addFeature(f)
        for p in points:
            g = QgsGeometry.fromPointXY(QgsPointXY(p.x, p.y))
            p.block = -1
            for i in idx.intersects(g.boundingBox()):
                if blocks[i].contains(g):
                    p.block = i
                    break
            if p.block < 0:
                cand = idx.nearestNeighbor(QgsPointXY(p.x, p.y), 1)
                p.block = cand[0] if cand else 0

    def groups(self, points):
        groups = {}
        for p in points:
            if self.method == METHOD_INDIVIDUAL:
                key = (p.upper, p.lower, p.block, p.fid)
            else:
                key = (p.upper, p.lower, p.block)
            groups.setdefault(key, []).append(p)
        return groups

    # -- main --------------------------------------------------------------------------
    def run(self, points):
        extent = self.dem.extent
        blocks = fault_blocks(extent, self.faults, self.snap_tol)
        self._log("Fault blocks: %d" % len(blocks))

        valid = []
        for p in points:
            if p.z is None:
                p.z = self.dem.sample(p.x, p.y)
            if p.z is None:
                self._log("Point %s skipped: outside DEM / nodata" % p.fid)
                continue
            valid.append(p)
        self.assign_blocks(valid, blocks)

        fault_union = QgsGeometry.unaryUnion(self.faults) if self.faults else None
        tol = 1.5 * self.dem.cell
        results = []
        groups = self.groups(valid)
        for gi, (key, pts) in enumerate(sorted(groups.items(), key=lambda kv: [str(k) for k in kv[0]])):
            if self._cancelled():
                break
            if self.feedback is not None:
                self.feedback.setProgress(100.0 * gi / max(1, len(groups)))
            block = blocks[key[2]]
            results.extend(self._trace_group(pts, key, block, fault_union, tol))
        return results

    def _trace_group(self, pts, key, block, fault_union, tol):
        upper, lower, block_id = key[0], key[1], key[2]
        win = block.boundingBox()
        if self.max_distance > 0:
            pr = QgsRectangle(pts[0].x, pts[0].y, pts[0].x, pts[0].y)
            for p in pts[1:]:
                pr.combineExtentWith(p.x, p.y)
            pr = buffered_rect(pr, self.max_distance)
            win = win.intersect(pr)
        win = buffered_rect(win, 2 * self.dem.cell)
        arr, gt = self.dem.read_window(win)
        if arr is None:
            return []
        ny, nx = arr.shape
        xs = gt[0] + (np.arange(nx) + 0.5) * gt[1]
        ys = gt[3] + (np.arange(ny) + 0.5) * gt[5]
        X, Y = np.meshgrid(xs, ys)
        field = arr - blended_surface(X, Y, pts, self.power)

        raw = zero_contours(field, gt)
        if not raw:
            self._log("No outcrop line found for %s/%s (block %d)" % (upper, lower, block_id))
            return []
        lines = QgsGeometry.unaryUnion(raw).mergeLines()
        lines = lines.intersection(block)
        if fault_union is not None:
            lines = lines.difference(fault_union)
        if self.max_distance > 0:
            reach = QgsGeometry.unaryUnion(
                [QgsGeometry.fromPointXY(QgsPointXY(p.x, p.y)).buffer(self.max_distance, 24) for p in pts]
            )
            lines = lines.intersection(reach)

        parts = line_parts(lines)
        # re-merge pieces split only by noding (not by faults)
        if len(parts) > 1:
            merged = QgsGeometry.unaryUnion(parts).mergeLines()
            if fault_union is not None:
                merged = merged.difference(fault_union)
            parts = line_parts(merged)

        out = []
        pgeoms = [(p, QgsGeometry.fromPointXY(QgsPointXY(p.x, p.y))) for p in pts]
        for part in parts:
            if part.length() <= max(self.min_length, 0.0):
                continue
            hit = [p for p, g in pgeoms if part.distance(g) <= tol]
            if not hit and not self.keep_all:
                continue
            side = _upper_side(part, pts, self.power, arr, gt, self.dem.cell)
            out.append(
                TraceResult(
                    part,
                    upper,
                    lower,
                    block_id,
                    hit,
                    side,
                    "individual" if self.method == METHOD_INDIVIDUAL else "blend",
                )
            )
        if not any(r.points for r in out):
            self._log("Traced line for %s/%s (block %d) does not pass its points" % (upper, lower, block_id))
        if self.connect_gap > 0 and len(out) > 1:
            out = self._join_pieces(out, block, fault_union, tol)
            for r in out:
                if not r.upper_side:
                    r.upper_side = _upper_side(r.geom, pts, self.power, arr, gt, self.dem.cell)
        return out

    def _join_pieces(self, pieces, block, fault_union, tol):
        """Join pieces of the same boundary end to end across gaps <= connect_gap.

        Ends lying on a fault or on the block edge are final and never joined.
        """
        barrier = [block.convertToType(GEOM_LINE, True)]
        if fault_union is not None:
            barrier.append(fault_union)
        barrier = QgsGeometry.unaryUnion([b for b in barrier if b is not None and not b.isEmpty()])

        def free_ends(geom):
            vs = polyline_xy(geom)
            if len(vs) < 2 or vs[0] == vs[-1]:
                return []
            ends = []
            for idx, v in ((0, vs[0]), (1, vs[-1])):
                if barrier.isEmpty() or QgsGeometry.fromPointXY(v).distance(barrier) > tol:
                    ends.append((idx, QgsPointXY(v)))
            return ends

        while True:
            best = None
            for i in range(len(pieces)):
                for j in range(i + 1, len(pieces)):
                    for ei, pi in free_ends(pieces[i].geom):
                        for ej, pj in free_ends(pieces[j].geom):
                            d = math.hypot(pi.x() - pj.x(), pi.y() - pj.y())
                            if d <= self.connect_gap and (best is None or d < best[0]):
                                best = (d, i, ei, j, ej)
            if best is None:
                return pieces
            _, i, ei, j, ej = best
            a = list(polyline_xy(pieces[i].geom))
            b = list(polyline_xy(pieces[j].geom))
            if ei == 0:
                a.reverse()
            if ej == 1:
                b.reverse()
            joined = QgsGeometry.fromPolylineXY(a + b)
            pi_, pj_ = pieces[i], pieces[j]
            merged = TraceResult(
                joined,
                pi_.upper,
                pi_.lower,
                pi_.block,
                pi_.points + pj_.points,
                "",  # recomputed by the caller
                pi_.method,
            )
            merged.joined = True
            pieces = [p for k, p in enumerate(pieces) if k not in (i, j)] + [merged]
