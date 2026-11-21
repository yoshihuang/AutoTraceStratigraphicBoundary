# -*- coding: utf-8 -*-
"""Processing algorithm: trace predicted stratigraphic boundary lines."""
import os

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsFields,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBand,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterLayer,
)
from qgis.PyQt.QtGui import QIcon

from .. import compat
from ..compat import is_null
from ..core.tracer import METHOD_BLEND, METHOD_INDIVIDUAL, BoundaryTracer, DemGrid, OutcropPoint
from ..i18n import tr
from .styles import StylePostProcessor

ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")


def _advanced(param):
    flag = compat._enum("Qgis.ProcessingParameterFlag.Advanced", "QgsProcessingParameterDefinition.FlagAdvanced")
    param.setFlags(param.flags() | flag)
    return param


def existing_field(source, name):
    """*name* if the source has that field, else '' (optional fields with a default name)."""
    return name if name and source.fields().indexOf(name) >= 0 else ""


def output_fields():
    fields = QgsFields()
    fields.append(compat.field_int("bnd_id"))
    fields.append(compat.field_string("unit_u", 20))
    fields.append(compat.field_string("unit_d", 20))
    fields.append(compat.field_string("upper_side", 1))
    fields.append(compat.field_int("block_id"))
    fields.append(compat.field_int("n_pts"))
    fields.append(compat.field_string("pt_ids", 254))
    fields.append(compat.field_string("method", 12))
    fields.append(compat.field_double("length_m"))
    return fields


