"""Help figures for the 3D model tool (run after test_model_alg.py)."""
import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"; os.environ["QT_QPA_FONTDIR"] = r"C:\Windows\Fonts"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsMapSettings, QgsMapRendererParallelJob
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor
app = QgsApplication([], True); app.initQgis()
from autotrace_strat_boundary.processing_provider.model_layers import style
gpkg = sys.argv[1]; out = sys.argv[2]
lays = []
for n in ("section_labels", "section_frame", "section_faults", "section_profile", "section_units"):
    l = QgsVectorLayer("%s|layername=%s" % (gpkg, n), n, "ogr"); style(l, n)
    if n == "section_labels": l.setSubsetString("\"kind\" <> 'title'")
    QgsProject.instance().addMapLayer(l); lays.append(l)
ext = lays[1].extent(); ext.grow(ext.width() * 0.05)
ms = QgsMapSettings(); ms.setLayers(lays); ms.setDestinationCrs(lays[0].crs()); ms.setExtent(ext)
W = 1100; ms.setOutputSize(QSize(W, int(W * ext.height() / ext.width()))); ms.setOutputDpi(110); ms.setBackgroundColor(QColor("white"))
job = QgsMapRendererParallelJob(ms); job.start(); job.waitForFinished(); job.renderedImage().save(out); print("saved", out)
