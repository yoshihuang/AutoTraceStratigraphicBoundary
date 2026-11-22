import os, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"; os.environ["QT_QPA_FONTDIR"] = r"C:\Windows\Fonts"
from qgis.core import QgsApplication, QgsProject, QgsLayoutExporter
app = QgsApplication([], True); app.initQgis()
prj = QgsProject.instance(); print("read", prj.read(sys.argv[1]))
lay = prj.layoutManager().layouts()[0]
ex = QgsLayoutExporter(lay); s = QgsLayoutExporter.ImageExportSettings(); s.dpi = 60
print("export", ex.exportToImage(sys.argv[2], s))