class TraceBoundaryAlgorithm(QgsProcessingAlgorithm):
    POINTS = "POINTS"
    DIP = "DIP_FIELD"
    AZIMUTH = "AZIMUTH_FIELD"
    AZIMUTH_TYPE = "AZIMUTH_TYPE"
    UPPER = "UPPER_FIELD"
    LOWER = "LOWER_FIELD"
    OVERTURNED = "OVERTURNED_FIELD"
    DEM = "DEM"
    BAND = "DEM_BAND"
    FAULTS = "FAULTS"
    METHOD = "METHOD"
    POWER = "POWER"
    MAX_DIST = "MAX_DISTANCE"
    GAP = "CONNECT_GAP"
    KEEP_ALL = "KEEP_ALL_BRANCHES"
    MIN_LEN = "MIN_LENGTH"
    OUTPUT = "OUTPUT"

    def name(self):
        return "tracestratboundary"

    def displayName(self):  # noqa: N802
        return tr("alg_trace")

    def group(self):
        return tr("group_name")

    def groupId(self):  # noqa: N802
        return "geomapping"

    def shortHelpString(self):  # noqa: N802
        return tr("help_trace")

    def icon(self):
        return QIcon(os.path.join(ICON_DIR, "trace.svg"))

    def createInstance(self):  # noqa: N802
        return TraceBoundaryAlgorithm()

    def initAlgorithm(self, config=None):  # noqa: N802
        self.addParameter(
            QgsProcessingParameterFeatureSource(self.POINTS, tr("p_points"), [compat.TYPE_VECTOR_POINT])
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.DIP, tr("p_dip"), "dip", self.POINTS, compat.FIELD_NUMERIC
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.AZIMUTH, tr("p_azimuth"), "dip_dir", self.POINTS, compat.FIELD_NUMERIC
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.AZIMUTH_TYPE, tr("p_azimuth_type"), [tr("opt_dipdir"), tr("opt_strike")], False, 0
            )
        )
        self.addParameter(
            QgsProcessingParameterField(self.UPPER, tr("p_upper"), "unit_code_u", self.POINTS, compat.FIELD_ANY)
        )
        self.addParameter(
            QgsProcessingParameterField(self.LOWER, tr("p_lower"), "unit_code_d", self.POINTS, compat.FIELD_ANY)
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.OVERTURNED, tr("p_overturned"), "overturned", self.POINTS, compat.FIELD_ANY, optional=True
            )
        )
        self.addParameter(QgsProcessingParameterRasterLayer(self.DEM, tr("p_dem")))
        self.addParameter(QgsProcessingParameterBand(self.BAND, tr("p_band"), 1, self.DEM))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.FAULTS, tr("p_faults"), [compat.TYPE_VECTOR_LINE], optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD, tr("p_method"), [tr("opt_blend"), tr("opt_individual")], False, METHOD_BLEND
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.GAP, tr("p_gap"), compat.NUM_DOUBLE, 100.0, minValue=0.0
            )
        )
        self.addParameter(
            _advanced(
                QgsProcessingParameterNumber(
                    self.POWER, tr("p_power"), compat.NUM_DOUBLE, 4.0, minValue=0.5, maxValue=12.0
                )
            )
        )
        self.addParameter(
            _advanced(
                QgsProcessingParameterNumber(
                    self.MAX_DIST, tr("p_maxdist"), compat.NUM_DOUBLE, 0.0, minValue=0.0
                )
            )
        )
        self.addParameter(
            _advanced(QgsProcessingParameterBoolean(self.KEEP_ALL, tr("p_keepall"), False))
        )
        self.addParameter(
            _advanced(
                QgsProcessingParameterNumber(
                    self.MIN_LEN, tr("p_minlen"), compat.NUM_DOUBLE, 0.0, minValue=0.0
                )
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, tr("p_out_lines"), compat.TYPE_VECTOR_LINE)
        )

    def processAlgorithm(self, parameters, context, feedback):  # noqa: N802
        source = self.parameterAsSource(parameters, self.POINTS, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POINTS))
        dem_layer = self.parameterAsRasterLayer(parameters, self.DEM, context)
        if dem_layer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.DEM))
        if dem_layer.providerType() != "gdal":
            raise QgsProcessingException(tr("msg_dem_file"))
        if dem_layer.crs().isGeographic():
            raise QgsProcessingException(tr("msg_geographic"))
        crs = dem_layer.crs()

        f_dip = self.parameterAsString(parameters, self.DIP, context)
        f_az = self.parameterAsString(parameters, self.AZIMUTH, context)
        strike = self.parameterAsEnum(parameters, self.AZIMUTH_TYPE, context) == 1
        f_up = self.parameterAsString(parameters, self.UPPER, context)
        f_lo = self.parameterAsString(parameters, self.LOWER, context)
        f_ov = existing_field(source, self.parameterAsString(parameters, self.OVERTURNED, context))

        xf = QgsCoordinateTransform(source.sourceCrs(), crs, context.transformContext())
        points = []
        for feat in source.getFeatures():
            g = feat.geometry()
            if g is None or g.isEmpty():
                continue
            vals = [feat[f_dip], feat[f_az], feat[f_up], feat[f_lo]]
            if any(is_null(v) for v in vals):
                feedback.pushWarning(tr("msg_point_skipped", fid=feat.id()))
                continue
            g.transform(xf)
            p = g.asPoint() if not g.isMultipart() else g.asMultiPoint()[0]
            az = float(vals[1]) + (90.0 if strike else 0.0)
            ov = False
            if f_ov and not is_null(feat[f_ov]):
                try:
                    ov = int(feat[f_ov]) != 0
                except (TypeError, ValueError):
                    ov = str(feat[f_ov]).strip().lower() in ("y", "yes", "true", "t")
            points.append(
                OutcropPoint(feat.id(), p.x(), p.y(), float(vals[0]), az, str(vals[2]), str(vals[3]), ov)
            )

        faults = []
        fsrc = self.parameterAsSource(parameters, self.FAULTS, context)
        if fsrc is not None:
            fx = QgsCoordinateTransform(fsrc.sourceCrs(), crs, context.transformContext())
            for feat in fsrc.getFeatures():
                g = feat.geometry()
                if g is None or g.isEmpty():
                    continue
                g.transform(fx)
                faults.append(g)

        dem = DemGrid(dem_layer.source(), self.parameterAsInt(parameters, self.BAND, context))
        tracer = BoundaryTracer(
            dem,
            faults,
            method=METHOD_INDIVIDUAL if self.parameterAsEnum(parameters, self.METHOD, context) == 1 else METHOD_BLEND,
            power=self.parameterAsDouble(parameters, self.POWER, context),
            max_distance=self.parameterAsDouble(parameters, self.MAX_DIST, context),
            connect_gap=self.parameterAsDouble(parameters, self.GAP, context),
            keep_all_branches=self.parameterAsBool(parameters, self.KEEP_ALL, context),
            min_length=self.parameterAsDouble(parameters, self.MIN_LEN, context),
            feedback=feedback,
        )
        results = tracer.run(points)

        fields = output_fields()
        sink, dest_id = self.parameterAsSink(
            parameters, self.OUTPUT, context, fields, compat.WKB_LINESTRING, crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        for i, r in enumerate(results, 1):
            f = QgsFeature(fields)
            f.setGeometry(r.geom)
            f.setAttributes(
                [
                    i,
                    r.upper,
                    r.lower,
                    r.upper_side,
                    r.block,
                    len(r.points),
                    ",".join(str(p.fid) for p in r.points)[:254],
                    r.method,
                    r.geom.length(),
                ]
            )
            sink.addFeature(f, compat.FAST_INSERT)
        feedback.pushInfo(tr("msg_traced", n=len(results)))

        if context.willLoadLayerOnCompletion(dest_id):
            context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(StylePostProcessor.create("trace"))
        return {self.OUTPUT: dest_id}
