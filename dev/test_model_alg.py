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
r = processing.run("autotracestrat:buildmodel3d", {
    "GEOLOGY": P["geology"], "DEM": P["DEM"], "FAULTS": P["faults"], "ATTITUDES": P["bedding"],
    "ATTITUDES2": P["Stratigraphic_Boundary"], "SECTIONS": P["section_line"], "VERTICAL_EXAGGERATION": 1,
    "FOLDS": P["fold_axes"], "OPEN_VIEWER": False, "OUTPUT_GPKG": OUT,
    "DRAPE_LAYERS": [P[n] for n in ("Stratigraphic_Boundary", "faults", "fold_axes", "contours", "geology")],
    "OUTPUT_DXF": os.path.join(os.path.dirname(OUT), "cad", "c19_cad.dxf"),
    "OUTPUT_OBJ": os.path.join(os.path.dirname(OUT), "cad", "c19_cad.obj"),
    "OUTPUT_STL": os.path.join(os.path.dirname(OUT), "cad", "c19_cad.stl"),
    "OUTPUT_VIEWER": os.path.join(os.path.dirname(OUT), "c19_view.html")})
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
# temporary CAD outputs -> next to the gpkg
OUT2 = os.path.join(os.path.dirname(OUT), "tmpcase", "m2.gpkg")
r2 = processing.run("autotracestrat:buildmodel3d", {"GEOLOGY": P["geology"], "DEM": P["DEM"], "FAULTS": P["faults"],
    "OPEN_VIEWER": False, "OUTPUT_GPKG": OUT2, "OUTPUT_DXF": "TEMPORARY_OUTPUT", "OUTPUT_STL": None})
print("temp case:", sorted(os.listdir(os.path.dirname(OUT2))), {k: os.path.basename(v) for k, v in r2.items() if k != "CAD_FILES"})
# render map + section sheet as QGIS shows it
os.environ["QT_QPA_FONTDIR"] = r"C:\Windows\Fonts"
from qgis.core import QgsMapSettings, QgsMapRendererParallelJob, QgsRectangle
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor
lays = [l for l in QgsProject.instance().layerTreeRoot().checkedLayers()]
lays = [l for l in lays if l.name() not in ("contours",)]
ext = QgsRectangle()
for l in lays:
    if l.name().startswith("section_") or l.name() in ("geology",):
        ext.combineExtentWith(l.extent())
ext.grow(80)
ms = QgsMapSettings(); ms.setLayers(lays); ms.setDestinationCrs(P["geology"].crs()); ms.setExtent(ext)
ms.setOutputSize(QSize(900, int(900 * ext.height() / ext.width()))); ms.setBackgroundColor(QColor("white")); ms.setOutputDpi(96)
job = QgsMapRendererParallelJob(ms); job.start(); job.waitForFinished()
job.renderedImage().save(os.path.join(os.path.dirname(OUT), "sheet.png")); print("sheet rendered", [l.name() for l in lays][:12])
