"""Package the sample project: copy the folder, drop empty temporary layers, zip into the plugin."""
from qgis_env import *
import shutil, tempfile, zipfile
from qgis.core import QgsProject
name = os.path.basename(SAMPLE)
tmp = tempfile.mkdtemp()
dst = os.path.join(tmp, name)
shutil.copytree(SAMPLE, dst, ignore=shutil.ignore_patterns("*.gpkg-shm", "*.gpkg-wal", "*.qgz~", "*.qgs~"))
prj = QgsProject.instance()
prj.read(os.path.join(dst, "case.qgz"))
drop = [l.id() for l in prj.mapLayers().values() if l.providerType() == "memory" and l.featureCount() == 0]
print("removing empty temporary layers:", [prj.mapLayer(i).name() for i in drop])
prj.removeMapLayers(drop)
assert prj.write(os.path.join(dst, "case.qgz"))
prj.clear()
out = os.path.join(os.path.dirname(HERE), "autotrace_strat_boundary", "data", "case_sample.zip")
os.makedirs(os.path.dirname(out), exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(dst)):
        z.write(os.path.join(dst, f), name + "/" + f)
print("written", out, os.path.getsize(out) // 1024, "KB")
# verify: extract + open
chk = tempfile.mkdtemp()
zipfile.ZipFile(out).extractall(chk)
prj.read(os.path.join(chk, name, "case.qgz"))
print({l.name(): (l.isValid(), l.featureCount() if hasattr(l, "featureCount") else "-") for l in prj.mapLayers().values()})
