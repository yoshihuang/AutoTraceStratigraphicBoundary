from qgis_env import *
from qgis.core import QgsVectorLayer, QgsGeometry
from autotrace_strat_boundary.core.tracer import BoundaryTracer, DemGrid, OutcropPoint
pts_l = QgsVectorLayer(GPKG + "|layername=Stratigraphic_Boundary", "p", "ogr")
flt = QgsVectorLayer(GPKG + "|layername=faults", "f", "ogr")
geo = QgsVectorLayer(GPKG + "|layername=geology", "g", "ogr")
pts = [OutcropPoint(f.id(), f.geometry().asPoint().x(), f.geometry().asPoint().y(), f["dip"], f["dip_dir"], f["unit_code_u"], f["unit_code_d"], f["overturned"]) for f in pts_l.getFeatures()]
dem = DemGrid(DEM)
tr = BoundaryTracer(dem, [f.geometry() for f in flt.getFeatures()])
res = tr.run(pts)
print("\n".join(tr.messages))
# truth: shared boundaries between geology polygons
gs = {f["unit_code"]: f.geometry() for f in geo.getFeatures()}
fault = QgsGeometry.unaryUnion([f.geometry() for f in flt.getFeatures()])
for r in res:
    truth = gs[r.upper].intersection(gs[r.lower])
    # sample distances
    L = r.geom.length(); ds=[]
    n=50
    for i in range(n+1):
        p = r.geom.interpolate(L*i/n)
        ds.append(p.distance(truth))
    ds.sort()
    print(r.upper, r.lower, "blk", r.block, "pts", [p.fid for p in r.points], "side", r.upper_side, "len %.0f" % L,
          "dist median %.1f p90 %.1f max %.1f" % (ds[len(ds)//2], ds[int(len(ds)*.9)], ds[-1]))
