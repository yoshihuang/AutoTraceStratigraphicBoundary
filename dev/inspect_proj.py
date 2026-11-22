from qgis_env import *
from qgis.core import QgsProject
QgsProject.instance().read(os.path.join(SAMPLE, "case.qgz"))
root = QgsProject.instance().layerTreeRoot()
for node in root.findLayers():
    l = node.layer()
    if l is None:
        print("MISSING", node.name()); continue
    fc = l.featureCount() if hasattr(l, "featureCount") else "-"
    print("%-40s valid=%s visible=%s n=%s provider=%s src=%s" % (l.name(), l.isValid(), node.isVisible(), fc, l.providerType(), l.source()[-60:]))
