# -*- coding: utf-8 -*-
"""Lightweight multi-language support.

Language resolution:
  1. plugin setting  ``AutoTraceStratBoundary/language``  (en / zh_TW / zh_CN / ja)
  2. "auto" (default) -> the QGIS user-interface locale
  3. fallback English

To add a language: add its code to LANGUAGES, add a column to every entry
of STRINGS and add ``help/<code>/index.html``.
"""
from qgis.core import QgsApplication, QgsSettings
from qgis.PyQt.QtCore import QLocale

SETTINGS_KEY = "AutoTraceStratBoundary/language"

LANGUAGES = [
    ("en", "English"),
    ("zh_TW", "繁體中文"),
    ("zh_CN", "简体中文"),
    ("ja", "日本語"),
]
_CODES = [c for c, _ in LANGUAGES]


def _from_locale(loc):
    loc = (loc or "").replace("-", "_")
    low = loc.lower()
    if low.startswith("zh"):
        if any(t in low for t in ("tw", "hk", "mo", "hant")):
            return "zh_TW"
        return "zh_CN"
    if low.startswith("ja"):
        return "ja"
    return "en"


def qgis_language():
    """Language of the QGIS user interface.

    QgsApplication.locale() only returns the language part ("zh"), which
    cannot tell Traditional from Simplified Chinese, so the full locale is
    taken from the QGIS override setting or the system locale first.
    """
    s = QgsSettings()
    override = str(s.value("locale/overrideFlag", False)).lower() in ("true", "1")
    candidates = []
    if override:
        candidates.append(s.value("locale/userLocale", "") or "")
    candidates.append(QLocale.system().name())
    candidates.append(QgsApplication.locale() or "")
    app_lang = candidates[-1].split("_")[0].lower()
    for loc in candidates:
        if not loc:
            continue
        # the system locale only counts if it has the same language as the UI
        if app_lang and loc.split("_")[0].lower() != app_lang:
            continue
        return _from_locale(loc)
    return _from_locale(candidates[-1])


def preferred_setting():
    v = QgsSettings().value(SETTINGS_KEY, "auto")
    return v if v in _CODES else "auto"


def set_preferred(code):
    QgsSettings().setValue(SETTINGS_KEY, code if code in _CODES else "auto")


def current_language():
    pref = preferred_setting()
    return qgis_language() if pref == "auto" else pref


def tr(key, **kw):
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(current_language()) or entry.get("en") or key
    return text.format(**kw) if kw else text


