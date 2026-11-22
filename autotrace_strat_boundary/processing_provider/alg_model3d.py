# -*- coding: utf-8 -*-
"""Processing algorithm: 3D geological model and geological sections."""
import math
import os
import time

import numpy as np
from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingOutputFile,
    QgsProcessingOutputString,
    QgsProcessingParameterBand,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsRectangle,
)
from qgis.PyQt.QtGui import QIcon

from .. import compat
from ..compat import is_null
from ..core import export3d, model_inputs as mi, model_outputs as mo, model_writer as mw
from ..core.geom_utils import line_parts, polygon_parts
from ..core.model3d import Fault, GeoModel, Unit
from ..i18n import current_language, tr
from .alg_trace import ICON_DIR, _advanced, existing_field

PALETTE = ["#f4a582", "#fddbc7", "#d1e5f0", "#92c5de", "#b8e186", "#fee08b", "#c2a5cf", "#e6f598",
           "#fdae61", "#abdda4", "#d6604d", "#4393c3"]


def _num(v, default=None):
    if is_null(v):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def unit_colors(layer, field):
    """unit code -> '#rrggbb' from a categorized renderer on *field*."""
    out = {}
    r = layer.renderer() if layer is not None else None
    if isinstance(r, QgsCategorizedSymbolRenderer) and r.classAttribute() == field:
        for c in r.categories():
            if c.symbol() is not None and not is_null(c.value()):
                out[str(c.value())] = c.symbol().color().name()
    return out


