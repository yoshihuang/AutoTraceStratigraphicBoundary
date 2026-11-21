from qgis_env import *
from qgis.core import QgsVectorLayer, QgsGeometry
from autotrace_strat_boundary.core.tracer import BoundaryTracer, DemGrid, OutcropPoint
from autotrace_strat_boundary.core.geology_builder import GeologyBuilder, BoundaryLine, stratigraphic_order
from autotrace_strat_boundary.core.geom_utils import line_parts
L = lambda n: QgsVectorLayer(GPKG + "|layername=" + n, n, "ogr")
pts_l, flt, geo, bed = L("Stratigraphic_Boundary"), L("faults"), L("geology"), L("bedding")
faults=[f.geometry() for f in flt.getFeatures()]
gs = {f["unit_code"]: f.geometry() for f in geo.getFeatures()}
dem = DemGrid(DEM)
def score(polys, tag):
    ok=sum(p.geom.intersection(gs[p.unit]).area() for p in polys if p.unit in gs)
    print(tag, "units", sorted((p.unit, p.qa) for p in polys if p.unit), "unassigned", sum(1 for p in polys if p.unit is None), "correct area %.1f%%" % (100*ok/4e6))
pts = [OutcropPoint(f.id(), f.geometry().asPoint().x(), f.geometry().asPoint().y(), f["dip"], f["dip_dir"], f["unit_code_u"], f["unit_code_d"], f["overturned"]) for f in pts_l.getFeatures()]
tr = BoundaryTracer(dem, faults, connect_gap=100).run(pts)
bl = [BoundaryLine(r.geom, r.upper, r.lower, r.upper_side) for r in tr]
print("order", stratigraphic_order(bl))
gb = GeologyBuilder(dem.extent, 2.5, min_area=100)
score(gb.build(bl, faults), "traced(raw)")
bedpts=[(f.geometry().asPoint(), f["unit_code"]) for f in bed.getFeatures()]
score(gb.build(bl, faults, bedpts), "traced+bedding")
# truth lines, no orientation, + 1 seed point
truth=[]
for u,d in [("O5","O4"),("O4","O3"),("O3","O2"),("O2","O1")]:
    for p in line_parts(gs[u].intersection(gs[d]).mergeLines()): truth.append(BoundaryLine(p,u,d,""))
score(gb.build(truth, faults, bedpts[:1]), "truth-lines+1seed")
score(gb.build(truth, faults, bedpts), "truth-lines+bedding")
gb5 = GeologyBuilder(dem.extent, 5, min_area=100)
score(gb5.build(truth, faults, bedpts), "truth-lines+bedding snap5")
score(gb5.build(truth, faults, bedpts[:1]), "truth-lines+1seed snap5")
print("dangles snap2.5", len(gb.find_dangles(truth, faults)), "snap5", len(gb5.dangles))
