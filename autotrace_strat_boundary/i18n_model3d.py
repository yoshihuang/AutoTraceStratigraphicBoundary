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

# 1.2: folds and explicit output files
STRINGS.update({
    "m_folds": {
        "en": "Fold axial traces (optional, e.g. fold_axes)", "zh_TW": "褶皺軸跡（選填，如 fold_axes）",
        "zh_CN": "褶皱轴迹（可选，如 fold_axes）", "ja": "褶曲軸跡（任意、例：fold_axes）"},
    "m_ftrend": {
        "en": "Fold axis trend field (empty = along the trace)", "zh_TW": "褶皺軸趨向欄位（空白＝沿軸跡方向）",
        "zh_CN": "褶皱轴趋向字段（空白＝沿轴迹方向）", "ja": "褶曲軸のトレンドフィールド（空欄＝軸跡の方向）"},
    "m_fplunge": {
        "en": "Fold axis plunge field (empty = 0)", "zh_TW": "褶皺軸傾沒角欄位（空白＝0）",
        "zh_CN": "褶皱轴倾伏角字段（空白＝0）", "ja": "褶曲軸のプランジフィールド（空欄＝0）"},
    "m_ftype": {
        "en": "Fold type field (anticline / syncline)", "zh_TW": "褶皺類型欄位（背斜／向斜）",
        "zh_CN": "褶皱类型字段（背斜／向斜）", "ja": "褶曲の種類フィールド（背斜／向斜）"},
    "m_fname": {"en": "Fold name field", "zh_TW": "褶皺名稱欄位", "zh_CN": "褶皱名称字段", "ja": "褶曲名フィールド"},
    "m_out_dxf": {
        "en": "3D CAD file – DXF (polyface meshes)", "zh_TW": "3D CAD 檔案－DXF（polyface mesh）",
        "zh_CN": "3D CAD 文件－DXF（polyface mesh）", "ja": "3D CAD ファイル－DXF（polyface mesh）"},
    "m_out_obj": {
        "en": "3D CAD file – OBJ + MTL", "zh_TW": "3D CAD 檔案－OBJ + MTL",
        "zh_CN": "3D CAD 文件－OBJ + MTL", "ja": "3D CAD ファイル－OBJ + MTL"},
    "m_out_stl": {
        "en": "3D CAD file – STL (one file per unit)", "zh_TW": "3D CAD 檔案－STL（每個地層一個檔案）",
        "zh_CN": "3D CAD 文件－STL（每个地层一个文件）", "ja": "3D CAD ファイル－STL（地層ごとに 1 ファイル）"},
    "m_out_html": {
        "en": "3D viewer (HTML)", "zh_TW": "3D 檢視器（HTML）", "zh_CN": "3D 查看器（HTML）", "ja": "3D ビューア（HTML）"},
    "m_msg_folds": {
        "en": "Folds {n}: {p} hinge constraints added", "zh_TW": "褶皺 {n} 條：加入 {p} 個樞紐位態條件",
        "zh_CN": "褶皱 {n} 条：加入 {p} 个枢纽产状条件", "ja": "褶曲 {n} 本：ヒンジ条件 {p} 点を追加"},
    "m_done_bar": {
        "en": "{n} files written to {folder}", "zh_TW": "已輸出 {n} 個檔案至 {folder}",
        "zh_CN": "已输出 {n} 个文件至 {folder}", "ja": "{n} 個のファイルを {folder} に出力しました"},
    "m_open_folder": {"en": "Open folder", "zh_TW": "開啟資料夾", "zh_CN": "打开文件夹", "ja": "フォルダを開く"},
    "v_folds": {"en": "Fold axes", "zh_TW": "褶皺軸", "zh_CN": "褶皱轴", "ja": "褶曲軸"},
})
for _lang, _text in (
    ("en", "<p><b>Folds</b>: along every fold axial trace the bedding contains the fold axis (trend / plunge), "
           "so the trace adds attitude constraints at the hinge.</p>"
           "<p><b>Output</b>: everything goes to one folder (prefix.gpkg, prefix_viewer.html, the ticked CAD formats, "
           "one prefix_section_<name>.qgz per section, each section in its own GeoPackage layers with x = distance from 0 and y = elevation). The first section opens in a new QGIS window; the current project is not changed.</p>"),
    ("zh_TW", "<p><b>褶皺</b>：褶皺樞紐處的地層面包含褶皺軸（趨向／傾沒角），因此軸跡會在樞紐加入位態條件。</p>"
              "<p><b>輸出</b>：所有成果輸出至同一資料夾（前綴.gpkg、前綴_viewer.html、勾選的 CAD 格式、每個剖面一個 前綴_section_<剖面名>.qgz，各剖面在 GeoPackage 中各自成圖層，x＝自 0 起算的距離、y＝高程）；"
              "地質剖面以新的 QGIS 視窗開啟，目前的專案不會更動。</p>"),
    ("zh_CN", "<p><b>褶皱</b>：褶皱枢纽处的地层面包含褶皱轴（趋向／倾伏角），因此轴迹会在枢纽加入产状条件。</p>"
              "<p><b>输出</b>：所有成果输出至同一文件夹（前缀.gpkg、前缀_viewer.html、勾选的 CAD 格式、每个剖面一个 前缀_section_<剖面名>.qgz，各剖面在 GeoPackage 中各自成图层，x＝自 0 起算的距离、y＝高程）；"
              "地质剖面以新的 QGIS 窗口打开，当前工程不会更改。</p>"),
    ("ja", "<p><b>褶曲</b>：ヒンジでは地層面が褶曲軸（トレンド／プランジ）を含むため、軸跡がヒンジの姿勢条件になります。</p>"
           "<p><b>出力</b>：すべて同じフォルダに保存します（接頭辞.gpkg、接頭辞_viewer.html、選んだ CAD 形式、断面ごとの 接頭辞_section_<断面名>.qgz。各断面は GeoPackage の別レイヤで x＝0 からの距離、y＝標高）。"
           "地質断面は新しい QGIS ウィンドウで開き、現在のプロジェクトは変更しません。</p>"),
):
    STRINGS["help_model3d"][_lang] += _text
