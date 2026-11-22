# -*- coding: utf-8 -*-
"""UI strings of the 3D model / section tool (merged into i18n.STRINGS)."""

# fmt: off
STRINGS = {
    "act_model3d": {
        "en": "Build 3D geological model and sections…", "zh_TW": "產生 3D 地質模型與地質剖面…",
        "zh_CN": "生成 3D 地质模型与地质剖面…", "ja": "3D 地質モデルと地質断面を作成…"},
    "alg_model3d": {
        "en": "Build 3D geological model and sections", "zh_TW": "產生 3D 地質模型與地質剖面",
        "zh_CN": "生成 3D 地质模型与地质剖面", "ja": "3D 地質モデルと地質断面の作成"},
    "m_geology": {
        "en": "Geological map (geology polygons)", "zh_TW": "地質圖（geology 多邊形）",
        "zh_CN": "地质图（geology 多边形）", "ja": "地質図（geology ポリゴン）"},
    "m_unit": {"en": "Unit code field", "zh_TW": "地層代號欄位", "zh_CN": "地层代号字段", "ja": "地層コードフィールド"},
    "m_order": {
        "en": "Stratigraphic order field (1 = oldest)", "zh_TW": "層序欄位（1 = 最老）",
        "zh_CN": "层序字段（1 = 最老）", "ja": "層序フィールド（1 = 最古）"},
    "m_name": {"en": "Unit name field", "zh_TW": "地層名稱欄位", "zh_CN": "地层名称字段", "ja": "地層名フィールド"},
    "m_series": {
        "en": "Series field (higher = above an unconformity)", "zh_TW": "層系欄位（數字大＝不整合之上）",
        "zh_CN": "层系字段（数字大＝不整合之上）", "ja": "層群フィールド（大きい＝不整合の上）"},
    "m_thick": {"en": "Thickness field (m)", "zh_TW": "厚度欄位（m）", "zh_CN": "厚度字段（m）", "ja": "層厚フィールド（m）"},
    "m_kind": {
        "en": "Kind field (sed / ign)", "zh_TW": "岩類欄位（sed 沉積／ign 火成）",
        "zh_CN": "岩类字段（sed 沉积／ign 火成）", "ja": "岩種フィールド（sed 堆積／ign 火成）"},
    "m_fdip": {"en": "Fault dip field", "zh_TW": "斷層傾角欄位", "zh_CN": "断层倾角字段", "ja": "断層傾斜フィールド"},
    "m_fdipdir": {
        "en": "Fault dip direction field", "zh_TW": "斷層傾向欄位", "zh_CN": "断层倾向字段", "ja": "断層傾斜方位フィールド"},
    "m_fdefault": {
        "en": "Fault dip when no value (°)", "zh_TW": "無資料時的斷層傾角（°）",
        "zh_CN": "无数据时的断层倾角（°）", "ja": "値がない場合の断層傾斜（°）"},
    "m_att": {
        "en": "Attitude points 1 (optional, e.g. bedding)", "zh_TW": "位態點位 1（選填，如 bedding）",
        "zh_CN": "产状点位 1（可选，如 bedding）", "ja": "姿勢点 1（任意、例：bedding）"},
    "m_att2": {
        "en": "Attitude points 2 (optional, e.g. Stratigraphic_Boundary)",
        "zh_TW": "位態點位 2（選填，如 Stratigraphic_Boundary）",
        "zh_CN": "产状点位 2（可选，如 Stratigraphic_Boundary）",
        "ja": "姿勢点 2（任意、例：Stratigraphic_Boundary）"},
    "m_aunit": {
        "en": "Unit code field of the point (optional)", "zh_TW": "點位所屬地層欄位（選填）",
        "zh_CN": "点位所属地层字段（可选）", "ja": "点の地層コードフィールド（任意）"},
    "m_sections": {
        "en": "Section lines (optional; empty = one automatic section)", "zh_TW": "剖面線（選填；空白＝自動一條）",
        "zh_CN": "剖面线（可选；空白＝自动一条）", "ja": "断面線（任意；空欄＝自動で 1 本）"},
    "m_sname": {"en": "Section name field", "zh_TW": "剖面名稱欄位", "zh_CN": "剖面名称字段", "ja": "断面名フィールド"},
    "m_ve": {
        "en": "Section vertical exaggeration", "zh_TW": "剖面垂直誇大倍率", "zh_CN": "剖面垂直夸大倍率", "ja": "断面の垂直誇張"},
    "m_cell": {
        "en": "Model cell size (map units, 0 = auto)", "zh_TW": "模型網格大小（圖面單位，0＝自動）",
        "zh_CN": "模型网格大小（地图单位，0＝自动）", "ja": "モデルのセルサイズ（地図単位、0＝自動）"},
    "m_depth": {
        "en": "Model depth below the lowest ground (0 = auto)", "zh_TW": "模型底部深度（自最低地表起算，0＝自動）",
        "zh_CN": "模型底部深度（自最低地表起算，0＝自动）", "ja": "最低地表からのモデル深さ（0＝自動）"},
    "m_usethick": {
        "en": "Use the unit thicknesses as interface spacing", "zh_TW": "以地層厚度作為界面間距",
        "zh_CN": "以地层厚度作为界面间距", "ja": "層厚を境界面の間隔に使う"},
    "m_cad": {"en": "3D CAD formats", "zh_TW": "3D CAD 格式", "zh_CN": "3D CAD 格式", "ja": "3D CAD 形式"},
    "m_open": {
        "en": "Open the 3D viewer when finished", "zh_TW": "完成後開啟 3D 檢視器",
        "zh_CN": "完成后打开 3D 查看器", "ja": "完了後に 3D ビューアを開く"},
    "m_out": {
        "en": "Output GeoPackage (model and sections)", "zh_TW": "輸出 GeoPackage（模型與剖面）",
        "zh_CN": "输出 GeoPackage（模型与剖面）", "ja": "出力 GeoPackage（モデルと断面）"},
    "m_viewer": {"en": "3D viewer (HTML)", "zh_TW": "3D 檢視器（HTML）", "zh_CN": "3D 查看器（HTML）", "ja": "3D ビューア（HTML）"},
    "m_files": {"en": "Written files", "zh_TW": "輸出檔案", "zh_CN": "输出文件", "ja": "出力ファイル"},
    "m_msg_nofields": {
        "en": "{layer}: dip / azimuth fields not found, layer skipped.", "zh_TW": "{layer}：找不到傾角／方位欄位，已略過。",
        "zh_CN": "{layer}：找不到倾角／方位字段，已跳过。", "ja": "{layer}：傾斜／方位フィールドがないためスキップしました。"},
    "m_msg_nounits": {
        "en": "The geology layer has no units.", "zh_TW": "地質圖沒有地層資料。",
        "zh_CN": "地质图没有地层数据。", "ja": "地質図に地層がありません。"},
    "m_msg_noorder": {
        "en": "No stratigraphic order field: units are ordered by code.", "zh_TW": "未指定層序欄位：依地層代號排序。",
        "zh_CN": "未指定层序字段：按地层代号排序。", "ja": "層序フィールドがないため、地層コード順にしました。"},
    "m_msg_noextent": {
        "en": "The geology layer and the DEM do not overlap.", "zh_TW": "地質圖與 DEM 範圍沒有重疊。",
        "zh_CN": "地质图与 DEM 范围没有重叠。", "ja": "地質図と DEM の範囲が重なっていません。"},
    "m_msg_cell": {
        "en": "Model cell size: {cell}", "zh_TW": "模型網格大小：{cell}", "zh_CN": "模型网格大小：{cell}",
        "ja": "セルサイズ：{cell}"},
    "m_msg_inputs": {
        "en": "Units {u}, contact points {c}, attitudes {a}, faults {f}",
        "zh_TW": "地層 {u}、界面點 {c}、位態 {a}、斷層 {f}",
        "zh_CN": "地层 {u}、界面点 {c}、产状 {a}、断层 {f}", "ja": "地層 {u}、境界点 {c}、姿勢 {a}、断層 {f}"},
    "m_msg_agree": {
        "en": "Model units at the ground surface agree with the map: {p}%",
        "zh_TW": "模型地表地層與地質圖一致率：{p}%", "zh_CN": "模型地表地层与地质图一致率：{p}%",
        "ja": "地表でのモデルと地質図の一致率：{p}%"},
    "m_msg_autosec": {
        "en": "No section lines: one section across the strike was added.",
        "zh_TW": "未提供剖面線：已自動產生一條垂直走向的剖面。",
        "zh_CN": "未提供剖面线：已自动生成一条垂直走向的剖面。",
        "ja": "断面線がないため、走向に直交する断面を 1 本作成しました。"},
    "m_sec_title": {
        "en": "Section {a}  (V.E. x{ve})", "zh_TW": "地質剖面 {a}（垂直誇大 ×{ve}）",
        "zh_CN": "地质剖面 {a}（垂直夸大 ×{ve}）", "ja": "地質断面 {a}（垂直誇張 ×{ve}）"},
    "m_msg_done": {
        "en": "Finished in {s} s, {n} files:", "zh_TW": "完成（{s} 秒），輸出 {n} 個檔案：",
        "zh_CN": "完成（{s} 秒），输出 {n} 个文件：", "ja": "完了（{s} 秒）、{n} ファイル："},
    "m_viewer_title": {"en": "3D geological model", "zh_TW": "3D 地質模型", "zh_CN": "3D 地质模型", "ja": "3D 地質モデル"},
    "m_agree_short": {"en": "map agreement", "zh_TW": "地表一致率", "zh_CN": "地表一致率", "ja": "地表一致率"},
    "m_group": {
        "en": "3D model · {name}", "zh_TW": "3D 地質模型・{name}", "zh_CN": "3D 地质模型・{name}",
        "ja": "3D 地質モデル・{name}"},
    "v_h_units": {"en": "Units", "zh_TW": "地層", "zh_CN": "地层", "ja": "地層"},
    "v_h_layers": {"en": "Layers", "zh_TW": "圖層", "zh_CN": "图层", "ja": "レイヤ"},
    "v_h_ve": {"en": "Vertical exaggeration", "zh_TW": "垂直誇大", "zh_CN": "垂直夸大", "ja": "垂直誇張"},
    "v_h_cut": {"en": "Cut (east / north)", "zh_TW": "切割（東側／北側）", "zh_CN": "切割（东侧／北侧）", "ja": "切断（東側／北側）"},
    "v_h_view": {"en": "View", "zh_TW": "視角", "zh_CN": "视角", "ja": "視点"},
    "v_top": {"en": "Top", "zh_TW": "俯視", "zh_CN": "俯视", "ja": "真上"},
    "v_iso": {"en": "Oblique", "zh_TW": "斜視", "zh_CN": "斜视", "ja": "斜め"},
    "v_shot": {"en": "Save PNG", "zh_TW": "存成 PNG", "zh_CN": "存为 PNG", "ja": "PNG 保存"},
    "v_hint": {
        "en": "Left drag: rotate · right drag: pan · wheel: zoom", "zh_TW": "左鍵拖曳：旋轉・右鍵拖曳：平移・滾輪：縮放",
        "zh_CN": "左键拖动：旋转・右键拖动：平移・滚轮：缩放", "ja": "左ドラッグ：回転・右ドラッグ：移動・ホイール：拡大縮小"},
    "v_terrain": {"en": "Terrain (geological map)", "zh_TW": "地形（地質圖）", "zh_CN": "地形（地质图）", "ja": "地形（地質図）"},
    "v_sections": {"en": "Geological sections", "zh_TW": "地質剖面", "zh_CN": "地质剖面", "ja": "地質断面"},
    "v_faults": {"en": "Faults", "zh_TW": "斷層", "zh_CN": "断层", "ja": "断層"},
    "v_horizons": {"en": "Interfaces", "zh_TW": "地層界面", "zh_CN": "地层界面", "ja": "地層境界面"},
    "help_model3d": {
        "en": (
            "<p>Builds a <b>3D geological model</b> and <b>geological sections</b> from the geological map, the DEM, "
            "attitudes and faults (implicit potential-field method, as in geomap-workbench).</p>"
            "<ul><li>Contacts between adjacent units are taken from the map and placed on the DEM; "
            "attitudes control the dip of the surfaces at depth; faults offset them.</li>"
            "<li>Series (unconformities), thicknesses and intrusive (ign) units are supported.</li>"
            "<li>Output GeoPackage: units_3d, horizons_3d, faults_3d, terrain_3d, section_fences_3d (3D), "
            "and the section sheet drawn below the map (section_units, section_profile, section_faults, "
            "section_frame, section_labels), section_lines, model_info.</li>"
            "<li>3D CAD: DXF (polyface mesh), OBJ + MTL, STL; plus an offline 3D viewer (HTML).</li></ul>"),
        "zh_TW": (
            "<p>由地質圖、DEM、位態與斷層建立 <b>3D 地質模型</b> 與 <b>地質剖面</b>"
            "（隱式位勢場法，與 geomap-workbench 相同）。</p>"
            "<ul><li>相鄰地層的界線取自地質圖並置於 DEM 上；位態控制地層面在地下的傾斜；斷層使地層錯移。</li>"
            "<li>支援層系（不整合）、地層厚度與火成侵入體（ign）。</li>"
            "<li>輸出 GeoPackage：units_3d、horizons_3d、faults_3d、terrain_3d、section_fences_3d（3D），"
            "以及繪於地質圖下方的剖面圖（section_units、section_profile、section_faults、section_frame、"
            "section_labels）、section_lines、model_info。</li>"
            "<li>3D CAD：DXF（polyface mesh）、OBJ + MTL、STL；另產生離線 3D 檢視器（HTML）。</li></ul>"),
        "zh_CN": (
            "<p>由地质图、DEM、产状与断层建立 <b>3D 地质模型</b> 与 <b>地质剖面</b>"
            "（隐式位势场法，与 geomap-workbench 相同）。</p>"
            "<ul><li>相邻地层的界线取自地质图并置于 DEM 上；产状控制地层面在地下的倾斜；断层使地层错移。</li>"
            "<li>支持层系（不整合）、地层厚度与火成侵入体（ign）。</li>"
            "<li>输出 GeoPackage：units_3d、horizons_3d、faults_3d、terrain_3d、section_fences_3d（3D），"
            "以及绘于地质图下方的剖面图（section_units、section_profile、section_faults、section_frame、"
            "section_labels）、section_lines、model_info。</li>"
            "<li>3D CAD：DXF（polyface mesh）、OBJ + MTL、STL；另生成离线 3D 查看器（HTML）。</li></ul>"),
        "ja": (
            "<p>地質図・DEM・姿勢・断層から <b>3D 地質モデル</b> と <b>地質断面</b> を作成します"
            "（陰的ポテンシャル場法、geomap-workbench と同じ）。</p>"
            "<ul><li>隣接地層の境界を地質図から取り DEM 上に置き、姿勢で地下の傾斜を、断層で変位を与えます。</li>"
            "<li>層群（不整合）、層厚、火成貫入岩（ign）に対応します。</li>"
            "<li>出力 GeoPackage：units_3d、horizons_3d、faults_3d、terrain_3d、section_fences_3d（3D）、"
            "地質図の下に描く断面図（section_units、section_profile、section_faults、section_frame、"
            "section_labels）、section_lines、model_info。</li>"
            "<li>3D CAD：DXF（polyface mesh）、OBJ + MTL、STL。オフラインの 3D ビューア（HTML）も作成します。</li></ul>"),
    },
}
# fmt: on