class BuildModel3DAlgorithm(QgsProcessingAlgorithm):
    GEOLOGY = "GEOLOGY"
    UNIT = "UNIT_FIELD"
    NAME = "NAME_FIELD"
    ORDER = "ORDER_FIELD"
    SERIES = "SERIES_FIELD"
    THICK = "THICK_FIELD"
    KIND = "KIND_FIELD"
    DEM = "DEM"
    BAND = "DEM_BAND"
    FAULTS = "FAULTS"
    F_DIP = "FAULT_DIP_FIELD"
    F_DIPDIR = "FAULT_DIPDIR_FIELD"
    F_DEFAULT_DIP = "FAULT_DEFAULT_DIP"
    ATT = "ATTITUDES"
    A_DIP = "ATT_DIP_FIELD"
    A_AZ = "ATT_AZIMUTH_FIELD"
    A_UNIT = "ATT_UNIT_FIELD"
    A_OVER = "ATT_OVERTURNED_FIELD"
    ATT2 = "ATTITUDES2"
    B_DIP = "ATT2_DIP_FIELD"
    B_AZ = "ATT2_AZIMUTH_FIELD"
    B_UNIT = "ATT2_UNIT_FIELD"
    B_OVER = "ATT2_OVERTURNED_FIELD"
    AZ_TYPE = "AZIMUTH_TYPE"
    SECTIONS = "SECTIONS"
    S_NAME = "SECTION_NAME_FIELD"
    CELL = "CELL_SIZE"
    DEPTH = "MODEL_DEPTH"
    VE = "VERTICAL_EXAGGERATION"
    USE_THICK = "USE_THICKNESS"
    CAD = "CAD_FORMATS"
    OPEN = "OPEN_VIEWER"
    OUTPUT = "OUTPUT_GPKG"
    VIEWER = "VIEWER_HTML"
    FILES = "CAD_FILES"

    CAD_OPTIONS = ["DXF (polyface mesh)", "OBJ + MTL", "STL"]

    def name(self):
        return "buildmodel3d"

    def displayName(self):  # noqa: N802
        return tr("alg_model3d")

    def group(self):
        return tr("group_name")

    def groupId(self):  # noqa: N802
        return "geomapping"

    def shortHelpString(self):  # noqa: N802
        return tr("help_model3d")

    def icon(self):
        return QIcon(os.path.join(ICON_DIR, "model3d.svg"))

    def createInstance(self):  # noqa: N802
        return BuildModel3DAlgorithm()

    # ------------------------------------------------------------------ parameters
    def initAlgorithm(self, config=None):  # noqa: N802
        P = self.addParameter
        P(QgsProcessingParameterVectorLayer(self.GEOLOGY, tr("m_geology"), [compat.TYPE_VECTOR_POLYGON]))
        P(QgsProcessingParameterField(self.UNIT, tr("m_unit"), "unit_code", self.GEOLOGY, compat.FIELD_ANY))
        P(QgsProcessingParameterField(self.ORDER, tr("m_order"), "strat_order", self.GEOLOGY, compat.FIELD_NUMERIC,
                                      optional=True))
        P(QgsProcessingParameterField(self.NAME, tr("m_name"), "unit_name", self.GEOLOGY, compat.FIELD_ANY,
                                      optional=True))
        P(QgsProcessingParameterField(self.SERIES, tr("m_series"), "series", self.GEOLOGY, compat.FIELD_NUMERIC,
                                      optional=True))
        P(QgsProcessingParameterField(self.THICK, tr("m_thick"), "thick_m", self.GEOLOGY, compat.FIELD_NUMERIC,
                                      optional=True))
        P(QgsProcessingParameterField(self.KIND, tr("m_kind"), "kind", self.GEOLOGY, compat.FIELD_ANY, optional=True))
        P(QgsProcessingParameterRasterLayer(self.DEM, tr("p_dem")))
        P(QgsProcessingParameterBand(self.BAND, tr("p_band"), 1, self.DEM))
        P(QgsProcessingParameterFeatureSource(self.FAULTS, tr("p_faults"), [compat.TYPE_VECTOR_LINE], optional=True))
        P(QgsProcessingParameterField(self.F_DIP, tr("m_fdip"), "dip", self.FAULTS, compat.FIELD_NUMERIC, optional=True))
        P(QgsProcessingParameterField(self.F_DIPDIR, tr("m_fdipdir"), "dip_dir", self.FAULTS, compat.FIELD_NUMERIC,
                                      optional=True))
        P(_advanced(QgsProcessingParameterNumber(self.F_DEFAULT_DIP, tr("m_fdefault"), compat.NUM_DOUBLE, 60.0,
                                                 minValue=1.0, maxValue=90.0)))
        P(QgsProcessingParameterFeatureSource(self.ATT, tr("m_att"), [compat.TYPE_VECTOR_POINT], optional=True))
        P(QgsProcessingParameterField(self.A_DIP, tr("p_dip"), "dip", self.ATT, compat.FIELD_NUMERIC, optional=True))
        P(QgsProcessingParameterField(self.A_AZ, tr("p_azimuth"), "dip_dir", self.ATT, compat.FIELD_NUMERIC,
                                      optional=True))
        P(QgsProcessingParameterField(self.A_UNIT, tr("m_aunit"), "unit_code", self.ATT, compat.FIELD_ANY, optional=True))
        P(QgsProcessingParameterField(self.A_OVER, tr("p_overturned"), "overturned", self.ATT, compat.FIELD_ANY,
                                      optional=True))
        P(QgsProcessingParameterFeatureSource(self.ATT2, tr("m_att2"), [compat.TYPE_VECTOR_POINT], optional=True))
        P(QgsProcessingParameterField(self.B_DIP, tr("p_dip"), "dip", self.ATT2, compat.FIELD_NUMERIC, optional=True))
        P(QgsProcessingParameterField(self.B_AZ, tr("p_azimuth"), "dip_dir", self.ATT2, compat.FIELD_NUMERIC,
                                      optional=True))
        P(QgsProcessingParameterField(self.B_UNIT, tr("m_aunit"), "unit_code_u", self.ATT2, compat.FIELD_ANY,
                                      optional=True))
        P(QgsProcessingParameterField(self.B_OVER, tr("p_overturned"), "overturned", self.ATT2, compat.FIELD_ANY,
                                      optional=True))
        P(QgsProcessingParameterEnum(self.AZ_TYPE, tr("p_azimuth_type"), [tr("opt_dipdir"), tr("opt_strike")],
                                     False, 0))
        P(QgsProcessingParameterFeatureSource(self.SECTIONS, tr("m_sections"), [compat.TYPE_VECTOR_LINE],
                                              optional=True))
        P(QgsProcessingParameterField(self.S_NAME, tr("m_sname"), "name", self.SECTIONS, compat.FIELD_ANY,
                                      optional=True))
        P(QgsProcessingParameterNumber(self.VE, tr("m_ve"), compat.NUM_DOUBLE, 1.0, minValue=0.1, maxValue=20.0))
        P(QgsProcessingParameterNumber(self.CELL, tr("m_cell"), compat.NUM_DOUBLE, 0.0, minValue=0.0))
        P(QgsProcessingParameterNumber(self.DEPTH, tr("m_depth"), compat.NUM_DOUBLE, 0.0, minValue=0.0))
        P(_advanced(QgsProcessingParameterBoolean(self.USE_THICK, tr("m_usethick"), False)))
        P(QgsProcessingParameterEnum(self.CAD, tr("m_cad"), self.CAD_OPTIONS, True, [0, 1], optional=True))
        P(QgsProcessingParameterBoolean(self.OPEN, tr("m_open"), True))
        P(QgsProcessingParameterFileDestination(self.OUTPUT, tr("m_out"), "GeoPackage (*.gpkg)"))
        self.addOutput(QgsProcessingOutputFile(self.VIEWER, tr("m_viewer")))
        self.addOutput(QgsProcessingOutputString(self.FILES, tr("m_files")))

    # ------------------------------------------------------------------ helpers
    def _attitudes(self, parameters, context, src_key, f_dip, f_az, f_unit, f_over, crs, topo, code_idx,
                   polys, pidx, strike, feedback):
        src = self.parameterAsSource(parameters, src_key, context)
        if src is None:
            return []
        dip_f = existing_field(src, self.parameterAsString(parameters, f_dip, context))
        az_f = existing_field(src, self.parameterAsString(parameters, f_az, context))
        if not dip_f or not az_f:
            feedback.pushWarning(tr("m_msg_nofields", layer=src.sourceName()))
            return []
        unit_f = existing_field(src, self.parameterAsString(parameters, f_unit, context))
        over_f = existing_field(src, self.parameterAsString(parameters, f_over, context))
        xf = QgsCoordinateTransform(src.sourceCrs(), crs, context.transformContext())
        out = []
        for feat in src.getFeatures():
            g = feat.geometry()
            dip, az = _num(feat[dip_f]), _num(feat[az_f])
            if g is None or g.isEmpty() or dip is None or az is None:
                continue
            g.transform(xf)
            p = g.asPoint() if not g.isMultipart() else g.asMultiPoint()[0]
            ov = False
            if over_f and not is_null(feat[over_f]):
                try:
                    ov = int(feat[over_f]) != 0
                except (TypeError, ValueError):
                    ov = str(feat[over_f]).strip().lower() in ("y", "yes", "true", "t")
            n = mi.attitude_normal(dip, az + (90.0 if strike else 0.0), ov)
            ui = code_idx.get(str(feat[unit_f])) if unit_f and not is_null(feat[unit_f]) else None
            if ui is None:
                ui = mi.unit_at(polys, pidx, p.x(), p.y())
            out.append((p.x(), p.y(), float(topo(p.x(), p.y())), n[0], n[1], n[2], ui))
        return out

    # ------------------------------------------------------------------ main
    def processAlgorithm(self, parameters, context, feedback):  # noqa: N802
        t_start = time.time()
        log = feedback.pushInfo
        geo = self.parameterAsVectorLayer(parameters, self.GEOLOGY, context)
        if geo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.GEOLOGY))
        crs = geo.crs()
        if crs.isGeographic():
            raise QgsProcessingException(tr("msg_geographic"))
        f_unit = self.parameterAsString(parameters, self.UNIT, context)
        fget = {k: existing_field(geo, self.parameterAsString(parameters, p, context))
                for k, p in (("name", self.NAME), ("order", self.ORDER), ("series", self.SERIES),
                             ("thick", self.THICK), ("kind", self.KIND))}
        colors = unit_colors(geo, f_unit)

        # units and polygons
        info, geoms = {}, []
        for feat in geo.getFeatures():
            code = feat[f_unit]
            g = feat.geometry()
            if is_null(code) or g is None or g.isEmpty():
                continue
            code = str(code)
            d = info.setdefault(code, {})
            for k, f in fget.items():
                if f and k not in d and not is_null(feat[f]):
                    d[k] = feat[f]
            for part in polygon_parts(g):
                geoms.append((part, code))
        if not info:
            raise QgsProcessingException(tr("m_msg_nounits"))
        if not fget["order"]:
            feedback.pushWarning(tr("m_msg_noorder"))
        codes = sorted(info, key=lambda c: (_num(info[c].get("order"), 1e9), c))
        units = []
        for i, c in enumerate(codes):
            d = info[c]
            units.append(Unit(c, str(d.get("name", c)), _num(d.get("order"), i + 1),
                              int(_num(d.get("series"), 1)), _num(d.get("thick")), d.get("kind", "sed"),
                              colors.get(c, PALETTE[i % len(PALETTE)])))
        code_idx = {u.code: i for i, u in enumerate(units)}
        polys = [(g, code_idx[c]) for g, c in geoms]
        pidx = mi.polygon_index(polys)

        # extent and DEM
        dem = self.parameterAsRasterLayer(parameters, self.DEM, context)
        if dem is None or dem.providerType() != "gdal":
            raise QgsProcessingException(tr("msg_dem_file"))
        ext = QgsRectangle(geo.extent())
        dem_ext = QgsCoordinateTransform(dem.crs(), crs, context.transformContext()).transformBoundingBox(dem.extent())
        ext = ext.intersect(dem_ext)
        if ext.isEmpty():
            raise QgsProcessingException(tr("m_msg_noextent"))
        extent = (ext.xMinimum(), ext.yMinimum(), ext.xMaximum(), ext.yMaximum())
        size = max(ext.width(), ext.height())
        cell = self.parameterAsDouble(parameters, self.CELL, context) or size / 40.0
        log(tr("m_msg_cell", cell="%.1f" % cell))
        topo = mi.read_topography(dem.source(), self.parameterAsInt(parameters, self.BAND, context), extent,
                                  None if dem.crs() == crs else crs.toWkt(), max_cells=400)
        depth = self.parameterAsDouble(parameters, self.DEPTH, context) or 0.35 * size
        zbase = topo.min - depth

        # faults
        faults, fault_geoms = [], []
        fsrc = self.parameterAsSource(parameters, self.FAULTS, context)
        if fsrc is not None:
            xf = QgsCoordinateTransform(fsrc.sourceCrs(), crs, context.transformContext())
            fd = existing_field(fsrc, self.parameterAsString(parameters, self.F_DIP, context))
            fa = existing_field(fsrc, self.parameterAsString(parameters, self.F_DIPDIR, context))
            dflt = self.parameterAsDouble(parameters, self.F_DEFAULT_DIP, context)
            names = [f.name() for f in fsrc.fields()]
            for k, feat in enumerate(fsrc.getFeatures()):
                g = feat.geometry()
                if g is None or g.isEmpty():
                    continue
                g.transform(xf)
                fault_geoms.append(g)
                nm = str(feat["name"]) if "name" in names and not is_null(feat["name"]) else "F%d" % (k + 1)
                dip = _num(feat[fd], dflt) if fd else dflt
                dd = _num(feat[fa]) if fa else None
                for j, tr_pts in enumerate(mi.trace_xy(g)):
                    if len(tr_pts) >= 2:
                        faults.append(Fault(nm if j == 0 else "%s_%d" % (nm, j + 1), tr_pts, dip, dd, topo))

        model = GeoModel(units, topo, extent, zbase, faults,
                         {code_idx[c]: [r for g, cc in geoms if cc == c for r in mi.rings_of(g)]
                          for c in codes if units[code_idx[c]].kind == "ign"}, log=log)
        strike = self.parameterAsEnum(parameters, self.AZ_TYPE, context) == 1
        grads = self._attitudes(parameters, context, self.ATT, self.A_DIP, self.A_AZ, self.A_UNIT, self.A_OVER,
                                crs, topo, code_idx, polys, pidx, strike, feedback)
        grads += self._attitudes(parameters, context, self.ATT2, self.B_DIP, self.B_AZ, self.B_UNIT, self.B_OVER,
                                 crs, topo, code_idx, polys, pidx, strike, feedback)
        contacts = mi.contacts_from_geology(polys, fault_geoms, topo, cell * 0.75, cell * 0.5)
        log(tr("m_msg_inputs", u=len(units), c=len(contacts), a=len(grads), f=len(faults)))
        feedback.setProgress(5)
        if feedback.isCanceled():
            return {}
        try:
            model.build(contacts, grads, self.parameterAsBool(parameters, self.USE_THICK, context))
        except ValueError as e:
            raise QgsProcessingException(str(e))
        for w in model.warnings:
            feedback.pushWarning(w)
        feedback.setProgress(20)

        # surface agreement with the map (quality figure)
        xs = np.linspace(extent[0], extent[2], 80)[1:-1]
        ys = np.linspace(extent[1], extent[3], 80)[1:-1]
        X, Y = np.meshgrid(xs, ys)
        X, Y = X.ravel(), Y.ravel()
        U = model.unit_index(X, Y, topo(X, Y) - 0.5, clip_topo=False)
        truth = np.array([mi.unit_at(polys, pidx, x, y) for x, y in zip(X, Y)], dtype=object)
        truth = np.array([-9 if t is None else t for t in truth], dtype=int)
        agree = float(((U == truth) & (truth >= 0)).sum()) / max(1, int((truth >= 0).sum())) * 100.0
        log(tr("m_msg_agree", p="%.1f" % agree))

        # geometry
        solids = mo.unit_solids(model, cell, progress=lambda f: feedback.setProgress(20 + 30 * f))
        if feedback.isCanceled():
            return {}
        view_cell = max(cell, size / 40.0)
        view_solids = solids if view_cell == cell else mo.unit_solids(model, view_cell)
        hz = mo.horizons(model, cell)
        fplanes = mo.fault_planes(model, cell)
        tv, tf, tu = mo.terrain(model, n=150)
        feedback.setProgress(60)

        # sections
        sections = []
        ssrc = self.parameterAsSource(parameters, self.SECTIONS, context)
        if ssrc is not None:
            xf = QgsCoordinateTransform(ssrc.sourceCrs(), crs, context.transformContext())
            sn = existing_field(ssrc, self.parameterAsString(parameters, self.S_NAME, context))
            for k, feat in enumerate(ssrc.getFeatures()):
                g = feat.geometry()
                if g is None or g.isEmpty():
                    continue
                g.transform(xf)
                base = str(feat[sn]) if sn and not is_null(feat[sn]) else chr(ord("A") + k % 26)
                for j, part in enumerate(line_parts(g)):
                    pts = [(p.x(), p.y()) for p in part.asPolyline()]
                    if len(pts) >= 2:
                        sections.append(mo.Section(base if j == 0 else "%s%d" % (base, j + 1), pts))
        if not sections:
            mean = None
            if grads:
                hx = sum(g[3] for g in grads)
                hy = sum(g[4] for g in grads)
                if abs(hx) + abs(hy) > 1e-9:
                    mean = math.degrees(math.atan2(hx, hy)) % 360
            sections.append(mo.auto_section(model, mean))
            log(tr("m_msg_autosec"))
        ve = self.parameterAsDouble(parameters, self.VE, context)
        sec_res = [mo.section_raster(model, s) for s in sections]
        feedback.setProgress(70)

        # ------------------------------------------------------------ GeoPackage
        out_path = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if not out_path.lower().endswith(".gpkg"):
            out_path += ".gpkg"
        root = os.path.splitext(out_path)[0]
        W = mw.GpkgWriter(out_path, crs)
        ucol = [u.color for u in units]
        rows = []
        for ui, (v, f) in solids.items():
            u = units[ui]
            T = v[f]
            vol = float(abs(np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum()) / 6.0)
            rows.append((mw.geom_from_wkb(mw.triangles_wkb(v, f)),
                         [u.code, u.name, u.order, u.series, u.kind, u.color, len(f), vol]))
        W.add("units_3d", mw.wkb_type("mpz"), [("unit_code", "s"), ("unit_name", "s"), ("strat_order", "d"),
                                              ("series", "i"), ("kind", "s"), ("color", "s"), ("n_tri", "i"),
                                              ("volume_m3", "d")], rows)
        W.add("horizons_3d", mw.wkb_type("mpz"), [("series", "i"), ("unit_below", "s"), ("unit_above", "s"),
                                                 ("level", "d"), ("color", "s")],
              [(mw.geom_from_wkb(mw.triangles_wkb(v, f)),
                [sid, units[b].code, units[a].code, lv, units[a].color]) for sid, b, a, lv, v, f in hz])
        W.add("faults_3d", mw.wkb_type("mpz"), [("name", "s"), ("dip", "d")],
              [(mw.geom_from_wkb(mw.triangles_wkb(v, f)), [fl.name, fl.dip]) for fl, v, f in fplanes])
        trows = []
        for ui in sorted(set(tu.tolist())):
            if ui < 0:
                continue
            m = tu == ui
            trows.append((mw.geom_from_wkb(mw.triangles_wkb(tv, tf[m])), [units[ui].code, units[ui].color]))
        W.add("terrain_3d", mw.wkb_type("mpz"), [("unit_code", "s"), ("color", "s")], trows)

        # section sheet below the map
        H = ext.height()
        gap = 0.08 * max(H, size * 0.5)
        y_cursor = extent[1] - gap
        sl_rows, su_rows, sp_rows, sf_rows, fr_rows, lb_rows, fence_rows, viewer_secs = [], [], [], [], [], [], [], []
        for sec, res in zip(sections, sec_res):
            h = (res["ztop"] - res["zbase"]) * ve
            sy0 = y_cursor - h - gap * 0.35
            sx0 = extent[0]
            sl_rows.append((QgsGeometry.fromPolylineXY([QgsPointXY(*p) for p in sec.pts]),
                            [sec.name, sec.title, sec.start, sec.end, sec.length]))
            per_unit = {}
            for ui, g in mw.section_polygons(res, sx0, sy0, ve):
                if ui < 0:
                    continue
                su_rows.append((g, [sec.name, units[ui].code, units[ui].name, units[ui].color]))
                per_unit.setdefault(ui, []).extend(mw.sheet_to_world(g, sec, sx0, sy0, res["zbase"], ve, res["ds"] * 4))
            for ui, gl in per_unit.items():
                fence_rows.append((QgsGeometry.collectGeometry(gl), [sec.name, units[ui].code, units[ui].color]))
            prof = res["profile"]
            sp_rows.append((QgsGeometry.fromPolylineXY(
                [QgsPointXY(sx0 + s, sy0 + (z - res["zbase"]) * ve) for s, z in prof]), [sec.name]))
            for flt, run in res["faults"]:
                sf_rows.append((QgsGeometry.fromPolylineXY(
                    [QgsPointXY(sx0 + s, sy0 + (z - res["zbase"]) * ve) for s, z in run]), [sec.name, flt.name]))
            title = tr("m_sec_title", a=sec.title, ve="%g" % ve)
            lines, labels = mw.section_annotations(sec, res, sx0, sy0, ve, title)
            fr_rows += [(g, [sec.name, k]) for g, k in lines]
            lb_rows += [(QgsGeometry.fromPointXY(p), [sec.name, t, k]) for p, t, k in labels]
            cx0, cy0 = (extent[0] + extent[2]) / 2.0, (extent[1] + extent[3]) / 2.0
            u_of = [float(c) / sec.length for c in sec.cum]
            viewer_secs.append(dict(name=sec.name, ztop=res["ztop"], zbase=res["zbase"],
                                    pts=[[float(p[0] - cx0), float(p[1] - cy0), u] for p, u in zip(sec.pts, u_of)],
                                    img=mw.section_image(res, ucol)))
            y_cursor = sy0 - gap
        W.add("section_lines", mw.wkb_type("ls"), [("name", "s"), ("title", "s"), ("start", "s"), ("end", "s"),
                                                  ("length_m", "d")], sl_rows)
        W.add("section_units", mw.wkb_type("mp"), [("section", "s"), ("unit_code", "s"), ("unit_name", "s"),
                                                  ("color", "s")],
              [(QgsGeometry(g).makeValid() if not g.isGeosValid() else g, a) for g, a in su_rows])
        W.add("section_profile", mw.wkb_type("ls"), [("section", "s")], sp_rows)
        W.add("section_faults", mw.wkb_type("ls"), [("section", "s"), ("fault", "s")], sf_rows)
        W.add("section_frame", mw.wkb_type("ls"), [("section", "s"), ("kind", "s")], fr_rows)
        W.add("section_labels", mw.wkb_type("pt"), [("section", "s"), ("text", "s"), ("kind", "s")], lb_rows)
        W.add("section_fences_3d", mw.wkb_type("mpz"), [("section", "s"), ("unit_code", "s"), ("color", "s")],
              fence_rows)
        info_rows = [("crs", crs.authid()), ("extent", "%.3f,%.3f,%.3f,%.3f" % extent), ("zbase", "%.2f" % zbase),
                     ("cell_size", "%.2f" % cell), ("vertical_exaggeration", "%g" % ve),
                     ("surface_agreement_pct", "%.1f" % agree), ("contacts", str(len(contacts))),
                     ("attitudes", str(len(grads))), ("faults", str(len(faults)))]
        for S in model.series:
            info_rows.append(("series_%s_levels" % S.sid, ", ".join("%.2f" % v for v in S.levels if v > -1e11)))
        for k, w in enumerate(model.warnings):
            info_rows.append(("warning_%d" % (k + 1), w))
        W.add("model_info", mw.wkb_type("none"), [("key", "s"), ("value", "s")], [(None, r) for r in info_rows])
        feedback.setProgress(85)

        # ------------------------------------------------------------ CAD
        files = [out_path]
        meshes = [dict(name="unit_%s" % units[ui].code, color=units[ui].color, verts=v, faces=f)
                  for ui, (v, f) in solids.items()]
        meshes += [dict(name="fault_%s" % fl.name, color="#d62728", verts=v, faces=f) for fl, v, f in fplanes]
        meshes += [dict(name="horizon_%s_%s" % (units[b].code, units[a].code), color=units[a].color, verts=v, faces=f)
                   for sid, b, a, lv, v, f in hz]
        meshes.append(dict(name="terrain", color="#c8b48c", verts=tv, faces=tf))
        cad = self.parameterAsEnums(parameters, self.CAD, context)
        polylines = []
        for sec in sections:
            z = topo(sec.pts[:, 0], sec.pts[:, 1])
            polylines.append(("section_%s" % sec.title, "#000000",
                              [(float(x), float(y), float(zz)) for (x, y), zz in zip(sec.pts, z)]))
        if 0 in cad:
            files += export3d.write_dxf(root + ".dxf", meshes, polylines)
        if 1 in cad:
            files += export3d.write_obj(root + ".obj", meshes)
        if 2 in cad:
            files += export3d.write_stl(root + ".stl", [m for m in meshes if m["name"].startswith("unit_")])
        feedback.setProgress(92)

        # ------------------------------------------------------------ viewer
        center = ((extent[0] + extent[2]) / 2.0, (extent[1] + extent[3]) / 2.0)
        vmesh = [mw.viewer_mesh("solid", units[ui].name, units[ui].color, v, f, center, unit=units[ui].code)
                 for ui, (v, f) in view_solids.items()]
        vmesh += [mw.viewer_mesh("horizon", "%s/%s" % (units[a].code, units[b].code), units[a].color, v, f, center)
                  for sid, b, a, lv, v, f in hz]
        vmesh += [mw.viewer_mesh("fault", fl.name, "#d62728", v, f, center) for fl, v, f in fplanes]
        tcols = np.array([mw.hex_rgb(units[u].color) if u >= 0 else (200, 200, 200) for u in tu], dtype=np.uint8)
        vmesh.append(mw.viewer_mesh("terrain", "terrain", "#ffffff", tv, tf, center, face_colors=tcols))
        lang = current_language()
        data = dict(
            title=tr("m_viewer_title"), subtitle="%s · %s · %s %.1f%%" % (geo.name(), crs.authid(),
                                                                         tr("m_agree_short"), agree),
            units=[dict(code=u.code, name=u.name, color=u.color) for u in reversed(units)],
            meshes=vmesh, sections=viewer_secs, warnings=model.warnings[:3], lang=lang,
            extent=[extent[0] - center[0], extent[1] - center[1], extent[2] - center[0], extent[3] - center[1],
                    zbase, topo.max],
            text={k: tr("v_" + k) for k in ("h_units", "h_layers", "h_ve", "h_cut", "h_view", "top", "iso", "shot",
                                             "hint", "terrain", "sections", "faults", "horizons")},
        )
        viewer = mw.write_viewer(root + "_viewer.html", data)
        files.append(viewer)
        feedback.setProgress(100)
        log(tr("m_msg_done", s="%.0f" % (time.time() - t_start), n=len(files)))
        for f in files:
            log("  " + f)
        self._post = dict(gpkg=out_path, viewer=viewer, open=self.parameterAsBool(parameters, self.OPEN, context),
                          layers=list(W.layers))
        return {self.OUTPUT: out_path, self.VIEWER: viewer, self.FILES: ";".join(files)}

    def postProcessAlgorithm(self, context, feedback):  # noqa: N802
        post = getattr(self, "_post", None)
        if not post:
            return {}
        from .model_layers import load_model_layers

        try:
            load_model_layers(post["gpkg"], context.project() or None, post["layers"])
        except Exception as e:  # never fail the run because of styling
            feedback.reportError(str(e))
        if post["open"]:
            from qgis.PyQt.QtCore import QUrl
            from qgis.PyQt.QtGui import QDesktopServices

            QDesktopServices.openUrl(QUrl.fromLocalFile(post["viewer"]))
        return {}
