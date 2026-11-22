"""Run the 3D tool with a temporary output folder and log every message (regression for CRS transform errors)."""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import (QgsApplication, QgsProject, QgsProcessingFeedback, QgsMessageLog, QgsVectorLayer,
                       QgsCoordinateReferenceSystem, QgsCoordinateTransform)
app = QgsApplication([], True); app.initQgis()
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
from processing.core.Processing import Processing; Processing.initialize()
import processing
from autotrace_strat_boundary.processing_provider.provider import AutoTraceStratProvider
PROV = AutoTraceStratProvider(); QgsApplication.processingRegistry().addProvider(PROV)

msgs = []
QgsApplication.messageLog().messageReceived.connect(lambda m, tag, lvl: msgs.append("LOG[%s] %s" % (tag, m)))


class FB(QgsProcessingFeedback):
    def reportError(self, error, fatalError=False):
        msgs.append("ERROR " + error)

    def pushWarning(self, w):
        msgs.append("WARN " + w)


SAMPLE = os.path.join(os.path.dirname(HERE), "case")
QgsProject.instance().read(os.path.join(SAMPLE, "case.qgz"))
P = {l.name(): l for l in QgsProject.instance().mapLayers().values()}
r = processing.run("autotracestrat:buildmodel3d", {
    "GEOLOGY": P["geology_Interpolation"], "DEM": P["DEM"], "FAULTS": P["faults"], "SECTIONS": P["section_line"],
    "OUTPUT_FOLDER": "TEMPORARY_OUTPUT", "CAD_FORMATS": [0, 1], "OPEN_VIEWER": False, "OPEN_SECTIONS": False},
    feedback=FB())
print("folder:", r["OUTPUT_FOLDER"])
# what QGIS does with the outputs: open the section project, compute WGS84 extents, save it again
for proj in r["SECTION_PROJECTS"].split(";"):
    sp = QgsProject(); print("read", sp.read(proj))
    for l in sp.mapLayers().values():
        try:
            l.wgs84Extent(True)
        except Exception as e:
            msgs.append("wgs84Extent %s: %s" % (l.name(), e))
    print("write", sp.write(proj))
# loading a section layer into the main (EPSG:3826) project, as a user would
lyr = QgsVectorLayer(r["OUTPUT_GPKG"] + "|layername=section_A_A_units", "u", "ogr")
QgsProject.instance().addMapLayer(lyr)
try:
    QgsCoordinateTransform(lyr.crs(), QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance()).transformBoundingBox(lyr.extent())
except Exception as e:
    msgs.append("transform to 4326: %s" % e)
for n in ("section_A_A_units", "section_A_A_profile"):
    l = QgsVectorLayer(r["OUTPUT_GPKG"] + "|layername=" + n, n, "ogr")
    ct = QgsCoordinateTransform(l.crs(), QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
    print("%s CRS=%s transform-to-4326 valid=%s extent=%s" % (n, l.crs().authid(), ct.isValid(), l.extent().toString(1)))
hits = [m for m in msgs if "transform" in m.lower() or "4096" in m]
print("messages mentioning transform:", len(hits))
for m in hits[:8]:
    print("  ", m[:200])
