# -*- coding: utf-8 -*-
"""Turn QGIS layers into model inputs (contacts, attitudes, faults, DEM)."""
import math

import numpy as np
from osgeo import gdal

from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsSpatialIndex

from .geom_utils import line_parts, polygon_parts, polyline_xy
from .model3d import Topography


def read_topography(dem_path, band, extent, crs_wkt=None, max_cells=600):
    """DEM resampled to <= max_cells per side over *extent* (x0, y0, x1, y1), in crs_wkt."""
    x0, y0, x1, y1 = extent
    res = max(x1 - x0, y1 - y0) / float(max_cells)
    opts = dict(format="MEM", outputBounds=(x0, y0, x1, y1), xRes=res, yRes=res,
                resampleAlg="bilinear", dstNodata=-1e30)
    if crs_wkt:
        opts["dstSRS"] = crs_wkt
    src = gdal.Open(dem_path)
    if src is None:
        raise IOError("Cannot open DEM: %s" % dem_path)
    nd = src.GetRasterBand(band).GetNoDataValue()
    if nd is not None:
        opts["srcNodata"] = nd
    ds = gdal.Warp("", src, **opts)
    if ds is None:
        raise IOError("Cannot resample DEM: %s" % dem_path)
    arr = ds.GetRasterBand(band).ReadAsArray().astype(np.float64)
    arr[arr <= -1e29] = np.nan
    if nd is not None:
        arr[arr == nd] = np.nan
    return Topography(arr, ds.GetGeoTransform())


def sample_line(geom, step):
    """Points every *step* along all parts of a line geometry."""
    out = []
    for part in line_parts(geom):
        L = part.length()
        n = max(1, int(math.ceil(L / step)))
        for i in range(n + 1):
            p = part.interpolate(L * i / n).asPoint()
            out.append((p.x(), p.y()))
    return out


def contacts_from_geology(polys, faults, topo, step, fault_tol):
    """Interface points from shared edges of geology polygons.

    polys: list of (QgsGeometry, unit index). Edges along faults are dropped.
    Returns list of (x, y, z, ua, ub).
    """
    idx = QgsSpatialIndex()
    for i, (g, _) in enumerate(polys):
        f = QgsFeature(i)
        f.setGeometry(g)
        idx.addFeature(f)
    fault_zone = None
    if faults:
        fault_zone = QgsGeometry.unaryUnion(faults).buffer(fault_tol, 4)
    out = []
    seen = set()
    for i, (gi, ui) in enumerate(polys):
        for j in idx.intersects(gi.boundingBox()):
            if j <= i or (i, j) in seen:
                continue
            gj, uj = polys[j]
            if ui == uj:
                continue
            seen.add((i, j))
            shared = gi.intersection(gj)
            lines = [p for p in line_parts(shared)]
            if not lines:
                continue
            shared = QgsGeometry.unaryUnion(lines)
            if fault_zone is not None:
                shared = shared.difference(fault_zone)
            for x, y in sample_line(shared, step):
                out.append((x, y, float(topo(x, y)), ui, uj))
    return out


def attitude_normal(dip, dipdir, overturned=False):
    de, th = math.radians(float(dip)), math.radians(float(dipdir))
    n = (math.sin(de) * math.sin(th), math.sin(de) * math.cos(th), math.cos(de))
    return tuple(-v for v in n) if overturned else n


def unit_at(polys, index, x, y):
    g = QgsGeometry.fromPointXY(QgsPointXY(x, y))
    for i in index.intersects(g.boundingBox()):
        if polys[i][0].contains(g):
            return polys[i][1]
    return None


def polygon_index(polys):
    idx = QgsSpatialIndex()
    for i, (g, _) in enumerate(polys):
        f = QgsFeature(i)
        f.setGeometry(g)
        idx.addFeature(f)
    return idx


def rings_of(geom):
    rings = []
    for part in polygon_parts(geom):
        for ring in part.asPolygon():
            rings.append(np.array([(p.x(), p.y()) for p in ring]))
    return rings


def trace_xy(geom):
    pts = []
    for part in line_parts(geom):
        pts.append([(p.x(), p.y()) for p in polyline_xy(part)])
    return pts
