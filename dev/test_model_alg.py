import os, sys, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import QgsApplication, QgsProject
app = QgsApplication([], True); app.initQgis()
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
from processing.core.Processing import Processing; Processing.initialize()
import processing
from autotrace_strat_boundary.processing_provider.provider import AutoTraceStratProvider
PROV = AutoTraceStratProvider(); QgsApplication.processingRegistry().addProvider(PROV)
SAMPLE = os.path.join(os.path.dirname(HERE), "c19_斜移斷層_由錯開的褶皺樞紐求淨滑移_gpkg")
QgsProject.instance().read(os.path.join(SAMPLE, "C19.qgz"))
P = {l.name(): l for l in QgsProject.instance().mapLayers().values()}
OUT = sys.argv[1]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
t = time.time()
n_before = len(QgsProject.instance().mapLayers())
r = processing.run("autotracestrat:buildmodel3d", {
    "GEOLOGY": P["geology"], "DEM": P["DEM"], "FAULTS": P["faults"], "ATTITUDES": P["bedding"],
    "ATTITUDES2": P["Stratigraphic_Boundary"], "SECTIONS": P["section_line"], "VERTICAL_EXAGGERATION": 1,
    "FOLDS": P["fold_axes"], "DRAPE_LAYERS": [P[n] for n in ("Stratigraphic_Boundary", "faults", "fold_axes", "contours", "geology")],
    "OUTPUT_FOLDER": os.path.dirname(OUT), "FILE_PREFIX": os.path.splitext(os.path.basename(OUT))[0],
    "CAD_FORMATS": [0, 1, 2], "OPEN_VIEWER": False, "OPEN_SECTIONS": False})
print("project layers before/after:", n_before, len(QgsProject.instance().mapLayers()))
print("time %.1fs" % (time.time() - t))
print(r)
import sqlite3
c = sqlite3.connect(OUT)
for (n,) in c.execute("select table_name from gpkg_contents"):
    print("  ", n, c.execute('select count(*) from "%s"' % n).fetchone()[0])
print(c.execute("select * from model_info").fetchall())
print([l.name() for l in QgsProject.instance().mapLayers().values() if l.source().startswith(OUT)])
for dp, dn, fn in os.walk(os.path.dirname(OUT)):
    for f in sorted(fn):
        print("  file", os.path.relpath(os.path.join(dp, f), os.path.dirname(OUT)), os.path.getsize(os.path.join(dp, f)) // 1024, "KB")
# the sections project
from qgis.core import QgsProject as _P
sp = _P(); ok = sp.read(r["SECTIONS_PROJECT"])
print("sections project:", ok, [l.name() for l in sp.mapLayers().values()], [lo.name() for lo in sp.layoutManager().layouts()])
