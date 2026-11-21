import os, sys, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import QgsApplication, QgsProject
app = QgsApplication([], True); app.initQgis()
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
from processing.core.Processing import Processing; Processing.initialize()
import processing
from osgeo import gdal; print("GDAL", gdal.__version__)
from autotrace_strat_boundary.processing_provider.provider import AutoTraceStratProvider
PROV = AutoTraceStratProvider(); QgsApplication.processingRegistry().addProvider(PROV)
from autotrace_strat_boundary.sample_data import extract_sample
tmp = tempfile.mkdtemp(); QgsProject.instance().read(extract_sample(tmp))
P = {l.name(): l for l in QgsProject.instance().mapLayers().values()}
r = processing.runAndLoadResults("autotracestrat:tracestratboundary", {"POINTS": P["Stratigraphic_Boundary"], "DEM": P["DEM"], "FAULTS": P["faults"], "OUTPUT": "TEMPORARY_OUTPUT"})
lay = QgsProject.instance().mapLayer(r["OUTPUT"])
print("trace layer:", lay.name(), lay.featureCount(), type(lay.renderer()).__name__, lay.labelsEnabled(), "editable provider:", lay.dataProvider().name())
r2 = processing.runAndLoadResults("autotracestrat:buildgeology", {"BOUNDARIES": lay, "FAULTS": P["faults"], "EXTENT": P["DEM"].extent(),
    "UNIT_POINTS": P["bedding"], "TEMPLATE": P["geology"], "OUTPUT": "TEMPORARY_OUTPUT", "DANGLES": "TEMPORARY_OUTPUT"})
g = QgsProject.instance().mapLayer(r2["OUTPUT"])
print("geology layer:", g.name(), g.featureCount(), type(g.renderer()).__name__, [c.label() for c in g.renderer().categories()][:6])
print("dangles:", QgsProject.instance().mapLayer(r2["DANGLES"]).featureCount())
