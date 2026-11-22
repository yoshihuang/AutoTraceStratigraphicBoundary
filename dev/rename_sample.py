"""Rename the layer-tree group named after the old GeoPackage and re-save case.qgz with QGIS."""
from qgis_env import *
from qgis.core import QgsProject
p = QgsProject.instance()
assert p.read(os.path.join(SAMPLE, "case.qgz"))
for g in p.layerTreeRoot().findGroups(True):
    if g.name().startswith("c19_"):
        print("group renamed:", g.name(), "-> data"); g.setName("data")
assert p.write(os.path.join(SAMPLE, "case.qgz"))
p.clear()
assert p.read(os.path.join(SAMPLE, "case.qgz"))
bad = [l.name() for l in p.mapLayers().values() if not l.isValid()]
print("layers", len(p.mapLayers()), "invalid", bad)
print(sorted({l.source().split("|")[0].replace("\\", "/").split("/")[-1] for l in p.mapLayers().values()}))
import zipfile; print(zipfile.ZipFile(os.path.join(SAMPLE, "case.qgz")).namelist())
