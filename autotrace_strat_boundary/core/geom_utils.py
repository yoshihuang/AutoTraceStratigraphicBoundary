# -*- coding: utf-8 -*-
"""Small geometry helpers shared by the tracer and the geology builder."""
import math

from qgis.core import QgsGeometry, QgsPointXY, QgsRectangle

from ..compat import GEOM_LINE, GEOM_POLYGON


def single_parts(geom):
    """Return the single-part geometries of *geom* (empty list for empty)."""
    if geom is None or geom.isEmpty():
        return []
    if geom.isMultipart():  # multi-geometries and geometry collections
        return [g for g in geom.asGeometryCollection() if not g.isEmpty()]
    return [geom]


def line_parts(geom):
    return [g for g in single_parts(geom) if g.type() == GEOM_LINE]


def polygon_parts(geom):
    return [g for g in single_parts(geom) if g.type() == GEOM_POLYGON]


def polyline_xy(geom):
    """List of QgsPointXY of a single-part line."""
    if geom.isMultipart():
        lines = geom.asMultiPolyline()
        return lines[0] if lines else []
    return geom.asPolyline()


def extend_line(geom, dist):
    """Extend every part of a (multi)line at both ends by *dist* along its end segments."""
    out = []
    for part in line_parts(geom):
        pts = polyline_xy(part)
        if len(pts) < 2:
            continue
        pts = [QgsPointXY(p) for p in pts]

        def _ext(a, b):
            dx, dy = a.x() - b.x(), a.y() - b.y()
            n = math.hypot(dx, dy)
            if n == 0:
                return QgsPointXY(a)
            return QgsPointXY(a.x() + dx / n * dist, a.y() + dy / n * dist)

        closed = pts[0] == pts[-1]
        if not closed:
            pts = [_ext(pts[0], pts[1])] + pts + [_ext(pts[-1], pts[-2])]
        out.append(QgsGeometry.fromPolylineXY(pts))
    if not out:
        return QgsGeometry()
    return QgsGeometry.collectGeometry(out)


def snap_connectors(parts, snap_tol):
    """Short segments joining loose line ends to the nearest other line within *snap_tol*.

    Each connector overshoots its target slightly so that noding always
    produces an intersection.
    """
    from qgis.core import QgsFeature, QgsSpatialIndex

    index = QgsSpatialIndex()
    for i, g in enumerate(parts):
        f = QgsFeature(i)
        f.setGeometry(g)
        index.addFeature(f)
    out = []
    for k, part in enumerate(parts):
        vs = polyline_xy(part)
        if len(vs) < 2 or vs[0] == vs[-1]:
            continue
        for v in (vs[0], vs[-1]):
            pg = QgsGeometry.fromPointXY(QgsPointXY(v))
            best, best_d = None, None
            for j in index.intersects(buffered_rect(pg.boundingBox(), snap_tol)):
                if j == k:
                    continue
                d = parts[j].distance(pg)
                if d <= snap_tol and (best_d is None or d < best_d):
                    best, best_d = j, d
            if best is None or best_d == 0:
                continue
            target = parts[best].nearestPoint(pg).asPoint()
            dx, dy = target.x() - v.x(), target.y() - v.y()
            n = math.hypot(dx, dy)
            if n < 1e-9:
                continue  # already touching
            over = min(snap_tol * 0.05, n)
            end = QgsPointXY(target.x() + dx / n * over, target.y() + dy / n * over)
            out.append(QgsGeometry.fromPolylineXY([QgsPointXY(v), end]))
    return out


def rect_ring(rect):
    pts = [
        QgsPointXY(rect.xMinimum(), rect.yMinimum()),
        QgsPointXY(rect.xMaximum(), rect.yMinimum()),
        QgsPointXY(rect.xMaximum(), rect.yMaximum()),
        QgsPointXY(rect.xMinimum(), rect.yMaximum()),
        QgsPointXY(rect.xMinimum(), rect.yMinimum()),
    ]
    return QgsGeometry.fromPolylineXY(pts)


def polygonize_lines(line_geoms, extent_rect, snap_tol):
    """Node *line_geoms* together with the extent frame and polygonize.

    Line ends are extended by *snap_tol* so lines that stop a hair short of a
    fault / frame / other line still close their polygons. Overshoots become
    dangles, which polygonize ignores.
    """
    frame = rect_ring(extent_rect)
    parts = [frame]
    for g in line_geoms:
        if g is not None and not g.isEmpty():
            parts.extend(line_parts(g))
    work = list(parts)
    if snap_tol > 0:
        work = [frame] + [extend_line(g, snap_tol) for g in parts[1:]]
        work.extend(snap_connectors(parts, snap_tol))
    noded = QgsGeometry.unaryUnion([g for g in work if not g.isEmpty()])
    polys = QgsGeometry.polygonize([noded])
    extent_poly = QgsGeometry.fromRect(extent_rect)
    result = []
    for p in polygon_parts(polys):
        c = p.intersection(extent_poly)
        for q in polygon_parts(c):
            if q.area() > 0:
                result.append(q)
    return result


def buffered_rect(rect, d):
    return QgsRectangle(rect.xMinimum() - d, rect.yMinimum() - d, rect.xMaximum() + d, rect.yMaximum() + d)