STRINGS.update({
    "m_drape": {
        "en": "Map layers draped on the terrain (3D viewer, OBJ texture)", "zh_TW": "貼在地形面上的地圖圖層（3D 檢視器、OBJ 貼圖）",
        "zh_CN": "贴在地形面上的地图图层（3D 查看器、OBJ 贴图）", "ja": "地形面に貼る地図レイヤ（3D ビューア、OBJ テクスチャ）"},
    "m_drape_px": {
        "en": "Map image size (pixels, long side)", "zh_TW": "地圖影像大小（長邊像素）",
        "zh_CN": "地图影像大小（长边像素）", "ja": "地図画像サイズ（長辺ピクセル）"},
    "m_msg_drape": {
        "en": "Map of {n} layers rendered for the terrain ({w} x {h} px)", "zh_TW": "已將 {n} 個圖層的地圖繪製為地形貼圖（{w} × {h} 像素）",
        "zh_CN": "已将 {n} 个图层的地图绘制为地形贴图（{w} × {h} 像素）", "ja": "{n} レイヤの地図を地形テクスチャとして描画（{w} × {h} px）"},
    "v_map": {"en": "QGIS map on the terrain", "zh_TW": "地形面貼上 QGIS 地圖", "zh_CN": "地形面贴上 QGIS 地图",
              "ja": "地形面に QGIS 地図を貼る"},
})
for _lang, _text in (
    ("en", "<p><b>Map drape</b>: the chosen map layers (by default the visible layers) are rendered and draped on "
           "the terrain of the 3D viewer and of the OBJ file, and saved as a georeferenced PNG (*_map.png + .pgw).</p>"),
    ("zh_TW", "<p><b>地圖貼圖</b>：所選的地圖圖層（預設為目前顯示的圖層）會繪製成影像，貼在 3D 檢視器與 OBJ 的地形面上，"
              "並另存為含地理參考的 PNG（*_map.png＋.pgw）。</p>"),
    ("zh_CN", "<p><b>地图贴图</b>：所选的地图图层（默认为当前显示的图层）会绘制成影像，贴在 3D 查看器与 OBJ 的地形面上，"
              "并另存为含地理参考的 PNG（*_map.png＋.pgw）。</p>"),
    ("ja", "<p><b>地図の貼り付け</b>：選んだ地図レイヤ（既定は表示中のレイヤ）を画像にして 3D ビューアと OBJ の地形面に貼り、"
           "位置情報付き PNG（*_map.png＋.pgw）としても保存します。</p>"),
):
    STRINGS["help_model3d"][_lang] += _text

