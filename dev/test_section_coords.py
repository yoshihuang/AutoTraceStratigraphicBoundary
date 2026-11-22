"""Section sheet coordinates: x from 0, y = elevation (V.E. 1 and 2), two sections."""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
app = QgsApplication([], True); app.initQgis()
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
from processing.core.Processing import Processing; Processing.initialize()
import processing
from autotrace_strat_boundary.processing_provider.provider import AutoTraceStratProvider
PROV = AutoTraceStratProvider(); QgsApplication.processingRegistry().addProvider(PROV)
from autotrace_strat_boundary.core.model_inputs import read_topography
SAMPLE = os.path.join(os.path.dirname(HERE), "case")
QgsProject.instance().read(os.path.join(SAMPLE, "case.qgz"))
P = {l.name(): l for l in QgsProject.instance().mapLayers().values()}
secs = QgsVectorLayer("LineString?crs=EPSG:3826&field=name:string", "secs", "memory")
feats = []
for f in P["section_line"].getFeatures():
    g = QgsFeature(secs.fields()); g.setGeometry(f.geometry()); g.setAttributes([f["name"]]); feats.append(g)
g = QgsFeature(secs.fields()); g.setGeometry(QgsGeometry.fromWkt("LineString(250400 2651900, 250400 2650100)")); g.setAttributes(["B-B'"]); feats.append(g)
secs.dataProvider().addFeatures(feats)
topo = read_topography(os.path.join(SAMPLE, "DEM.tif"), 1, (250000, 2650000, 252000, 2652000), max_cells=400)
OUT = sys.argv[1]
from qgis.core import QgsProcessingFeedback
class FB(QgsProcessingFeedback):
    def reportError(self, error, fatalError=False):
        print("  REPORTED ERROR:", error)
    def pushWarning(self, w):
        print("  WARNING:", w)
for ve in (1, 2):
    r = processing.run("autotracestrat:buildmodel3d", {
        "GEOLOGY": P["geology_Interpolation"], "DEM": P["DEM"], "FAULTS": P["faults"], "FOLDS": P["fold_axes"],
        "ATTITUDES": P["bedding"], "ATTITUDES2": P["Stratigraphic_Boundary"], "SECTIONS": secs,
        "VERTICAL_EXAGGERATION": ve, "OUTPUT_FOLDER": OUT, "FILE_PREFIX": "ve%d" % ve, "CAD_FORMATS": [],
        "OPEN_VIEWER": False, "OPEN_SECTIONS": False}, feedback=FB())
    gp = r["OUTPUT_GPKG"]
    import sqlite3
    tables = [t for (t,) in sqlite3.connect(gp).execute("select table_name from gpkg_contents order by table_name")]
    print("V.E.", ve, "| section tables:", [t for t in tables if t.startswith("section_")])
    for proj in r["SECTION_PROJECTS"].split(";"):
        sp = QgsProject(); ok = sp.read(proj)
        lays = {l.name(): l for l in sp.mapLayers().values()}
        prof = [l for l in sp.mapLayers().values() if l.name().endswith("_profile")][0]
        frame = [l for l in sp.mapLayers().values() if l.name().endswith("_frame")][0]
        f = next(prof.getFeatures()); pts = f.geometry().asPolyline()
        line = [l for l in feats if l["name"] == f["section"]][0].geometry().asPolyline()
        z0 = float(topo(line[0].x(), line[0].y()))
        fr = [g for g in frame.getFeatures() if g["kind"] == "frame"][0].geometry().boundingBox()
        print("  %s read=%s layers=%d layouts=%s CRS=%s" % (os.path.basename(proj), ok, len(lays),
              [lo.name() for lo in sp.layoutManager().layouts()], sp.crs().description()))
        print("     start x=%.2f start y=%.2f | ground at start %.2f (x V.E. %.2f) | frame x %.0f..%.0f y %.0f..%.0f"
              % (pts[0].x(), pts[0].y(), z0, z0 * ve, fr.xMinimum(), fr.xMaximum(), fr.yMinimum(), fr.yMaximum()))
