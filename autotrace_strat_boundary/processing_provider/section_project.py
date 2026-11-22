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


def _label(layout, text, x, y, w, h, size, bold, mm):
    lbl = QgsLayoutItemLabel(layout)
    lbl.setText(text)
    f = QFont("Arial", size)
    f.setBold(bold)
    try:
        from qgis.core import QgsTextFormat

        fmt = QgsTextFormat()
        fmt.setFont(f)
        fmt.setSize(size)
        lbl.setTextFormat(fmt)
    except (ImportError, AttributeError):
        lbl.setFont(f)
    lbl.attemptMove(QgsLayoutPoint(x, y, mm))
    lbl.attemptResize(QgsLayoutSize(w, h, mm))
    layout.addLayoutItem(lbl)
    return lbl


def _section_layout(prj, name, title, subtitle, layers, units_layer, ext, mm):
    """A3 landscape layout: title, the section map, its legend."""
    layout = QgsPrintLayout(prj)
    layout.initializeDefaults()
    layout.setName(name)
    layout.pageCollection().page(0).setPageSize(QgsLayoutSize(420, 297, mm))
    _label(layout, title, 12, 8, 330, 12, 20, True, mm)
    _label(layout, subtitle, 12, 19, 330, 6, 9, False, mm)
    mp = QgsLayoutItemMap(layout)
    mp.attemptMove(QgsLayoutPoint(12, 28, mm))
    mp.attemptResize(QgsLayoutSize(330, 258, mm))
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
    root = lg.model().rootGroup()
    keep = units_layer.id() if units_layer is not None else None
    for node in list(root.findLayers()):
        if node.layerId() != keep:
            root.removeChildNode(node)
    lg.attemptMove(QgsLayoutPoint(350, 28, mm))
    layout.addLayoutItem(lg)
    prj.layoutManager().addLayout(layout)


def write_section_project(gpkg, qgz_path, crs, title, layers, ve=1.0):
    """Write <qgz_path> for ONE section.

    layers: {"units": table, "profile": table, "faults": table, "frame": table, "labels": table} in *gpkg*.
    Section coordinates: x = distance from the section start (0 at the left), y = elevation x V.E.
    """
    prj = QgsProject()
    prj.setCrs(crs)
    prj.setTitle(title)
    prj.setFileName(qgz_path)
    loaded, units_layer = [], None
    for kind in ("labels", "frame", "faults", "profile", "units"):
        table = layers.get(kind)
        if not table:
            continue
        lyr = QgsVectorLayer("%s|layername=%s" % (gpkg, table), table, "ogr")
        if not lyr.isValid():
            continue
        style(lyr, "section_" + kind)
        if kind == "units":
            _unit_categories(lyr)
            lyr.setName(tr("m_lyr_units"))
            units_layer = lyr
        loaded.append(lyr)
    if not loaded:
        raise IOError("No section layers in %s" % gpkg)
    prj.addMapLayers(loaded)
    ext = QgsRectangle()
    ext.setNull()
    for lyr in loaded:
        ext.combineExtentWith(lyr.extent())
    ext.grow(max(ext.width(), ext.height()) * 0.04)
    prj.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(ext, crs))
    mm = compat._enum("Qgis.LayoutUnit.Millimeters", "QgsUnitTypes.LayoutMillimeters")
    _section_layout(prj, title, title, tr("m_sec_coords", ve="%g" % ve), loaded, units_layer, ext, mm)
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
