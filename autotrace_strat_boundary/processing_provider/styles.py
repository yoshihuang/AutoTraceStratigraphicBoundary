# -*- coding: utf-8 -*-
"""Default styles for the algorithm outputs (applied in the main thread)."""
from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsLineSymbol,
    QgsPalLayerSettings,
    QgsProcessingLayerPostProcessorInterface,
    QgsRendererCategory,
    QgsVectorLayerSimpleLabeling,
)

from .. import compat

PALETTE = [
    "#e41a1c", "#ff7f00", "#4daf4a", "#377eb8", "#984ea3",
    "#a65628", "#f781bf", "#1b9e77", "#d95f02", "#7570b3",
]
FILL_PALETTE = [
    "#f4a582", "#fddbc7", "#d1e5f0", "#92c5de", "#b8e186",
    "#fee08b", "#c2a5cf", "#e6f598", "#fdae61", "#abdda4",
]


def _line_label(layer, expression):
    s = QgsPalLayerSettings()
    s.fieldName = expression
    s.isExpression = True
    # Qgis.LabelPlacement since QGIS 3.26, scoped QgsPalLayerSettings.Placement before
    s.placement = compat._enum("Qgis.LabelPlacement.Line", "QgsPalLayerSettings.Placement.Line")
    layer.setLabeling(QgsVectorLayerSimpleLabeling(s))
    layer.setLabelsEnabled(True)


def style_trace_layer(layer):
    idx = layer.fields().indexOf("unit_u")
    if idx < 0:
        return
    values = sorted({str(v) for v in layer.uniqueValues(idx)})
    cats = []
    for i, v in enumerate(values):
        sym = QgsLineSymbol.createSimple(
            {"line_color": PALETTE[i % len(PALETTE)], "line_width": "0.6", "line_style": "dash"}
        )
        cats.append(QgsRendererCategory(v, sym, v))
    layer.setRenderer(QgsCategorizedSymbolRenderer("unit_u", cats))
    _line_label(layer, "\"unit_u\" || '/' || \"unit_d\"")
    layer.triggerRepaint()


def style_geology_layer(layer, template_renderer=None):
    if template_renderer is not None:
        layer.setRenderer(template_renderer)
        layer.triggerRepaint()
        return
    idx = layer.fields().indexOf("unit_code")
    if idx < 0:
        return
    values = sorted({str(v) for v in layer.uniqueValues(idx) if v is not None and str(v) != "NULL"})
    cats = []
    for i, v in enumerate(values):
        sym = QgsFillSymbol.createSimple(
            {"color": FILL_PALETTE[i % len(FILL_PALETTE)], "outline_color": "#555555", "outline_width": "0.2"}
        )
        cats.append(QgsRendererCategory(v, sym, v))
    unk = QgsFillSymbol.createSimple({"color": "#bbbbbb", "style": "b_diagonal", "outline_color": "#ff0000"})
    cats.append(QgsRendererCategory(None, unk, "?"))
    layer.setRenderer(QgsCategorizedSymbolRenderer("unit_code", cats))
    layer.triggerRepaint()


class StylePostProcessor(QgsProcessingLayerPostProcessorInterface):
    """Keeps a reference to itself; Processing does not take ownership in Python."""

    _alive = []

    def __init__(self, kind, renderer=None):
        super().__init__()
        self.kind = kind
        self.renderer = renderer

    def postProcessLayer(self, layer, context, feedback):  # noqa: N802
        try:
            if self.kind == "trace":
                style_trace_layer(layer)
            elif self.kind == "geology":
                style_geology_layer(layer, self.renderer)
        except Exception as e:  # styling must never fail the algorithm
            feedback.reportError(str(e))

    @classmethod
    def create(cls, kind, renderer=None):
        inst = cls(kind, renderer)
        cls._alive.append(inst)
        del cls._alive[:-20]
        return inst
