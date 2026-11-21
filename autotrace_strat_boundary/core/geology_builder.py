# -*- coding: utf-8 -*-
"""Build a geological map (unit polygons) from boundary lines and faults.

1. The boundary lines, the faults and the map frame are noded and
   polygonized (line ends are extended by a snapping tolerance so that lines
   stopping just short of a fault still close their polygons).
2. Every segment of every boundary line looks at the polygon on its left
   and on its right. With the ``upper_side`` attribute (L / R, written by the
   tracer) the polygon on that side gets the upper unit code, the other side
   the lower unit code. Votes are weighted by segment length.
3. Optional unit sample points (e.g. bedding points with a unit code) vote
   for the polygon that contains them, with overriding weight.
4. Polygons still unknown are filled by propagation across boundaries whose
   orientation is unknown: if one side is unit U and the line is U/D, the
   other side is D (and vice versa).
5. Polygons are dissolved per unit (optional).
"""
import math
from collections import defaultdict

from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsSpatialIndex

from .geom_utils import line_parts, polygonize_lines, polyline_xy, rect_ring

QA_OK = "ok"
QA_CONFLICT = "conflict"
QA_PROPAGATED = "propagated"
QA_UNASSIGNED = "unassigned"


class BoundaryLine(object):
    def __init__(self, geom, upper, lower, upper_side=""):
        self.geom = geom
        self.upper = upper
        self.lower = lower
        s = (upper_side or "").strip().upper()[:1]
        self.upper_side = s if s in ("L", "R") else ""


class GeologyPolygon(object):
    def __init__(self, geom, unit, qa):
        self.geom = geom
        self.unit = unit
        self.qa = qa


def stratigraphic_order(boundaries):
    """{unit: order} with 1 = oldest, from the upper/lower pairs (topological sort)."""
    above = defaultdict(set)  # lower -> {upper}
    units = set()
    for b in boundaries:
        if b.upper and b.lower and b.upper != b.lower:
            above[b.lower].add(b.upper)
            units.update((b.upper, b.lower))
    indeg = {u: 0 for u in units}
    for lo, ups in above.items():
        for u in ups:
            indeg[u] += 1
    order = {}
    level = sorted(u for u, d in indeg.items() if d == 0)
    n = 1
    while level:
        nxt = []
        for u in level:
            order[u] = n
            n += 1
            for v in sorted(above.get(u, ())):
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        level = sorted(nxt)
    for u in sorted(units):  # cycles: append in name order
        if u not in order:
            order[u] = n
            n += 1
    return order


