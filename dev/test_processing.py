from qgis_env import *
from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback, QgsProject, QgsRasterLayer, QgsVectorLayer
from processing.core.Processing import Processing
Processing.initialize()
import processing
from autotrace_strat_boundary.processing_provider.provider import AutoTraceStratProvider
prov = AutoTraceStratProvider(); QgsApplication.processingRegistry().addProvider(prov)
from autotrace_strat_boundary import i18n
import sys
if len(sys.argv) > 1: i18n.set_preferred(sys.argv[1])
alg = QgsApplication.processingRegistry().algorithmById("autotracestrat:tracestratboundary")
print(alg.displayName(), "|", [p.description() for p in alg.parameterDefinitions()][:3])
fb = QgsProcessingFeedback()
r = processing.run("autotracestrat:tracestratboundary", {
    "POINTS": GPKG + "|layername=Stratigraphic_Boundary", "DEM": DEM,
    "FAULTS": GPKG + "|layername=faults", "OUTPUT": "memory:"}, feedback=fb)
lines = r["OUTPUT"]; print("lines", lines.featureCount(), [f.attributes()[:7] for f in lines.getFeatures()][:3])
r2 = processing.run("autotracestrat:buildgeology", {
    "BOUNDARIES": lines, "FAULTS": GPKG + "|layername=faults", "EXTENT": "250000,252000,2650000,2652000 [EPSG:3826]",
    "UNIT_POINTS": GPKG + "|layername=bedding", "TEMPLATE": GPKG + "|layername=geology",
    "OUTPUT": "memory:", "DANGLES": "memory:"}, feedback=fb)
g = r2["OUTPUT"]
for f in g.getFeatures(): print(f.attributes())
print("dangles", r2["DANGLES"].featureCount())
i18n.set_preferred("auto")
