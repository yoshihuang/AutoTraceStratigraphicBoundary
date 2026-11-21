# -*- coding: utf-8 -*-
"""QGIS GUI integration: menu, toolbar, language switch, sample data, help."""
import os

from qgis.core import QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QActionGroup, QMenu

from . import i18n
from .compat import GEOM_LINE, GEOM_POINT, GEOM_POLYGON
from .i18n import tr
from .processing_provider.provider import PROVIDER_ID, AutoTraceStratProvider

PLUGIN_DIR = os.path.dirname(__file__)
ICON_DIR = os.path.join(PLUGIN_DIR, "icons")


def _icon(name):
    return QIcon(os.path.join(ICON_DIR, name))


def _find_layer(kind, names, required_fields=()):
    """First project layer matching *kind* whose name is in *names* (else any with the fields)."""
    layers = list(QgsProject.instance().mapLayers().values())
    lowered = [n.lower() for n in names]

    def ok(layer):
        if kind == "raster":
            return isinstance(layer, QgsRasterLayer)
        if not isinstance(layer, QgsVectorLayer) or layer.geometryType() != kind:
            return False
        fields = [f.lower() for f in layer.fields().names()]
        return all(r in fields for r in required_fields)

    cands = [lyr for lyr in layers if ok(lyr)]
    for lyr in cands:
        if lyr.name().lower() in lowered:
            return lyr
    for lyr in cands:
        if any(n in lyr.name().lower() for n in lowered):
            return lyr
    return cands[0] if cands and required_fields else None


class AutoTraceStratBoundaryPlugin(object):
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.menu = None
        self.toolbar = None
        self.actions = []
        self._dialog = None

    # ------------------------------------------------------------------ lifecycle
    def initProcessing(self):  # noqa: N802
        self.provider = AutoTraceStratProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):  # noqa: N802
        self.initProcessing()
        self._build_gui()

    def unload(self):
        self._remove_gui()
        if self.provider is not None:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

    def _build_gui(self):
        win = self.iface.mainWindow()
        self.menu = QMenu(tr("plugin_name"), win)
        self.menu.setIcon(_icon("icon.svg"))
        self.toolbar = self.iface.addToolBar(tr("plugin_name"))
        self.toolbar.setObjectName("AutoTraceStratBoundaryToolbar")

        def add(icon, key, slot, toolbar=True):
            a = QAction(_icon(icon), tr(key), win)
            a.triggered.connect(slot)
            self.menu.addAction(a)
            if toolbar:
                self.toolbar.addAction(a)
            self.actions.append(a)
            return a

        add("trace.svg", "act_trace", self.run_trace)
        add("geology.svg", "act_geology", self.run_geology)
        self.menu.addSeparator()
        add("sample.svg", "act_sample", self.download_sample)
        add("help.svg", "act_help", self.show_help)
        self.menu.addSeparator()

        lang_menu = self.menu.addMenu(tr("act_language"))
        group = QActionGroup(lang_menu)
        group.setExclusive(True)
        current = i18n.preferred_setting()
        for code, label in [("auto", tr("lang_auto"))] + i18n.LANGUAGES:
            a = QAction(label, lang_menu)
            a.setCheckable(True)
            a.setChecked(code == current)
            a.triggered.connect(lambda checked=False, c=code: self.set_language(c))
            group.addAction(a)
            lang_menu.addAction(a)
            self.actions.append(a)
        self._lang_group = group

        self.iface.pluginMenu().addMenu(self.menu)

    def _remove_gui(self):
        if self.menu is not None:
            self.iface.pluginMenu().removeAction(self.menu.menuAction())
            self.menu.deleteLater()
            self.menu = None
        if self.toolbar is not None:
            self.toolbar.deleteLater()
            self.toolbar = None
        self.actions = []

    def set_language(self, code):
        i18n.set_preferred(code)
        self._remove_gui()
        self._build_gui()
        if self.provider is not None:
            self.provider.refreshAlgorithms()

    # ------------------------------------------------------------------ actions
    def run_trace(self):
        params = {}
        pts = _find_layer(GEOM_POINT, ["Stratigraphic_Boundary"], ("dip", "unit_code_u"))
        if pts is None:
            pts = _find_layer(GEOM_POINT, ["Stratigraphic_Boundary", "boundary"])
        dem = _find_layer("raster", ["DEM", "dtm", "topo"])
        if dem is None:
            rasters = [lyr for lyr in QgsProject.instance().mapLayers().values() if isinstance(lyr, QgsRasterLayer)]
            dem = rasters[0] if rasters else None
        faults = _find_layer(GEOM_LINE, ["faults", "fault", "斷層", "断层"])
        if pts is not None:
            params["POINTS"] = pts.id()
        if dem is not None:
            params["DEM"] = dem.id()
        if faults is not None:
            params["FAULTS"] = faults.id()
        self._open_algorithm_dialog("%s:tracestratboundary" % PROVIDER_ID, params)

    def _open_algorithm_dialog(self, alg_id, params):
        """Open a Processing dialog non-modally, like the Processing Toolbox does.

        processing.execAlgorithmDialog() is not used: in QGIS 4 the dialog deletes
        itself on close and execAlgorithmDialog() then calls results() on the
        deleted widget ("wrapped C/C++ object ... has been deleted").
        """
        import processing

        dlg = processing.createAlgorithmDialog(alg_id, params)
        if dlg is None:
            return
        self._dialog = dlg  # keep a Python reference while it is open
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    def run_geology(self):
        params = {}
        bnd = _find_layer(GEOM_LINE, ["predicted", "boundary", "預判", "预判", "予測"], ("unit_u", "unit_d"))
        faults = _find_layer(GEOM_LINE, ["faults", "fault", "斷層", "断层"])
        bedding = _find_layer(GEOM_POINT, ["bedding"], ("unit_code",))
        geology = _find_layer(GEOM_POLYGON, ["geology"], ("unit_code",))
        dem = _find_layer("raster", ["DEM", "dtm", "topo"])
        if bnd is not None:
            params["BOUNDARIES"] = bnd.id()
        if faults is not None:
            params["FAULTS"] = faults.id()
        if bedding is not None:
            params["UNIT_POINTS"] = bedding.id()
        if geology is not None:
            params["TEMPLATE"] = geology.id()
        if dem is not None:
            e = dem.extent()
            params["EXTENT"] = "%f,%f,%f,%f [%s]" % (
                e.xMinimum(), e.xMaximum(), e.yMinimum(), e.yMaximum(), dem.crs().authid()
            )
        self._open_algorithm_dialog("%s:buildgeology" % PROVIDER_ID, params)

    def download_sample(self):
        from .sample_data import download_sample_dialog

        download_sample_dialog(self.iface)

    def show_help(self):
        from .help_dialog import HelpDialog

        dlg = HelpDialog(self.iface.mainWindow())
        dlg.exec() if hasattr(dlg, "exec") else dlg.exec_()
