"""Start a headless QGIS application for dev tests."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import QgsApplication
qgs = QgsApplication([], False)
qgs.initQgis()
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
SAMPLE = os.path.join(os.path.dirname(HERE), "c19_斜移斷層_由錯開的褶皺樞紐求淨滑移_gpkg")
GPKG = os.path.join(SAMPLE, "data.gpkg")
DEM = os.path.join(SAMPLE, "DEM.tif")