class GeologyBuilder(object):
    def __init__(self, extent, snap_tol=1.0, min_area=0.0, feedback=None):
        self.extent = extent
        self.snap_tol = snap_tol
        self.min_area = min_area
        self.dangles = []
        self.feedback = feedback
        self.messages = []

    def _log(self, msg):
        self.messages.append(msg)
        if self.feedback is not None:
            self.feedback.pushInfo(msg)

    def find_dangles(self, boundaries, faults):
        """End points of boundary lines that touch no other linework within snap_tol."""
        items = []
        for b in boundaries:
            items.extend(line_parts(b.geom))
        others = items + [g for f in faults for g in line_parts(f)]
        others.append(rect_ring(self.extent))
        index = QgsSpatialIndex()
        for i, g in enumerate(others):
            f = QgsFeature(i)
            f.setGeometry(g)
            index.addFeature(f)
        dangles = []
        for k, part in enumerate(items):
            vs = polyline_xy(part)
            if len(vs) < 2 or vs[0] == vs[-1]:
                continue
            for v in (vs[0], vs[-1]):
                pg = QgsGeometry.fromPointXY(QgsPointXY(v))
                box = pg.buffer(self.snap_tol, 4).boundingBox()
                touched = any(
                    j != k and others[j].distance(pg) <= self.snap_tol for j in index.intersects(box)
                )
                if not touched:
                    dangles.append(QgsPointXY(v))
        return dangles

    def build(self, boundaries, faults, unit_points=None, dissolve=True):
        self.dangles = self.find_dangles(boundaries, faults)
        if self.dangles:
            self._log("Dangling boundary ends (not closed within snap tolerance): %d" % len(self.dangles))
        lines = [b.geom for b in boundaries] + list(faults)
        polys = polygonize_lines(lines, self.extent, self.snap_tol)
        self._log("Polygons from linework: %d" % len(polys))
        if not polys:
            return []

        index = QgsSpatialIndex()
        for i, p in enumerate(polys):
            f = QgsFeature(i)
            f.setGeometry(p)
            index.addFeature(f)

        def locate(x, y):
            g = QgsGeometry.fromPointXY(QgsPointXY(x, y))
            for i in index.intersects(g.boundingBox()):
                if polys[i].contains(g):
                    return i
            return None

        fault_union = QgsGeometry.unaryUnion(list(faults)) if faults else None
        on_fault_tol = max(self.snap_tol * 0.1, 1e-6)

        votes = [defaultdict(float) for _ in polys]
        relations = []  # (left, right, upper, lower) for lines without orientation

        for bi, b in enumerate(boundaries):
            if self.feedback is not None:
                if self.feedback.isCanceled():
                    return []
                self.feedback.setProgress(80.0 * bi / max(1, len(boundaries)))
            for part in line_parts(b.geom):
                vs = polyline_xy(part)
                for a, c in zip(vs[:-1], vs[1:]):
                    dx, dy = c.x() - a.x(), c.y() - a.y()
                    seg = math.hypot(dx, dy)
                    if seg <= 0:
                        continue
                    eps = max(min(seg * 0.1, self.snap_tol * 0.1), 1e-6)
                    mx, my = (a.x() + c.x()) / 2.0, (a.y() + c.y()) / 2.0
                    if fault_union is not None and (
                        fault_union.distance(QgsGeometry.fromPointXY(QgsPointXY(mx, my))) < on_fault_tol
                    ):
                        continue  # boundary drawn along a fault: not a stratigraphic contact
                    nx_, ny_ = -dy / seg, dx / seg
                    li = locate(mx + nx_ * eps, my + ny_ * eps)
                    ri = locate(mx - nx_ * eps, my - ny_ * eps)
                    if li is None or ri is None or li == ri:
                        continue
                    if b.upper_side == "L":
                        votes[li][b.upper] += seg
                        votes[ri][b.lower] += seg
                    elif b.upper_side == "R":
                        votes[ri][b.upper] += seg
                        votes[li][b.lower] += seg
                    else:
                        relations.append((li, ri, b.upper, b.lower))

        point_votes = [defaultdict(int) for _ in polys]
        for pt, unit in unit_points or []:
            i = locate(pt.x(), pt.y())
            if i is not None and unit:
                point_votes[i][unit] += 1

        units = [None] * len(polys)
        qa = [QA_UNASSIGNED] * len(polys)
        for i in range(len(polys)):
            # unit sample points have priority over line orientation votes
            v = point_votes[i] or votes[i]
            if not v:
                continue
            ranked = sorted(v.items(), key=lambda kv: -kv[1])
            units[i] = ranked[0][0]
            qa[i] = QA_OK
            if len(ranked) > 1 and ranked[1][1] > 0.2 * ranked[0][1]:
                qa[i] = QA_CONFLICT
            elif point_votes[i] and votes[i]:
                line_best = max(votes[i].items(), key=lambda kv: kv[1])[0]
                if line_best != units[i]:
                    qa[i] = QA_CONFLICT

        changed = True
        while changed:
            changed = False
            for li, ri, up, lo in relations:
                for a, b in ((li, ri), (ri, li)):
                    if units[a] is not None and units[b] is None:
                        if units[a] == up:
                            units[b], qa[b], changed = lo, QA_PROPAGATED, True
                        elif units[a] == lo:
                            units[b], qa[b], changed = up, QA_PROPAGATED, True

        # small unassigned slivers join the neighbour sharing the longest edge
        if self.min_area > 0:
            changed = True
            while changed:
                changed = False
                for i, p in enumerate(polys):
                    if units[i] is not None or p.area() >= self.min_area:
                        continue
                    best, best_len = None, 0.0
                    for j in index.intersects(p.boundingBox()):
                        if j == i or units[j] is None:
                            continue
                        shared = p.intersection(polys[j]).length()
                        if shared > best_len:
                            best, best_len = j, shared
                    if best is not None:
                        units[i], qa[i], changed = units[best], QA_PROPAGATED, True

        n_un = sum(1 for u in units if u is None)
        if n_un:
            self._log("Unassigned polygons: %d" % n_un)

        if not dissolve:
            return [GeologyPolygon(p, units[i], qa[i]) for i, p in enumerate(polys)]

        result = []
        by_unit = defaultdict(list)
        for i, p in enumerate(polys):
            if units[i] is None:
                result.append(GeologyPolygon(p, None, QA_UNASSIGNED))
            else:
                by_unit[units[i]].append(i)
        rank = {QA_CONFLICT: 3, QA_PROPAGATED: 2, QA_OK: 1}
        for unit in sorted(by_unit):
            ids = by_unit[unit]
            geom = QgsGeometry.unaryUnion([polys[i] for i in ids])
            worst = max((qa[i] for i in ids), key=lambda q: rank.get(q, 0))
            result.append(GeologyPolygon(geom, unit, worst))
        return result