# 1.3: one output folder, sections in a new project, section cut in the viewer
STRINGS.update({
    "m_folder": {"en": "Output folder (GeoPackage, 3D viewer, 3D CAD, sections project)",
                 "zh_TW": "輸出資料夾（GeoPackage、3D 檢視器、3D CAD、剖面專案）",
                 "zh_CN": "输出文件夹（GeoPackage、3D 查看器、3D CAD、剖面工程）",
                 "ja": "出力フォルダ（GeoPackage、3D ビューア、3D CAD、断面プロジェクト）"},
    "m_prefix": {"en": "File name prefix", "zh_TW": "檔名前綴", "zh_CN": "文件名前缀", "ja": "ファイル名の接頭辞"},
    "m_open_sec": {"en": "Open the first section project in a new QGIS window",
                   "zh_TW": "以新的 QGIS 視窗開啟第一個剖面專案",
                   "zh_CN": "以新的 QGIS 窗口打开第一个剖面工程",
                   "ja": "最初の断面プロジェクトを新しい QGIS ウィンドウで開く"},
    "m_sec_project": {"en": "Sections project (QGZ)", "zh_TW": "剖面專案（QGZ）", "zh_CN": "剖面工程（QGZ）",
                      "ja": "断面プロジェクト（QGZ）"},
    "m_sec_project_title": {"en": "Geological sections – {name}", "zh_TW": "地質剖面－{name}",
                            "zh_CN": "地质剖面－{name}", "ja": "地質断面－{name}"},
    "m_msg_secproj": {"en": "Sections project written: {path}", "zh_TW": "已寫出剖面專案：{path}",
                      "zh_CN": "已写出剖面工程：{path}", "ja": "断面プロジェクトを保存しました：{path}"},
    "m_msg_secproj_manual": {"en": "Could not start a new QGIS window; open {path} yourself.",
                             "zh_TW": "無法另開 QGIS 視窗，請自行開啟 {path}。",
                             "zh_CN": "无法另开 QGIS 窗口，请自行打开 {path}。",
                             "ja": "新しい QGIS ウィンドウを起動できません。{path} を開いてください。"},
    "m_msg_locked": {"en": "Cannot overwrite {path} (is it open in QGIS?). Choose another folder or prefix.",
                     "zh_TW": "無法覆寫 {path}（是否正在 QGIS 中開啟？）。請改用其他資料夾或檔名前綴。",
                     "zh_CN": "无法覆盖 {path}（是否正在 QGIS 中打开？）。请改用其他文件夹或文件名前缀。",
                     "ja": "{path} を上書きできません（QGIS で開いていませんか？）。別のフォルダか接頭辞を指定してください。"},
    "m_lyr_units": {"en": "Section units", "zh_TW": "剖面地層", "zh_CN": "剖面地层", "ja": "断面の地層"},
    "m_legend": {"en": "Legend", "zh_TW": "圖例", "zh_CN": "图例", "ja": "凡例"},
    "v_cut_sec": {"en": "Section cut", "zh_TW": "剖面切割", "zh_CN": "剖面切割", "ja": "断面で切断"},
    "v_cut_none": {"en": "(none)", "zh_TW": "（不切割）", "zh_CN": "（不切割）", "ja": "（切断しない）"},
    "v_cut_left": {"en": "keep the left side ({a} → {b})", "zh_TW": "保留左側（{a} → {b}）",
                   "zh_CN": "保留左侧（{a} → {b}）", "ja": "左側を残す（{a} → {b}）"},
    "v_cut_right": {"en": "keep the right side ({a} → {b})", "zh_TW": "保留右側（{a} → {b}）",
                    "zh_CN": "保留右侧（{a} → {b}）", "ja": "右側を残す（{a} → {b}）"},
})
STRINGS.update({
    "m_sec_coords": {
        "en": "Section coordinates: x = distance from the section start (m), y = elevation (m) x V.E. {ve}",
        "zh_TW": "剖面座標：x＝自剖面起點起算的距離（m），y＝高程（m）× 垂直誇大 {ve}",
        "zh_CN": "剖面坐标：x＝自剖面起点起算的距离（m），y＝高程（m）× 垂直夸大 {ve}",
        "ja": "断面座標：x＝断面始点からの距離（m）、y＝標高（m）× 垂直誇張 {ve}"},
})
# fmt: on
