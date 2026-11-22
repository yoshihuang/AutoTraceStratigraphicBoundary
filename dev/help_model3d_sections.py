# -*- coding: utf-8 -*-
"""Insert the '3D model and sections' chapter into the four help pages (idempotent)."""
import os
import re

HELP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "autotrace_strat_boundary", "help")

CH = {
"en": dict(
toc="3D geological model and sections",
tips_old="8. Tips and limitations", tips_new="9. Tips and limitations",
flow='<td>→</td>\n<td><b>⑤</b><br><i>3D model and sections</i><br>(GeoPackage, CAD, 3D viewer)</td>',
step='<li><b>Build 3D geological model and sections…</b> – the dialog is pre-filled with <i>geology</i>, <i>DEM</i>, '
     '<i>faults</i>, <i>bedding</i>, <i>Stratigraphic_Boundary</i> and <i>section_line</i>. Choose the output GeoPackage and '
     'click <b>Run</b>. The section sheet appears below the map and the 3D viewer opens in the web browser.</li>',
body='''<h2 id="model3d">8. 3D geological model and sections</h2>
<p>The tool <b>Build 3D geological model and sections</b> turns the geological map into a 3D model, using the same
<b>implicit potential-field method</b> as the web app <a href="https://yoshihuang.github.io/geomap-workbench/">geomap-workbench</a>.</p>
<h3>8.1 Principle</h3>
<ul>
<li>Units are grouped into <b>series</b> (field <code>series</code>; a higher number lies above an unconformity) and ordered by
<code>strat_order</code> (1 = oldest).</li>
<li>For every series a scalar field f(x, y, z) is interpolated with a cubic radial basis function (kernel r³):
<b>interface points</b> come from the contacts between adjacent units on the geological map, placed on the DEM, and each contact
is an iso-surface of f; <b>attitudes</b> (dip, dip direction, overturned) are gradient constraints, so the surfaces dip correctly
at depth; every <b>fault</b> adds a drift term on its hanging-wall side, so the surfaces are offset across the fault plane
(trace + dip + dip direction).</li>
<li>A point belongs to the youngest series whose field is above that series' base, and to the unit whose interval contains
the field value. Units with <code>kind = ign</code> are extruded vertically from the map.</li>
<li>Solids are extracted with marching tetrahedra, clipped by the topography and the model box; they are closed (watertight)
meshes, so volumes are computed (<code>volume_m3</code>).</li>
<li>Quality: the log reports how many map cells have the same unit at the ground surface in the model (99.6 % for the sample).</li>
</ul>
<div class="fig"><img src="../img/fig5_model3d.png" width="560"><br>
<span class="cap">Fig. 5 – 3D model of the sample: plunging anticline (O1 core) offset by fault F1; terrain draped with the geological map.</span></div>
<div class="fig"><img src="../img/fig6_section.png" width="620"><br>
<span class="cap">Fig. 6 – Geological section A–A' of the sample (V.E. ×1), drawn below the map in QGIS.</span></div>
<h3>8.2 Parameters</h3>
<table class="grid">
<tr><th>Parameter</th><th>Meaning</th></tr>
<tr><td>Geological map and its fields</td><td>Unit code, stratigraphic order, name, series, thickness, kind (sed / ign).</td></tr>
<tr><td>Faults: dip / dip direction fields</td><td>Fault plane attitude (default dip 60° when empty).</td></tr>
<tr><td>Attitude points 1 and 2</td><td>Dip, dip direction (or strike), unit code (optional; otherwise the unit under the point), overturned.</td></tr>
<tr><td>Section lines</td><td>One section per line (field <code>name</code>, e.g. A-A'). Empty: one section across the strike.</td></tr>
<tr><td>Vertical exaggeration</td><td>Of the section sheet.</td></tr>
<tr><td>Cell size / model depth</td><td>0 = automatic (1/40 of the map width; depth 35 % of the width below the lowest ground). Smaller cells give smoother but larger files.</td></tr>
<tr><td>Use the unit thicknesses (advanced)</td><td>Fixes the spacing of the interfaces to <code>thick_m</code> instead of solving it from the contacts.</td></tr>
<tr><td>3D CAD formats</td><td>DXF (polyface meshes, one layer per unit), OBJ + MTL (colours), STL (one file per unit).</td></tr>
</table>
<h3>8.3 Outputs</h3>
<table class="grid">
<tr><th>GeoPackage layer</th><th>Content</th></tr>
<tr><td>units_3d</td><td>Closed 3D solid of every unit (MultiPolygonZ, triangles) with volume</td></tr>
<tr><td>horizons_3d / faults_3d / terrain_3d</td><td>Interfaces between units, fault planes, ground surface coloured by unit</td></tr>
<tr><td>section_fences_3d</td><td>Sections as vertical 3D panels on the section lines (for the QGIS 3D map view)</td></tr>
<tr><td>section_units / section_profile / section_faults / section_frame / section_labels</td><td>The section sheet, placed below the map in the map CRS (x = distance, y = elevation × V.E.), ready for a print layout</td></tr>
<tr><td>section_lines / model_info</td><td>Section lines on the map; parameters, interface levels and warnings</td></tr>
</table>
<p>Next to the GeoPackage: <code>*.dxf</code>, <code>*.obj</code> + <code>*.mtl</code>, <code>*_unit_*.stl</code> and <code>*_viewer.html</code>
– an offline 3D viewer (three.js) with unit switches, transparency, vertical exaggeration, east / north cut planes,
sections and PNG export. Add <code>#nopanel</code> to its address for a clean screenshot.</p>
'''),
"zh_TW": dict(
toc="3D 地質模型與地質剖面",
tips_old="8. 注意事項與限制", tips_new="9. 注意事項與限制",
flow='<td>→</td>\n<td><b>⑤</b><br><i>3D 模型與剖面</i><br>（GeoPackage、CAD、3D 檢視器）</td>',
step='<li><b>產生 3D 地質模型與地質剖面…</b>：對話框已自動帶入 <i>geology</i>、<i>DEM</i>、<i>faults</i>、<i>bedding</i>、'
     '<i>Stratigraphic_Boundary</i> 與 <i>section_line</i>；選擇輸出 GeoPackage 後按 <b>執行</b>。'
     '地質剖面會繪在地質圖下方，3D 檢視器則以瀏覽器開啟。</li>',
body='''<h2 id="model3d">8. 3D 地質模型與地質剖面</h2>
<p>「產生 3D 地質模型與地質剖面」工具把地質圖轉成 3D 模型，方法與網頁版
<a href="https://yoshihuang.github.io/geomap-workbench/">geomap-workbench</a> 相同，採用<b>隱式位勢場法</b>。</p>
<h3>8.1 原理</h3>
<ul>
<li>地層依<b>層系</b>（欄位 <code>series</code>；數字大者位於不整合之上）分組，並依 <code>strat_order</code>（1＝最老）排序。</li>
<li>每個層系以三次徑向基函數（核函數 r³）內插一個純量場 f(x, y, z)：<b>界面點</b>取自地質圖上相鄰地層的界線並置於 DEM 上，
每條界線都是 f 的一個等值面；<b>位態</b>（傾角、傾向、倒轉）作為梯度條件，使地層面在地下有正確的傾斜；
每條<b>斷層</b>（跡線＋傾角＋傾向）在上盤加入一個漂移項，使地層面在斷層面兩側錯移。</li>
<li>某一點屬於「場值高於該層系底面」的最年輕層系，並依場值所在區間決定地層。<code>kind = ign</code> 的地層由地質圖垂直延伸。</li>
<li>以 marching tetrahedra 擷取各地層實體，並以地形與模型邊界裁切；實體為封閉網格，因此可計算體積（<code>volume_m3</code>）。</li>
<li>品質檢核：記錄中會列出模型地表地層與地質圖的一致率（範例為 99.6%）。</li>
</ul>
<div class="fig"><img src="../img/fig5_model3d.png" width="560"><br>
<span class="cap">圖 5－範例的 3D 地質模型：傾沒背斜（核部 O1）被斷層 F1 錯移；地形面貼上地質圖。</span></div>
<div class="fig"><img src="../img/fig6_section.png" width="620"><br>
<span class="cap">圖 6－範例的地質剖面 A–A'（垂直誇大 ×1），繪於 QGIS 地質圖下方。</span></div>
<h3>8.2 參數</h3>
<table class="grid">
<tr><th>參數</th><th>說明</th></tr>
<tr><td>地質圖及其欄位</td><td>地層代號、層序、名稱、層系、厚度、岩類（sed／ign）。</td></tr>
<tr><td>斷層：傾角／傾向欄位</td><td>斷層面位態（空白時預設傾角 60°）。</td></tr>
<tr><td>位態點位 1、2</td><td>傾角、傾向（或走向）、所屬地層（選填，否則取點位所在的地層）、倒轉。</td></tr>
<tr><td>剖面線</td><td>每條線產生一個剖面（欄位 <code>name</code>，如 A-A'）；空白時自動產生一條垂直走向的剖面。</td></tr>
<tr><td>剖面垂直誇大倍率</td><td>剖面圖的垂直誇大。</td></tr>
<tr><td>網格大小／模型深度</td><td>0＝自動（圖幅寬度的 1/40；深度為最低地表以下圖幅寬度的 35%）。網格愈小愈平滑，但檔案愈大。</td></tr>
<tr><td>以地層厚度作為界面間距（進階）</td><td>以 <code>thick_m</code> 固定界面間距，而不由界線推求。</td></tr>
<tr><td>3D CAD 格式</td><td>DXF（polyface mesh，每個地層一個圖層）、OBJ + MTL（含顏色）、STL（每個地層一個檔案）。</td></tr>
</table>
<h3>8.3 輸出</h3>
<table class="grid">
<tr><th>GeoPackage 圖層</th><th>內容</th></tr>
<tr><td>units_3d</td><td>各地層的封閉 3D 實體（MultiPolygonZ 三角網）及體積</td></tr>
<tr><td>horizons_3d／faults_3d／terrain_3d</td><td>地層界面、斷層面、依地層著色的地形面</td></tr>
<tr><td>section_fences_3d</td><td>立在剖面線上的 3D 剖面（供 QGIS 3D 地圖檢視）</td></tr>
<tr><td>section_units／section_profile／section_faults／section_frame／section_labels</td><td>地質剖面圖，以地圖座標繪於地質圖下方（x＝距離、y＝高程×垂直誇大），可直接放入列印版面</td></tr>
<tr><td>section_lines／model_info</td><td>地圖上的剖面線；參數、界面場值與警告</td></tr>
</table>
<p>GeoPackage 旁另有 <code>*.dxf</code>、<code>*.obj</code> + <code>*.mtl</code>、<code>*_unit_*.stl</code> 與 <code>*_viewer.html</code>。
後者是離線 3D 檢視器（three.js），可切換各地層、調整透明度與垂直誇大、東西／南北向切割、顯示剖面並存成 PNG；
網址後加上 <code>#nopanel</code> 可隱藏面板以便截圖。</p>
'''),
"zh_CN": dict(
toc="3D 地质模型与地质剖面",
tips_old="8. 注意事项与限制", tips_new="9. 注意事项与限制",
flow='<td>→</td>\n<td><b>⑤</b><br><i>3D 模型与剖面</i><br>（GeoPackage、CAD、3D 查看器）</td>',
step='<li><b>生成 3D 地质模型与地质剖面…</b>：对话框已自动填入 <i>geology</i>、<i>DEM</i>、<i>faults</i>、<i>bedding</i>、'
     '<i>Stratigraphic_Boundary</i> 与 <i>section_line</i>；选择输出 GeoPackage 后点击 <b>运行</b>。'
     '地质剖面会绘在地质图下方，3D 查看器则用浏览器打开。</li>',
body='''<h2 id="model3d">8. 3D 地质模型与地质剖面</h2>
<p>“生成 3D 地质模型与地质剖面”工具把地质图转成 3D 模型，方法与网页版
<a href="https://yoshihuang.github.io/geomap-workbench/">geomap-workbench</a> 相同，采用<b>隐式位势场法</b>。</p>
<h3>8.1 原理</h3>
<ul>
<li>地层按<b>层系</b>（字段 <code>series</code>；数字大者位于不整合之上）分组，并按 <code>strat_order</code>（1＝最老）排序。</li>
<li>每个层系用三次径向基函数（核函数 r³）插值一个标量场 f(x, y, z)：<b>界面点</b>取自地质图上相邻地层的界线并置于 DEM 上，
每条界线都是 f 的一个等值面；<b>产状</b>（倾角、倾向、倒转）作为梯度条件，使地层面在地下有正确的倾斜；
每条<b>断层</b>（迹线＋倾角＋倾向）在上盘加入一个漂移项，使地层面在断层面两侧错移。</li>
<li>某一点属于“场值高于该层系底面”的最年轻层系，并按场值所在区间确定地层。<code>kind = ign</code> 的地层由地质图垂直延伸。</li>
<li>用 marching tetrahedra 提取各地层实体，并用地形与模型边界裁切；实体为封闭网格，因此可计算体积（<code>volume_m3</code>）。</li>
<li>质量检查：日志会列出模型地表地层与地质图的一致率（示例为 99.6%）。</li>
</ul>
<div class="fig"><img src="../img/fig5_model3d.png" width="560"><br>
<span class="cap">图 5－示例的 3D 地质模型：倾伏背斜（核部 O1）被断层 F1 错移；地形面贴上地质图。</span></div>
<div class="fig"><img src="../img/fig6_section.png" width="620"><br>
<span class="cap">图 6－示例的地质剖面 A–A'（垂直夸大 ×1），绘于 QGIS 地质图下方。</span></div>
<h3>8.2 参数</h3>
<table class="grid">
<tr><th>参数</th><th>说明</th></tr>
<tr><td>地质图及其字段</td><td>地层代号、层序、名称、层系、厚度、岩类（sed／ign）。</td></tr>
<tr><td>断层：倾角／倾向字段</td><td>断层面产状（空白时默认倾角 60°）。</td></tr>
<tr><td>产状点位 1、2</td><td>倾角、倾向（或走向）、所属地层（可选，否则取点位所在的地层）、倒转。</td></tr>
<tr><td>剖面线</td><td>每条线生成一个剖面（字段 <code>name</code>，如 A-A'）；空白时自动生成一条垂直走向的剖面。</td></tr>
<tr><td>剖面垂直夸大倍率</td><td>剖面图的垂直夸大。</td></tr>
<tr><td>网格大小／模型深度</td><td>0＝自动（图幅宽度的 1/40；深度为最低地表以下图幅宽度的 35%）。网格越小越平滑，但文件越大。</td></tr>
<tr><td>以地层厚度作为界面间距（高级）</td><td>以 <code>thick_m</code> 固定界面间距，而不由界线推求。</td></tr>
<tr><td>3D CAD 格式</td><td>DXF（polyface mesh，每个地层一个图层）、OBJ + MTL（含颜色）、STL（每个地层一个文件）。</td></tr>
</table>
<h3>8.3 输出</h3>
<table class="grid">
<tr><th>GeoPackage 图层</th><th>内容</th></tr>
<tr><td>units_3d</td><td>各地层的封闭 3D 实体（MultiPolygonZ 三角网）及体积</td></tr>
<tr><td>horizons_3d／faults_3d／terrain_3d</td><td>地层界面、断层面、按地层着色的地形面</td></tr>
<tr><td>section_fences_3d</td><td>立在剖面线上的 3D 剖面（供 QGIS 3D 地图查看）</td></tr>
<tr><td>section_units／section_profile／section_faults／section_frame／section_labels</td><td>地质剖面图，以地图坐标绘于地质图下方（x＝距离、y＝高程×垂直夸大），可直接放入打印布局</td></tr>
<tr><td>section_lines／model_info</td><td>地图上的剖面线；参数、界面场值与警告</td></tr>
</table>
<p>GeoPackage 旁另有 <code>*.dxf</code>、<code>*.obj</code> + <code>*.mtl</code>、<code>*_unit_*.stl</code> 与 <code>*_viewer.html</code>。
后者是离线 3D 查看器（three.js），可切换各地层、调整透明度与垂直夸大、东西／南北向切割、显示剖面并存为 PNG；
网址后加上 <code>#nopanel</code> 可隐藏面板以便截图。</p>
'''),
"ja": dict(
toc="3D 地質モデルと地質断面",
tips_old="8. 注意点と制限", tips_new="9. 注意点と制限",
flow='<td>→</td>\n<td><b>⑤</b><br><i>3D モデルと断面</i><br>（GeoPackage、CAD、3D ビューア）</td>',
step='<li><b>3D 地質モデルと地質断面を作成…</b>：ダイアログには <i>geology</i>、<i>DEM</i>、<i>faults</i>、<i>bedding</i>、'
     '<i>Stratigraphic_Boundary</i>、<i>section_line</i> が自動で入ります。出力 GeoPackage を選び <b>実行</b> を押すと、'
     '地質断面が地質図の下に描かれ、3D ビューアがブラウザで開きます。</li>',
body='''<h2 id="model3d">8. 3D 地質モデルと地質断面</h2>
<p>「3D 地質モデルと地質断面を作成」は、Web アプリ <a href="https://yoshihuang.github.io/geomap-workbench/">geomap-workbench</a>
と同じ<b>陰的ポテンシャル場法</b>で地質図を 3D モデルに変換します。</p>
<h3>8.1 原理</h3>
<ul>
<li>地層は<b>層群</b>（フィールド <code>series</code>；大きいほど不整合の上）にまとめ、<code>strat_order</code>（1＝最古）で並べます。</li>
<li>層群ごとに 3 次の放射基底関数（核 r³）でスカラー場 f(x, y, z) を補間します。<b>境界点</b>は地質図上の隣接地層の境界から取り
DEM 上に置き、各境界は f の等値面です。<b>姿勢</b>（傾斜・傾斜方位・逆転）は勾配条件として地下での傾斜を決め、
<b>断層</b>（トレース＋傾斜＋傾斜方位）は上盤側にドリフト項を加えて境界面を変位させます。</li>
<li>ある点は「場の値がその層群の基底より上」となる最も新しい層群に属し、値の区間で地層が決まります。
<code>kind = ign</code> の地層は地質図から鉛直に延ばします。</li>
<li>marching tetrahedra で各地層の立体を抽出し、地形とモデル範囲で切り取ります。閉じたメッシュなので体積（<code>volume_m3</code>）も計算します。</li>
<li>品質：ログに地表でのモデルと地質図の一致率を表示します（サンプルでは 99.6%）。</li>
</ul>
<div class="fig"><img src="../img/fig5_model3d.png" width="560"><br>
<span class="cap">図 5－サンプルの 3D 地質モデル：断層 F1 で変位したプランジ背斜（核部 O1）。地形面に地質図を貼っています。</span></div>
<div class="fig"><img src="../img/fig6_section.png" width="620"><br>
<span class="cap">図 6－サンプルの地質断面 A–A'（垂直誇張 ×1）。QGIS で地質図の下に描かれます。</span></div>
<h3>8.2 パラメータ</h3>
<table class="grid">
<tr><th>パラメータ</th><th>説明</th></tr>
<tr><td>地質図とフィールド</td><td>地層コード、層序、名称、層群、層厚、岩種（sed／ign）。</td></tr>
<tr><td>断層：傾斜／傾斜方位フィールド</td><td>断層面の姿勢（空欄なら傾斜 60°）。</td></tr>
<tr><td>姿勢点 1・2</td><td>傾斜、傾斜方位（または走向）、地層コード（任意；なければ点の下の地層）、逆転。</td></tr>
<tr><td>断面線</td><td>線ごとに 1 断面（フィールド <code>name</code>、例：A-A'）。空欄なら走向に直交する断面を 1 本作成。</td></tr>
<tr><td>断面の垂直誇張</td><td>断面図の垂直誇張。</td></tr>
<tr><td>セルサイズ／モデル深さ</td><td>0＝自動（図幅幅の 1/40；深さは最低地表から図幅幅の 35%）。小さいほど滑らかですがファイルは大きくなります。</td></tr>
<tr><td>層厚を境界面の間隔に使う（詳細）</td><td>境界から求めず、<code>thick_m</code> で境界面の間隔を固定します。</td></tr>
<tr><td>3D CAD 形式</td><td>DXF（polyface mesh、地層ごとのレイヤ）、OBJ + MTL（色付き）、STL（地層ごとのファイル）。</td></tr>
</table>
<h3>8.3 出力</h3>
<table class="grid">
<tr><th>GeoPackage レイヤ</th><th>内容</th></tr>
<tr><td>units_3d</td><td>各地層の閉じた 3D 立体（MultiPolygonZ の三角形）と体積</td></tr>
<tr><td>horizons_3d／faults_3d／terrain_3d</td><td>地層境界面、断層面、地層で色分けした地形面</td></tr>
<tr><td>section_fences_3d</td><td>断面線上に立てた 3D 断面（QGIS の 3D マップビュー用）</td></tr>
<tr><td>section_units／section_profile／section_faults／section_frame／section_labels</td><td>地図座標で地質図の下に配置した断面図（x＝距離、y＝標高×垂直誇張）。印刷レイアウトにそのまま使えます</td></tr>
<tr><td>section_lines／model_info</td><td>地図上の断面線；パラメータ、境界面の値、警告</td></tr>
</table>
<p>GeoPackage の横に <code>*.dxf</code>、<code>*.obj</code> + <code>*.mtl</code>、<code>*_unit_*.stl</code>、<code>*_viewer.html</code> を出力します。
最後はオフラインの 3D ビューア（three.js）で、地層の表示切替、透明度、垂直誇張、東西／南北の切断、断面表示、PNG 保存ができます。
アドレスに <code>#nopanel</code> を付けるとパネルを隠してスクリーンショットを撮れます。</p>
'''),
}

for lang, c in CH.items():
    p = os.path.join(HELP, lang, "index.html")
    s = open(p, encoding="utf-8").read()
    if 'id="model3d"' in s:
        print(lang, "already done")
        continue
    # contents: insert before the tips entry
    s = s.replace('<li><a href="#tips">', '<li><a href="#model3d">%s</a></li>\n<li><a href="#tips">' % c["toc"], 1)
    # workflow: add step 5
    s = re.sub(r'(</td>\s*</tr></table>)', c["flow"] + r"\n</tr></table>", s, count=1) if False else \
        s.replace("</td>\n</tr></table>", "</td>" + c["flow"] + "\n</tr></table>", 1)
    # step-by-step: add the step before the closing </ol> of the steps chapter
    i = s.index('id="steps"')
    j = s.index("</ol>", i)
    s = s[:j] + c["step"] + "\n" + s[j:]
    # new chapter before tips
    s = s.replace('<h2 id="tips">' + c["tips_old"], c["body"] + '\n<h2 id="tips">' + c["tips_new"], 1)
    assert 'id="model3d"' in s, lang
    open(p, "w", encoding="utf-8").write(s)
    print(lang, "ok")
