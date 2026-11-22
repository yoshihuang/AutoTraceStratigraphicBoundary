# -*- coding: utf-8 -*-
"""A separate QGIS project for the geological sections (the user's project is not touched)."""
import os

from qgis.core import (
    Qgis,
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPrintLayout,
    QgsProject,
    QgsRectangle,
    QgsReferencedRectangle,
    QgsRendererCategory,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QProcess, QUrl
from qgis.PyQt.QtGui import QColor, QDesktopServices, QFont

from .. import compat
from ..i18n import tr
from .model_layers import style

SECTION_LAYERS = ("section_labels", "section_frame", "section_faults", "section_profile", "section_units")


def _unit_categories(layer):
    """Categorized renderer on unit_code with the colour stored in each feature (legend-friendly)."""
    seen = {}
    for f in layer.getFeatures():
        code = f["unit_code"]
        if code not in seen:
            seen[code] = (f["color"] or "#cccccc", f["unit_name"] or code)
    cats = []
    for code in sorted(seen):
        color, name = seen[code]
        sym = QgsFillSymbol.createSimple({"color": color, "outline_color": "#333333", "outline_width": "0.15"})
        label = name if str(name).startswith(str(code)) else "%s %s" % (code, name)
        cats.append(QgsRendererCategory(code, sym, label))
    layer.setRenderer(QgsCategorizedSymbolRenderer("unit_code", cats))


def write_section_project(gpkg, qgz_path, crs, title, layer_names=None):
    """Write <qgz_path> with the section-sheet layers of *gpkg* and an A3 print layout."""
    prj = QgsProject()
    prj.setCrs(crs)
    prj.setTitle(title)
    prj.setFileName(qgz_path)
    names = layer_names or SECTION_LAYERS
    layers = []
    for name in SECTION_LAYERS:
        if name not in names:
            continue
        lyr = QgsVectorLayer("%s|layername=%s" % (gpkg, name), name, "ogr")
        if not lyr.isValid():
            continue
        style(lyr, name)
        if name == "section_units":
            _unit_categories(lyr)
            lyr.setName(tr("m_lyr_units"))
        layers.append(lyr)
    if not layers:
        raise IOError("No section layers in %s" % gpkg)
    prj.addMapLayers(layers)

    ext = QgsRectangle()
    ext.setNull()
    for lyr in layers:
        ext.combineExtentWith(lyr.extent())
    ext.grow(max(ext.width(), ext.height()) * 0.03)
    prj.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(ext, crs))

    # print layout: A3 landscape, sections + legend + title
    layout = QgsPrintLayout(prj)
    layout.initializeDefaults()
    layout.setName(title)
    mm = compat._enum("Qgis.LayoutUnit.Millimeters", "QgsUnitTypes.LayoutMillimeters")
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(420, 297, mm))
    lbl = QgsLayoutItemLabel(layout)
    lbl.setText(title)
    f = QFont("Arial", 20)
    f.setBold(True)
    try:
        from qgis.core import QgsTextFormat

        fmt = QgsTextFormat()
        fmt.setFont(f)
        fmt.setSize(20)
        lbl.setTextFormat(fmt)
    except (ImportError, AttributeError):
        lbl.setFont(f)
    lbl.attemptMove(QgsLayoutPoint(12, 8, mm))
    lbl.attemptResize(QgsLayoutSize(330, 14, mm))
    layout.addLayoutItem(lbl)
    mp = QgsLayoutItemMap(layout)
    mp.attemptMove(QgsLayoutPoint(12, 26, mm))
    mp.attemptResize(QgsLayoutSize(330, 260, mm))
    mp.setLayers(layers)
    mp.setExtent(ext)
    mp.setFrameEnabled(True)
    mp.setBackgroundColor(QColor(255, 255, 255))
    layout.addLayoutItem(mp)
    lg = QgsLayoutItemLegend(layout)
    lg.setTitle(tr("m_legend"))
    lg.setLinkedMap(mp)
    manual = getattr(getattr(Qgis, "LegendSyncMode", None), "Manual", None)
    if manual is not None and hasattr(lg, "setSyncMode"):  # QGIS 4
        lg.setSyncMode(manual)
    else:
        lg.setAutoUpdateModel(False)
    model = lg.model()
    root = model.rootGroup()
    units_id = layers[-1].id() if layers[-1].name() == tr("m_lyr_units") else None
    for node in list(root.findLayers()):
        if node.layerId() != units_id:
            root.removeChildNode(node)
    lg.attemptMove(QgsLayoutPoint(350, 26, mm))
    layout.addLayoutItem(lg)
    prj.layoutManager().addLayout(layout)

    d = os.path.dirname(os.path.abspath(qgz_path))
    if not os.path.isdir(d):
        os.makedirs(d)
    if not prj.write(qgz_path):
        raise IOError("Cannot write %s: %s" % (qgz_path, prj.error()))
    return qgz_path


def open_in_new_qgis(qgz_path):
    """Open the project in a second QGIS window; True when started."""
    exe = QCoreApplication.applicationFilePath()
    base = os.path.basename(exe).lower()
    if "qgis" in base:
        res = QProcess.startDetached(exe, [qgz_path])
        ok = res[0] if isinstance(res, tuple) else bool(res)
        if ok:
            return True
    return QDesktopServices.openUrl(QUrl.fromLocalFile(qgz_path))
