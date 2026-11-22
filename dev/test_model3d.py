from qgis_env import *
import time, numpy as np
from qgis.core import QgsVectorLayer, QgsGeometry, QgsPointXY
from autotrace_strat_boundary.core.model3d import GeoModel, Unit, Fault, AIR, NONE
from autotrace_strat_boundary.core import model_inputs as mi
L = lambda n: QgsVectorLayer(GPKG + "|layername=" + n, n, "ogr")
geo, flt, bed, sb = L("geology"), L("faults"), L("bedding"), L("Stratigraphic_Boundary")
t0 = time.time()
units, polys = [], []
for f in sorted(geo.getFeatures(), key=lambda f: f["strat_order"]):
    units.append(Unit(f["unit_code"], f["unit_name"], f["strat_order"], f["series"] or 1, f["thick_m"], f["kind"]))
    polys.append((f.geometry(), len(units) - 1))
code = {u.code: i for i, u in enumerate(units)}
ext = geo.extent(); extent = (ext.xMinimum(), ext.yMinimum(), ext.xMaximum(), ext.yMaximum())
topo = mi.read_topography(DEM, 1, extent, max_cells=400)
faults = [Fault(f["name"], mi.trace_xy(f.geometry())[0], f["dip"], f["dip_dir"], topo) for f in flt.getFeatures()]
zbase = topo.min - 0.35 * max(extent[2]-extent[0], extent[3]-extent[1])
model = GeoModel(units, topo, extent, zbase, faults, log=print)
contacts = mi.contacts_from_geology(polys, [f.geometry() for f in flt.getFeatures()], topo, 20, 5)
grads = []
for f in bed.getFeatures():
    p = f.geometry().asPoint(); n = mi.attitude_normal(f["dip"], f["dip_dir"], f["overturned"] == 1)
    grads.append((p.x(), p.y(), float(topo(p.x(), p.y())), *n, code.get(f["unit_code"])))
for f in sb.getFeatures():
    p = f.geometry().asPoint(); n = mi.attitude_normal(f["dip"], f["dip_dir"], f["overturned"] == 1)
    grads.append((p.x(), p.y(), float(topo(p.x(), p.y())), *n, code.get(f["unit_code_u"])))
print("contacts", len(contacts), "grads", len(grads), "prep %.1fs" % (time.time()-t0))
t1 = time.time(); model.build(contacts, grads); print("build %.1fs" % (time.time()-t1))
# surface agreement
xs = np.linspace(extent[0]+5, extent[2]-5, 120); ys = np.linspace(extent[1]+5, extent[3]-5, 120)
X, Y = np.meshgrid(xs, ys); X, Y = X.ravel(), Y.ravel(); Z = topo(X, Y) - 1.0
t2 = time.time(); U = model.unit_index(X, Y, Z); print("eval %d pts %.1fs" % (len(X), time.time()-t2))
idx = mi.polygon_index(polys)
truth = np.array([mi.unit_at(polys, idx, x, y) if mi.unit_at(polys, idx, x, y) is not None else -9 for x, y in zip(X, Y)])
ok = (U == truth) & (truth >= 0)
print("surface agreement %.1f%%" % (100 * ok.sum() / (truth >= 0).sum()))
for i, u in enumerate(units):
    m = truth == i; print(" ", u.code, "map cells", m.sum(), "agree %.0f%%" % (100 * (U[m] == i).mean() if m.any() else 0))
print("warnings", model.warnings)
