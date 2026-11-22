import os, sys, tempfile, shutil
os.environ["QT_QPA_PLATFORM"] = "offscreen"
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from qgis.core import QgsApplication, QgsProject
app = QgsApplication([], True); app.initQgis()
sys.path.append(os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"))
from processing.core.Processing import Processing; Processing.initialize()
from qgis.PyQt.QtWidgets import QMainWindow, QMenu
class Iface:
    def __init__(s): s.win = QMainWindow(); s.pm = QMenu("Plugins", s.win)
    def mainWindow(s): return s.win
    def addToolBar(s, name): return s.win.addToolBar(name)
    def pluginMenu(s): return s.pm
    def newProject(s, prompt=False): QgsProject.instance().clear(); return True
    def addProject(s, p): return QgsProject.instance().read(p)
import autotrace_strat_boundary as pkg
from autotrace_strat_boundary import i18n
iface = Iface(); plugin = pkg.classFactory(iface); plugin.initGui()
reg = QgsApplication.processingRegistry()
for lang in ("en", "zh_TW", "zh_CN", "ja"):
    plugin.set_language(lang)
    alg = reg.algorithmById("autotracestrat:tracestratboundary")
    print(lang, "| menu:", plugin.menu.title(), "|", [a.text() for a in plugin.menu.actions() if a.text()][:4],
          "| alg:", alg.displayName(), "|", alg.parameterDefinition("POINTS").description())
plugin.set_language("auto"); print("auto ->", i18n.current_language())
# sample extraction + open project
from autotrace_strat_boundary.sample_data import extract_sample
tmp = tempfile.mkdtemp()
proj = extract_sample(tmp); print("project:", os.path.relpath(proj, tmp))
print("open:", iface.addProject(proj), {l.name(): l.isValid() for l in QgsProject.instance().mapLayers().values()})
# real Processing dialogs: open, read pre-filled values, close (regression: QGIS 4 deleted-widget crash)
import processing.tools.general as pg
from qgis.gui import QgsMessageBar, QgsMapCanvas
iface.messageBar = lambda bar=QgsMessageBar(): bar
iface.mapCanvas = lambda c=QgsMapCanvas(): c
pg.iface = iface
names = {l.id(): l.name() for l in QgsProject.instance().mapLayers().values()}
for run in (plugin.run_trace, plugin.run_geology, plugin.run_model3d):
    run()
    dlg = plugin._dialog
    vals = dlg.mainWidget().createProcessingParameters()
    print(dlg.windowTitle(), "visible:", dlg.isVisible(),
          {k: (v.name() if hasattr(v, "name") else names.get(v, v)) for k, v in vals.items() if k in ("POINTS","DEM","FAULTS","UNIT_POINTS","TEMPLATE","GEOLOGY","FOLDS","ATTITUDES","SECTIONS","BOUNDARIES")}, "drape:", len(vals.get("DRAPE_LAYERS") or []))
    dlg.close(); app.processEvents()
    print("closed without error")
# help dialogs
from autotrace_strat_boundary.help_dialog import HelpDialog
from qgis.PyQt.QtWidgets import QTextBrowser
for lang in ("en", "zh_TW", "zh_CN", "ja"):
    i18n.set_preferred(lang); d = HelpDialog(iface.win); b = d.findChild(QTextBrowser)
    doc = b.document(); txt = doc.toPlainText()
    from qgis.PyQt.QtGui import QTextDocument
    img = doc.resource(QTextDocument.ResourceType.ImageResource.value if hasattr(QTextDocument.ResourceType.ImageResource,"value") else QTextDocument.ImageResource, b.source().resolved(__import__("qgis.PyQt.QtCore",fromlist=["QUrl"]).QUrl("../img/fig1_structure_contours.png")))
    print(lang, "help chars", len(txt), "|", txt[:30].replace("\n"," "), "| img ok:", img is not None and not getattr(img,"isNull",lambda:False)())
i18n.set_preferred("auto")
plugin.unload(); print("unloaded; provider present:", reg.providerById("autotracestrat") is not None)
QgsProject.instance().clear(); shutil.rmtree(tmp, ignore_errors=True)
