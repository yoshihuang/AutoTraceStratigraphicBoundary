# -*- coding: utf-8 -*-
"""QGIS 3.x (Qt5) / QGIS 4.x (Qt6) compatibility helpers.

All enum lookups go through this module so the rest of the plugin never has
to care which API generation is running.
"""
from qgis.core import Qgis, QgsField

_USE_METATYPE = Qgis.QGIS_VERSION_INT >= 33800  # QgsField(name, QMetaType.Type) since 3.38
if _USE_METATYPE:
    from qgis.PyQt.QtCore import QMetaType

    _T_DOUBLE = QMetaType.Type.Double
    _T_INT = QMetaType.Type.Int
    _T_STRING = QMetaType.Type.QString

if not _USE_METATYPE:  # QGIS 3.x older than 3.38
    from qgis.PyQt.QtCore import QVariant

    _T_DOUBLE = QVariant.Double
    _T_INT = QVariant.Int
    _T_STRING = QVariant.String


def _enum(new_path, old_path):
    """Resolve 'Qgis.X.Y' first, then the legacy dotted path."""
    import qgis.core as qc

    for path in (new_path, old_path):
        if not path:
            continue
        obj = qc
        try:
            for part in path.split("."):
                obj = getattr(obj, part)
            return obj
        except AttributeError:
            continue
    raise AttributeError("Cannot resolve enum %s / %s" % (new_path, old_path))


# processing source types
TYPE_VECTOR_POINT = _enum("Qgis.ProcessingSourceType.VectorPoint", "QgsProcessing.TypeVectorPoint")
TYPE_VECTOR_LINE = _enum("Qgis.ProcessingSourceType.VectorLine", "QgsProcessing.TypeVectorLine")
TYPE_VECTOR_POLYGON = _enum("Qgis.ProcessingSourceType.VectorPolygon", "QgsProcessing.TypeVectorPolygon")
TYPE_VECTOR_ANY = _enum("Qgis.ProcessingSourceType.VectorAnyGeometry", "QgsProcessing.TypeVectorAnyGeometry")

# number parameter types
NUM_DOUBLE = _enum("Qgis.ProcessingNumberParameterType.Double", "QgsProcessingParameterNumber.Double")
NUM_INT = _enum("Qgis.ProcessingNumberParameterType.Integer", "QgsProcessingParameterNumber.Integer")

# field parameter data types
FIELD_ANY = _enum("Qgis.ProcessingFieldParameterDataType.Any", "QgsProcessingParameterField.Any")
FIELD_NUMERIC = _enum("Qgis.ProcessingFieldParameterDataType.Numeric", "QgsProcessingParameterField.Numeric")

# wkb types
WKB_LINESTRING = _enum("Qgis.WkbType.LineString", "QgsWkbTypes.LineString")
WKB_MULTILINESTRING = _enum("Qgis.WkbType.MultiLineString", "QgsWkbTypes.MultiLineString")
WKB_MULTIPOLYGON = _enum("Qgis.WkbType.MultiPolygon", "QgsWkbTypes.MultiPolygon")

GEOM_POINT = _enum("Qgis.GeometryType.Point", "QgsWkbTypes.PointGeometry")
GEOM_LINE = _enum("Qgis.GeometryType.Line", "QgsWkbTypes.LineGeometry")
GEOM_POLYGON = _enum("Qgis.GeometryType.Polygon", "QgsWkbTypes.PolygonGeometry")

FAST_INSERT = _enum("QgsFeatureSink.Flag.FastInsert", "QgsFeatureSink.FastInsert")


def field_double(name):
    return QgsField(name, _T_DOUBLE)


def field_int(name):
    return QgsField(name, _T_INT)


def field_string(name, length=0):
    f = QgsField(name, _T_STRING)
    if length:
        f.setLength(length)
    return f


def geometry_type(geom):
    """Geometry type of a QgsGeometry (works on 3.x and 4.x)."""
    return geom.type()


def is_null(value):
    """True for None and QVariant NULL."""
    if value is None:
        return True
    try:
        from qgis.PyQt.QtCore import QVariant

        if isinstance(value, QVariant) and value.isNull():
            return True
    except Exception:
        pass
    return str(value) == "NULL"
