# -*- coding: utf-8 -*-
"""Add the model GeoPackage layers to the project with ready-made styles (main thread)."""
import os

from qgis.core import (
    QgsFillSymbol,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsProject,
    QgsProperty,
    QgsSingleSymbolRenderer,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor, QFont

from .. import compat
from ..i18n import tr

VISIBLE = ("section_lines", "section_units", "section_profile", "section_faults", "section_frame", "section_labels")
ORDER = ("section_labels", "section_frame", "section_faults", "section_profile", "section_units", "section_lines",
         "section_fences_3d", "faults_3d", "horizons_3d", "units_3d", "terrain_3d")


def _fill_by_field(layer, alpha=255, outline="#333333", width="0.15"):
    sym = QgsFillSymbol.createSimple({"color": "#cccccc", "outline_color": outline, "outline_width": width})
    prop = compat._enum("QgsSymbolLayer.Property.FillColor", "QgsSymbolLayer.PropertyFillColor")
    expr = "set_color_part(\"color\", 'alpha', %d)" % alpha
    sym.symbolLayer(0).setDataDefinedProperty(prop, QgsProperty.fromExpression(expr))
    layer.setRenderer(QgsSingleSymbolRenderer(sym))


def _labels(layer, expr, size=9, bold=False, color="#000000", placement=None):
    s = QgsPalLayerSettings()
    s.fieldName = expr
    s.isExpression = True
    fmt = QgsTextFormat()
    f = QFont("Arial", size)
    f.setBold(bold)
    fmt.setFont(f)
    fmt.setSize(size)
    fmt.setColor(QColor(color))
    buf = fmt.buffer()
    buf.setEnabled(True)
    buf.setSize(0.8)
    fmt.setBuffer(buf)
    s.setFormat(fmt)
    if placement is not None:
        s.placement = placement
    layer.setLabeling(QgsVectorLayerSimpleLabeling(s))
    layer.setLabelsEnabled(True)


def style(layer, name):
    if name in ("units_3d", "terrain_3d", "section_fences_3d", "section_units", "horizons_3d"):
        _fill_by_field(layer, alpha=255 if name != "horizons_3d" else 170,
                       width="0.15" if name == "section_units" else "0")
        if name == "section_units":
            _labels(layer, '"unit_code"', 9, True)
    elif name == "faults_3d":
        layer.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
            {"color": "214,39,40,120", "outline_color": "#d62728", "outline_width": "0.1"})))
    elif name == "section_lines":
        layer.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple(
            {"line_color": "#c4122f", "line_width": "0.8", "line_style": "dash"})))
        _labels(layer, '"title"', 10, True, "#c4122f",
                compat._enum("Qgis.LabelPlacement.Line", "QgsPalLayerSettings.Placement.Line"))
    elif name == "section_profile":
        layer.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple(
            {"line_color": "#3b2a1a", "line_width": "0.6"})))
    elif name == "section_faults":
        layer.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple(
            {"line_color": "#d62728", "line_width": "0.9"})))
        _labels(layer, '"fault"', 9, True, "#d62728")
    elif name == "section_frame":
        layer.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple(
            {"line_color": "#000000", "line_width": "0.3"})))
    elif name == "section_labels":
        layer.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple(
            {"name": "circle", "size": "0", "color": "0,0,0,0", "outline_style": "no"})))
        _labels(layer, '"text"', 9, False)
        lab = layer.labeling().settings()
        props = lab.dataDefinedProperties()
        size_prop = compat._enum("QgsPalLayerSettings.Property.Size", "QgsPalLayerSettings.Size")
        bold_prop = compat._enum("QgsPalLayerSettings.Property.Bold", "QgsPalLayerSettings.Bold")
        props.setProperty(size_prop, QgsProperty.fromExpression(
            "CASE WHEN \"kind\" = 'title' THEN 12 WHEN \"kind\" = 'end' THEN 11 ELSE 8 END"))
        props.setProperty(bold_prop, QgsProperty.fromExpression("\"kind\" IN ('title', 'end')"))
        lab.setDataDefinedProperties(props)
        layer.setLabeling(QgsVectorLayerSimpleLabeling(lab))
    layer.triggerRepaint()


def load_model_layers(gpkg, project=None, names=None):
    project = project or QgsProject.instance()
    root = project.layerTreeRoot()
    group = root.insertGroup(0, tr("m_group", name=os.path.splitext(os.path.basename(gpkg))[0]))
    names = names or ORDER
    added = []
    for name in ORDER:
        if name not in names:
            continue
        lyr = QgsVectorLayer("%s|layername=%s" % (gpkg, name), name, "ogr")
        if not lyr.isValid():
            continue
        style(lyr, name)
        project.addMapLayer(lyr, False)
        node = group.addLayer(lyr)
        node.setItemVisibilityChecked(name in VISIBLE)
        node.setExpanded(False)
        added.append(lyr)
    return added
