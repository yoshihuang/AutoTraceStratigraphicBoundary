# -*- coding: utf-8 -*-
"""Processing algorithm: build a geological map from boundary lines and faults."""
import os

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterExtent,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorLayer,
    QgsRectangle,
)
from qgis.PyQt.QtGui import QIcon

from .. import compat
from ..compat import is_null
from ..core.geology_builder import BoundaryLine, GeologyBuilder, stratigraphic_order
from ..i18n import tr
from .alg_trace import ICON_DIR, _advanced, existing_field
from .styles import StylePostProcessor

# same schema as the sample geology layer
GEOLOGY_FIELDS = [
    ("unit_code", "s"),
    ("unit_name", "s"),
    ("strat_order", "i"),
    ("series", "i"),
    ("thick_m", "d"),
    ("kind", "s"),
]


def geology_fields():
    fields = QgsFields()
    make = {"s": compat.field_string, "i": compat.field_int, "d": compat.field_double}
    for name, t in GEOLOGY_FIELDS:
        fields.append(make[t](name))
    fields.append(compat.field_string("qa", 12))
    fields.append(compat.field_double("area_m2"))
    return fields


class BuildGeologyAlgorithm(QgsProcessingAlgorithm):
    BOUNDARIES = "BOUNDARIES"
    UPPER = "UPPER_FIELD"
    LOWER = "LOWER_FIELD"
    SIDE = "SIDE_FIELD"
    FAULTS = "FAULTS"
    EXTENT = "EXTENT"
    UNIT_POINTS = "UNIT_POINTS"
    UNIT_FIELD = "UNIT_POINT_FIELD"
    TEMPLATE = "TEMPLATE"
    TEMPLATE_FIELD = "TEMPLATE_FIELD"
    SNAP = "SNAP_TOLERANCE"
    MIN_AREA = "MIN_AREA"
    DISSOLVE = "DISSOLVE"
    OUTPUT = "OUTPUT"
    DANGLES = "DANGLES"

    def name(self):
        return "buildgeology"

    def displayName(self):  # noqa: N802
        return tr("alg_geology")

    def group(self):
        return tr("group_name")

    def groupId(self):  # noqa: N802
        return "geomapping"

    def shortHelpString(self):  # noqa: N802
        return tr("help_geology")

    def icon(self):
        return QIcon(os.path.join(ICON_DIR, "geology.svg"))

    def createInstance(self):  # noqa: N802
        return BuildGeologyAlgorithm()

    def initAlgorithm(self, config=None):  # noqa: N802
        self.addParameter(
            QgsProcessingParameterFeatureSource(self.BOUNDARIES, tr("g_bnd"), [compat.TYPE_VECTOR_LINE])
        )
        self.addParameter(
            QgsProcessingParameterField(self.UPPER, tr("p_upper"), "unit_u", self.BOUNDARIES, compat.FIELD_ANY)
        )
        self.addParameter(
            QgsProcessingParameterField(self.LOWER, tr("p_lower"), "unit_d", self.BOUNDARIES, compat.FIELD_ANY)
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.SIDE, tr("g_side"), "upper_side", self.BOUNDARIES, compat.FIELD_ANY, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.FAULTS, tr("p_faults"), [compat.TYPE_VECTOR_LINE], optional=True
            )
        )
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, tr("g_extent"), optional=True))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.UNIT_POINTS, tr("g_unitpts"), [compat.TYPE_VECTOR_POINT], optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIT_FIELD, tr("g_unitfield"), "unit_code", self.UNIT_POINTS, compat.FIELD_ANY, optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TEMPLATE, tr("g_template"), [compat.TYPE_VECTOR_POLYGON], optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.TEMPLATE_FIELD, tr("g_template_field"), "unit_code", self.TEMPLATE, compat.FIELD_ANY,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(self.SNAP, tr("g_snap"), compat.NUM_DOUBLE, 5.0, minValue=0.0)
        )
        self.addParameter(
            _advanced(
                QgsProcessingParameterNumber(self.MIN_AREA, tr("g_minarea"), compat.NUM_DOUBLE, 100.0, minValue=0.0)
            )
        )
        self.addParameter(QgsProcessingParameterBoolean(self.DISSOLVE, tr("g_dissolve"), True))
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, tr("g_out"), compat.TYPE_VECTOR_POLYGON)
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.DANGLES, tr("g_out_dangles"), compat.TYPE_VECTOR_POINT, optional=True, createByDefault=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):  # noqa: N802
        bsrc = self.parameterAsSource(parameters, self.BOUNDARIES, context)
        if bsrc is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.BOUNDARIES))
        crs = bsrc.sourceCrs()
        f_up = self.parameterAsString(parameters, self.UPPER, context)
        f_lo = self.parameterAsString(parameters, self.LOWER, context)
        f_side = existing_field(bsrc, self.parameterAsString(parameters, self.SIDE, context))

        boundaries = []
        for feat in bsrc.getFeatures():
            g = feat.geometry()
            if g is None or g.isEmpty():
                continue
            up, lo = feat[f_up], feat[f_lo]
            side = feat[f_side] if f_side else ""
            boundaries.append(
                BoundaryLine(
                    g,
                    None if is_null(up) else str(up),
                    None if is_null(lo) else str(lo),
                    "" if is_null(side) else str(side),
                )
            )

        faults = []
        fsrc = self.parameterAsSource(parameters, self.FAULTS, context)
        if fsrc is not None:
            xf = QgsCoordinateTransform(fsrc.sourceCrs(), crs, context.transformContext())
            for feat in fsrc.getFeatures():
                g = feat.geometry()
                if g is not None and not g.isEmpty():
                    g.transform(xf)
                    faults.append(g)

        unit_points = []
        psrc = self.parameterAsSource(parameters, self.UNIT_POINTS, context)
        f_unit = self.parameterAsString(parameters, self.UNIT_FIELD, context)
        f_unit = existing_field(psrc, f_unit) if psrc is not None else ""
        if psrc is not None and f_unit:
            xf = QgsCoordinateTransform(psrc.sourceCrs(), crs, context.transformContext())
            for feat in psrc.getFeatures():
                g = feat.geometry()
                if g is None or g.isEmpty() or is_null(feat[f_unit]):
                    continue
                g.transform(xf)
                p = g.asPoint() if not g.isMultipart() else g.asMultiPoint()[0]
                unit_points.append((p, str(feat[f_unit])))

        extent = self.parameterAsExtent(parameters, self.EXTENT, context, crs)
        if extent is None or extent.isNull() or extent.isEmpty():
            extent = QgsRectangle()
            extent.setNull()
            for g in [b.geom for b in boundaries] + faults:
                extent.combineExtentWith(g.boundingBox())
        if extent.isNull() or extent.isEmpty():
            raise QgsProcessingException(tr("msg_no_extent"))

        # template attributes / style
        template = self.parameterAsVectorLayer(parameters, self.TEMPLATE, context)
        f_tpl = self.parameterAsString(parameters, self.TEMPLATE_FIELD, context)
        tpl_attrs, renderer = {}, None
        f_tpl = existing_field(template, f_tpl) if template is not None else ""
        if template is not None and f_tpl:
            names = template.fields().names()
            for feat in template.getFeatures():
                code = feat[f_tpl]
                if is_null(code) or str(code) in tpl_attrs:
                    continue
                tpl_attrs[str(code)] = {n: feat[n] for n, _ in GEOLOGY_FIELDS if n in names}
            if template.renderer() is not None:
                renderer = template.renderer().clone()

        builder = GeologyBuilder(
            extent,
            snap_tol=self.parameterAsDouble(parameters, self.SNAP, context),
            min_area=self.parameterAsDouble(parameters, self.MIN_AREA, context),
            feedback=feedback,
        )
        polys = builder.build(
            boundaries, faults, unit_points, dissolve=self.parameterAsBool(parameters, self.DISSOLVE, context)
        )
        order = stratigraphic_order(boundaries)

        fields = geology_fields()
        sink, dest_id = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, compat.WKB_MULTIPOLYGON, crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        n_un = 0
        for p in polys:
            f = QgsFeature(fields)
            geom = QgsGeometry(p.geom)
            geom.convertToMultiType()
            f.setGeometry(geom)
            attrs = {"unit_code": p.unit, "unit_name": p.unit, "strat_order": order.get(p.unit), "kind": "sed"}
            if p.unit is None:
                n_un += 1
                attrs = {}
            for k, v in tpl_attrs.get(p.unit, {}).items():
                if not is_null(v):
                    attrs[k] = v
            for name, _ in GEOLOGY_FIELDS:
                f[name] = attrs.get(name)
            f["qa"] = p.qa
            f["area_m2"] = geom.area()
            sink.addFeature(f, compat.FAST_INSERT)

        dsink, dangle_id = self.parameterAsSink(
            parameters, self.DANGLES, context, QgsFields(), _point_wkb(), crs
        )
        if dsink is not None:
            for pt in builder.dangles:
                f = QgsFeature()
                f.setGeometry(QgsGeometry.fromPointXY(pt))
                dsink.addFeature(f, compat.FAST_INSERT)

        feedback.pushInfo(tr("msg_built", n=len(polys), u=n_un, d=len(builder.dangles)))
        if context.willLoadLayerOnCompletion(dest_id):
            context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(
                StylePostProcessor.create("geology", renderer)
            )
        result = {self.OUTPUT: dest_id}
        if dsink is not None:
            result[self.DANGLES] = dangle_id
        return result


def _point_wkb():
    return compat._enum("Qgis.WkbType.Point", "QgsWkbTypes.Point")