# fmt: off
STRINGS = {
    # ---------------------------------------------------------------- plugin / menu
    "plugin_name": {
        "en": "AutoTrace Stratigraphic Boundary", "zh_TW": "地層邊界自動追蹤",
        "zh_CN": "地层边界自动追踪", "ja": "地層境界自動トレース"},
    "provider_name": {
        "en": "AutoTrace Strat Boundary", "zh_TW": "地層邊界自動追蹤",
        "zh_CN": "地层边界自动追踪", "ja": "地層境界自動トレース"},
    "group_name": {
        "en": "Geological mapping", "zh_TW": "地質圖繪製",
        "zh_CN": "地质图绘制", "ja": "地質図作成"},
    "act_trace": {
        "en": "Trace predicted boundary lines…", "zh_TW": "繪製地層邊界預判線…",
        "zh_CN": "绘制地层边界预判线…", "ja": "地層境界予測線を作成…"},
    "act_geology": {
        "en": "Build geological map…", "zh_TW": "產生地質圖…",
        "zh_CN": "生成地质图…", "ja": "地質図を作成…"},
    "act_sample": {
        "en": "Download sample project and data…", "zh_TW": "下載範例專案與資料…",
        "zh_CN": "下载示例工程与数据…", "ja": "サンプルプロジェクトとデータをダウンロード…"},
    "act_help": {
        "en": "Principle and user guide", "zh_TW": "繪製原理與操作說明",
        "zh_CN": "绘制原理与操作说明", "ja": "作図原理と操作説明"},
    "act_language": {
        "en": "Language", "zh_TW": "語言 Language", "zh_CN": "语言 Language", "ja": "言語 Language"},
    "lang_auto": {
        "en": "Follow QGIS", "zh_TW": "跟隨 QGIS", "zh_CN": "跟随 QGIS", "ja": "QGIS に従う"},

    # ---------------------------------------------------------------- sample data
    "sample_choose_dir": {
        "en": "Choose a folder for the sample project", "zh_TW": "選擇範例專案的存放資料夾",
        "zh_CN": "选择示例工程的存放文件夹", "ja": "サンプルプロジェクトの保存先フォルダを選択"},
    "sample_exists": {
        "en": "The folder already exists:\n{path}\n\nOverwrite its files?",
        "zh_TW": "資料夾已存在：\n{path}\n\n要覆蓋其中的檔案嗎？",
        "zh_CN": "文件夹已存在：\n{path}\n\n要覆盖其中的文件吗？",
        "ja": "フォルダは既に存在します：\n{path}\n\nファイルを上書きしますか？"},
    "sample_done": {
        "en": "Sample data saved to:\n{path}\n\nOpen the sample project now?",
        "zh_TW": "範例資料已儲存至：\n{path}\n\n現在開啟範例專案嗎？",
        "zh_CN": "示例数据已保存至：\n{path}\n\n现在打开示例工程吗？",
        "ja": "サンプルデータを保存しました：\n{path}\n\n今すぐサンプルプロジェクトを開きますか？"},
    "sample_error": {
        "en": "Could not save the sample data:\n{err}", "zh_TW": "無法儲存範例資料：\n{err}",
        "zh_CN": "无法保存示例数据：\n{err}", "ja": "サンプルデータを保存できませんでした：\n{err}"},

    # ---------------------------------------------------------------- help dialog
    "help_title": {
        "en": "Principle and user guide", "zh_TW": "繪製原理與操作說明",
        "zh_CN": "绘制原理与操作说明", "ja": "作図原理と操作説明"},
    "help_browser": {
        "en": "Open in web browser", "zh_TW": "以瀏覽器開啟", "zh_CN": "用浏览器打开", "ja": "ブラウザで開く"},
    "close": {"en": "Close", "zh_TW": "關閉", "zh_CN": "关闭", "ja": "閉じる"},

    # ---------------------------------------------------------------- trace algorithm
    "alg_trace": {
        "en": "Trace predicted stratigraphic boundaries", "zh_TW": "繪製地層邊界預判線",
        "zh_CN": "绘制地层边界预判线", "ja": "地層境界予測線の作成"},
    "p_points": {
        "en": "Boundary outcrop points (e.g. Stratigraphic_Boundary)",
        "zh_TW": "地層邊界露頭點位圖層（如 Stratigraphic_Boundary）",
        "zh_CN": "地层边界露头点位图层（如 Stratigraphic_Boundary）",
        "ja": "地層境界露頭点レイヤ（例：Stratigraphic_Boundary）"},
    "p_dip": {"en": "Dip field", "zh_TW": "傾角欄位", "zh_CN": "倾角字段", "ja": "傾斜フィールド"},
    "p_azimuth": {
        "en": "Dip direction (or strike) field", "zh_TW": "傾向（或走向）欄位",
        "zh_CN": "倾向（或走向）字段", "ja": "傾斜方位（または走向）フィールド"},
    "p_azimuth_type": {
        "en": "Azimuth field contains", "zh_TW": "方位欄位內容", "zh_CN": "方位字段内容", "ja": "方位フィールドの内容"},
    "opt_dipdir": {"en": "Dip direction", "zh_TW": "傾向", "zh_CN": "倾向", "ja": "傾斜方位"},
    "opt_strike": {
        "en": "Strike (right-hand rule)", "zh_TW": "走向（右手定則）",
        "zh_CN": "走向（右手定则）", "ja": "走向（右手則）"},
    "p_upper": {
        "en": "Upper unit code field", "zh_TW": "上層地層代號欄位",
        "zh_CN": "上层地层代号字段", "ja": "上位層コードフィールド"},
    "p_lower": {
        "en": "Lower unit code field", "zh_TW": "下層地層代號欄位",
        "zh_CN": "下层地层代号字段", "ja": "下位層コードフィールド"},
    "p_overturned": {
        "en": "Overturned flag field (optional, 1 = overturned)", "zh_TW": "倒轉層欄位（選填，1 = 倒轉）",
        "zh_CN": "倒转层字段（可选，1 = 倒转）", "ja": "逆転フラグフィールド（任意、1 = 逆転）"},
    "p_dem": {"en": "Topography DEM", "zh_TW": "地形 DEM", "zh_CN": "地形 DEM", "ja": "地形 DEM"},
    "p_band": {"en": "DEM band", "zh_TW": "DEM 波段", "zh_CN": "DEM 波段", "ja": "DEM バンド"},
    "p_faults": {
        "en": "Faults / structural lines (optional)", "zh_TW": "斷層／構造線（選填）",
        "zh_CN": "断层／构造线（可选）", "ja": "断層・構造線（任意）"},
    "p_method": {"en": "Method", "zh_TW": "方法", "zh_CN": "方法", "ja": "手法"},
    "opt_blend": {
        "en": "Join points of the same boundary (blended planes)",
        "zh_TW": "同一邊界的點位相接（混合層面）",
        "zh_CN": "同一边界的点位相接（混合层面）",
        "ja": "同じ境界の点をつなぐ（平面の混合）"},
    "opt_individual": {
        "en": "Each point on its own plane", "zh_TW": "各點位獨立（單一層面）",
        "zh_CN": "各点位独立（单一层面）", "ja": "各点を個別の平面で"},
    "p_power": {
        "en": "Blending power (inverse-distance exponent)", "zh_TW": "混合權重次方（反距離指數）",
        "zh_CN": "混合权重次方（反距离指数）", "ja": "混合の重み指数（逆距離のべき）"},
    "p_maxdist": {
        "en": "Maximum extension from the points (0 = unlimited)", "zh_TW": "由點位最大延伸距離（0 = 不限）",
        "zh_CN": "由点位最大延伸距离（0 = 不限）", "ja": "点からの最大延長距離（0 = 無制限）"},
    "p_gap": {
        "en": "Join loose ends of the same boundary closer than (0 = off)",
        "zh_TW": "同一邊界線段端點相接的最大間距（0 = 不相接）",
        "zh_CN": "同一边界线段端点相接的最大间距（0 = 不相接）",
        "ja": "同じ境界の端点を接続する最大間隔（0 = 接続しない）"},
    "p_keepall": {
        "en": "Keep branches that pass no outcrop point", "zh_TW": "保留未通過露頭點的分支",
        "zh_CN": "保留未通过露头点的分支", "ja": "露頭点を通らない分岐も残す"},
    "p_minlen": {"en": "Minimum line length", "zh_TW": "最短線長", "zh_CN": "最短线长", "ja": "最小線長"},
    "p_out_lines": {
        "en": "Predicted boundary lines", "zh_TW": "地層邊界預判線",
        "zh_CN": "地层边界预判线", "ja": "地層境界予測線"},
    "msg_geographic": {
        "en": "The DEM uses a geographic CRS. Use a projected CRS in metres.",
        "zh_TW": "DEM 為地理座標系統，請改用以公尺為單位的投影座標系統。",
        "zh_CN": "DEM 为地理坐标系，请改用以米为单位的投影坐标系。",
        "ja": "DEM が地理座標系です。メートル単位の投影座標系を使用してください。"},
    "msg_dem_file": {
        "en": "The DEM must be a GDAL raster file.", "zh_TW": "DEM 必須是 GDAL 可讀取的網格檔。",
        "zh_CN": "DEM 必须是 GDAL 可读取的栅格文件。", "ja": "DEM は GDAL で読めるラスタファイルである必要があります。"},
    "msg_point_skipped": {
        "en": "Point {fid} skipped: missing dip / azimuth / unit codes.",
        "zh_TW": "點位 {fid} 略過：缺少傾角、方位或地層代號。",
        "zh_CN": "点位 {fid} 跳过：缺少倾角、方位或地层代号。",
        "ja": "点 {fid} をスキップ：傾斜・方位・地層コードが不足しています。"},
    "msg_traced": {
        "en": "{n} predicted boundary lines created.", "zh_TW": "已產生 {n} 條地層邊界預判線。",
        "zh_CN": "已生成 {n} 条地层边界预判线。", "ja": "{n} 本の地層境界予測線を作成しました。"},

    # ---------------------------------------------------------------- geology algorithm
    "alg_geology": {
        "en": "Build geological map from boundaries and faults", "zh_TW": "由地層邊界線與斷層產生地質圖",
        "zh_CN": "由地层边界线与断层生成地质图", "ja": "地層境界線と断層から地質図を作成"},
    "g_bnd": {
        "en": "Boundary lines (edited predictions)", "zh_TW": "地層邊界線（編修後的預判線）",
        "zh_CN": "地层边界线（编辑后的预判线）", "ja": "地層境界線（編集後の予測線）"},
    "g_side": {
        "en": "Upper-unit side field (L / R, optional)", "zh_TW": "上層所在側欄位（L／R，選填）",
        "zh_CN": "上层所在侧字段（L／R，可选）", "ja": "上位層の側フィールド（L／R、任意）"},
    "g_extent": {
        "en": "Map extent (empty = extent of the lines)", "zh_TW": "圖幅範圍（空白 = 線段範圍）",
        "zh_CN": "图幅范围（空白 = 线段范围）", "ja": "図郭範囲（空欄 = 線の範囲）"},
    "g_unitpts": {
        "en": "Unit sample points (optional, e.g. bedding)", "zh_TW": "地層代號點位（選填，如 bedding）",
        "zh_CN": "地层代号点位（可选，如 bedding）", "ja": "地層コード点（任意、例：bedding）"},
    "g_unitfield": {
        "en": "Unit code field of the sample points", "zh_TW": "點位的地層代號欄位",
        "zh_CN": "点位的地层代号字段", "ja": "点の地層コードフィールド"},
    "g_template": {
        "en": "Unit attribute / style template (optional, e.g. an old geology layer)",
        "zh_TW": "地層屬性與樣式範本（選填，如原有 geology 圖層）",
        "zh_CN": "地层属性与样式模板（可选，如原有 geology 图层）",
        "ja": "地層属性・スタイルのテンプレート（任意、例：既存の geology）"},
    "g_template_field": {
        "en": "Unit code field of the template", "zh_TW": "範本的地層代號欄位",
        "zh_CN": "模板的地层代号字段", "ja": "テンプレートの地層コードフィールド"},
    "g_snap": {
        "en": "Snapping tolerance for line ends", "zh_TW": "線段端點接合容許距離",
        "zh_CN": "线段端点接合容许距离", "ja": "線端のスナップ許容距離"},
    "g_minarea": {
        "en": "Merge unassigned slivers smaller than (area)", "zh_TW": "併入鄰區的未判定碎片面積上限",
        "zh_CN": "并入邻区的未判定碎片面积上限", "ja": "隣接区域に統合する未判定の小片の面積上限"},
    "g_dissolve": {
        "en": "Dissolve polygons by unit", "zh_TW": "依地層合併多邊形",
        "zh_CN": "按地层合并多边形", "ja": "地層ごとにポリゴンを統合"},
    "g_out": {"en": "Geology", "zh_TW": "地質圖 geology", "zh_CN": "地质图 geology", "ja": "地質図 geology"},
    "g_out_dangles": {
        "en": "Unclosed boundary ends (check)", "zh_TW": "未閉合端點（檢核用）",
        "zh_CN": "未闭合端点（检核用）", "ja": "閉じていない境界端点（チェック用）"},
    "msg_no_extent": {
        "en": "Cannot determine the map extent.", "zh_TW": "無法決定圖幅範圍。",
        "zh_CN": "无法确定图幅范围。", "ja": "図郭範囲を決定できません。"},
    "msg_built": {
        "en": "{n} geology polygons created ({u} unassigned, {d} unclosed ends).",
        "zh_TW": "已產生 {n} 個地質區（未判定 {u} 個，未閉合端點 {d} 個）。",
        "zh_CN": "已生成 {n} 个地质区（未判定 {u} 个，未闭合端点 {d} 个）。",
        "ja": "{n} 個の地質区を作成しました（未判定 {u}、未閉合端点 {d}）。"},

    # ---------------------------------------------------------------- algorithm help
    "help_trace": {
        "en": (
            "<p>Predicts where each stratigraphic boundary crops out, by the <b>structure-contour method</b>: "
            "the boundary plane through each outcrop point (dip, dip direction, DEM elevation) is intersected "
            "with the topography and the line is followed to both sides of the point.</p>"
            "<ul><li>Points with the same upper and lower unit codes in the same fault block are joined into one "
            "line (blended planes).</li>"
            "<li>Lines stop on faults and end on the fault line.</li>"
            "<li>The output is a temporary layer: edit it, then save it.</li></ul>"
            "<p>Field <i>upper_side</i> (L/R) records on which side of the line, looking along it, the upper unit "
            "crops out. It is used by <i>Build geological map</i>.</p>"),
        "zh_TW": (
            "<p>依<b>構造等高線原理</b>預測地層邊界的露頭位置：以露頭點的傾角、傾向及 DEM 高程建立地層面，"
            "求地層面與地形面的交線，並由點位往兩側延伸。</p>"
            "<ul><li>同一斷塊內、上層與下層代號相同的點位，以混合層面連成同一條線（端點相接）。</li>"
            "<li>預判線遇到斷層即停止，並終止於斷層線上。</li>"
            "<li>輸出為暫存圖層，請編修後另存。</li></ul>"
            "<p>欄位 <i>upper_side</i>（L／R）記錄沿線前進方向時上層位於左側或右側，供「產生地質圖」使用。</p>"),
        "zh_CN": (
            "<p>依<b>构造等高线原理</b>预测地层边界的露头位置：以露头点的倾角、倾向及 DEM 高程建立地层面，"
            "求地层面与地形面的交线，并由点位往两侧延伸。</p>"
            "<ul><li>同一断块内、上层与下层代号相同的点位，以混合层面连成同一条线（端点相接）。</li>"
            "<li>预判线遇到断层即停止，并终止于断层线上。</li>"
            "<li>输出为临时图层，请编辑后另存。</li></ul>"
            "<p>字段 <i>upper_side</i>（L／R）记录沿线前进方向时上层位于左侧或右侧，供“生成地质图”使用。</p>"),
        "ja": (
            "<p><b>構造等高線法</b>で地層境界の露頭位置を予測します。露頭点の傾斜・傾斜方位と DEM 標高から"
            "境界面を作り、地形面との交線を点の両側へ追跡します。</p>"
            "<ul><li>同じ断層ブロック内で上位・下位コードが同じ点は、平面の混合により 1 本の線でつながります。</li>"
            "<li>予測線は断層で止まり、断層線上で終わります。</li>"
            "<li>出力は一時レイヤです。編集後に保存してください。</li></ul>"
            "<p><i>upper_side</i>（L／R）は線の進行方向に対して上位層が左右どちらにあるかを示し、"
            "「地質図を作成」で使われます。</p>"),
    },
    "help_geology": {
        "en": (
            "<p>Builds a geological map (unit polygons) from your edited boundary lines and the faults.</p>"
            "<ol><li>Boundary lines, faults and the map frame are noded and turned into polygons. Line ends "
            "within the snapping tolerance of another line are joined.</li>"
            "<li>Each polygon gets the upper or lower unit code of the boundaries around it, using "
            "<i>upper_side</i> (L/R). Lines without it pass a known unit across to the other side.</li>"
            "<li>Optional unit sample points (e.g. bedding with unit_code) take priority.</li>"
            "<li>Field <i>qa</i>: ok / conflict / propagated / unassigned. Check the "
            "<i>unclosed ends</i> output for gaps.</li></ol>"),
        "zh_TW": (
            "<p>由編修後的地層邊界線與斷層產生地質圖（地層多邊形）。</p>"
            "<ol><li>地層邊界線、斷層與圖框經節點化後組成多邊形；端點距其他線段在容許距離內者自動接合。</li>"
            "<li>依 <i>upper_side</i>（L／R）判定每個多邊形為邊界的上層或下層；沒有此欄位的線，"
            "則由已知鄰區跨越邊界推定另一側。</li>"
            "<li>可選用地層代號點位（如含 unit_code 的 bedding），其判定優先。</li>"
            "<li>欄位 <i>qa</i>：ok／conflict（判定衝突）／propagated（推定）／unassigned（未判定）。"
            "請以「未閉合端點」輸出檢查缺口。</li></ol>"),
        "zh_CN": (
            "<p>由编辑后的地层边界线与断层生成地质图（地层多边形）。</p>"
            "<ol><li>地层边界线、断层与图框经节点化后组成多边形；端点距其他线段在容许距离内者自动接合。</li>"
            "<li>依 <i>upper_side</i>（L／R）判定每个多边形为边界的上层或下层；没有此字段的线，"
            "则由已知邻区跨越边界推定另一侧。</li>"
            "<li>可选用地层代号点位（如含 unit_code 的 bedding），其判定优先。</li>"
            "<li>字段 <i>qa</i>：ok／conflict（判定冲突）／propagated（推定）／unassigned（未判定）。"
            "请以“未闭合端点”输出检查缺口。</li></ol>"),
        "ja": (
            "<p>編集済みの地層境界線と断層から地質図（地層ポリゴン）を作成します。</p>"
            "<ol><li>境界線・断層・図郭をノード化してポリゴン化します。許容距離内の線端は自動で接続します。</li>"
            "<li><i>upper_side</i>（L／R）により各ポリゴンを上位層／下位層に割り当てます。"
            "この値がない線では、既知の隣接区域から反対側を推定します。</li>"
            "<li>地層コード点（unit_code を持つ bedding など）を指定すると優先されます。</li>"
            "<li><i>qa</i>：ok／conflict（矛盾）／propagated（推定）／unassigned（未判定）。"
            "「閉じていない境界端点」で隙間を確認してください。</li></ol>"),
    },
}
# fmt: on
