# -*- coding: utf-8 -*-
"""Guide update for 1.3: output folder, sections project, viewer section cut, new sample (idempotent)."""
import io
import os
import re

HELP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "autotrace_strat_boundary", "help")

T = {
"en": dict(
    sample_after="can be opened at once.</li>",
    sample_add=" The sample also contains the result of every step: <i>地層邊界預判線</i> (predicted lines), "
               "<i>地層預判界線(修正後)</i> (edited lines), <i>geology_Interpolation</i> (generated geology) and "
               "<i>Checking_Point</i> (check point), so each tool can be tried directly.",
    step_re=r"<li><b>Build 3D geological model and sections…</b>.*?</li>",
    step='<li><b>Build 3D geological model and sections…</b> – the dialog is pre-filled with the geology, <i>DEM</i>, '
         '<i>faults</i>, <i>fold_axes</i>, <i>bedding</i>, <i>Stratigraphic_Boundary</i>, <i>section_line</i> and the visible '
         'layers to drape. Choose an <b>output folder</b> and a file-name prefix and click <b>Run</b>. The sections open '
         'in a <b>new QGIS window</b> (your project stays open and unchanged) and the 3D model opens in the web browser.</li>',
    row_re=r"<tr><td>Output files</td><td>.*?</td></tr>",
    row='<tr><td>Output folder, file-name prefix, 3D CAD formats</td><td>Everything is written to one folder: '
        '<code>prefix.gpkg</code>, <code>prefix_viewer.html</code>, <code>prefix_sections.qgz</code>, '
        '<code>prefix_map.png</code> + <code>.pgw</code> and the ticked CAD formats: DXF (polyface meshes, one layer per unit), '
        'OBJ + MTL (colours, textured terrain), STL (one file per unit).</td></tr>',
    para_re=r"<p>Other outputs \(file names chosen in the dialog\):.*?</p>",
    para='<p><b>Sections project</b> – <code>prefix_sections.qgz</code> contains only the section sheet (unit polygons with '
         'a legend, ground profile, faults, fold marks, frame, ticks and labels) and an A3 print layout ready for '
         'PDF export. It opens in a separate QGIS window, so the current project is neither closed nor changed.</p>\n'
         '<p><b>3D viewer</b> – <code>prefix_viewer.html</code> (three.js, works offline): unit switches, transparency, '
         'vertical exaggeration, east / north cuts and the <b>section cut</b> – choose a section and the side to keep; '
         'the model is cut along the section line, the section drawing caps the cut and the view turns to it. '
         'Add <code>#cut=0:L</code> (or <code>0:R</code>) to the address to open with a cut, <code>#nopanel</code> '
         'for a clean screenshot.</p>'),
"zh_TW": dict(
    sample_after="並可立即開啟。</li>",
    sample_add="範例中也保留了各步驟的成果：<i>地層邊界預判線</i>（預判線）、<i>地層預判界線(修正後)</i>（編修後的線）、"
               "<i>geology_Interpolation</i>（產生的地質圖）與 <i>Checking_Point</i>（檢核點），可直接試用各項工具。",
    step_re=r"<li><b>產生 3D 地質模型與地質剖面…</b>.*?</li>",
    step='<li><b>產生 3D 地質模型與地質剖面…</b>：對話框已自動帶入地質圖、<i>DEM</i>、<i>faults</i>、<i>fold_axes</i>、'
         '<i>bedding</i>、<i>Stratigraphic_Boundary</i>、<i>section_line</i> 與要貼在地形面上的顯示中圖層。'
         '選擇<b>輸出資料夾</b>與檔名前綴後按 <b>執行</b>。地質剖面會以<b>新的 QGIS 視窗</b>開啟'
         '（原本的專案不關閉、也不新增圖層），3D 模型則在瀏覽器中開啟。</li>',
    row_re=r"<tr><td>輸出檔案</td><td>.*?</td></tr>",
    row='<tr><td>輸出資料夾、檔名前綴、3D CAD 格式</td><td>所有成果輸出至同一資料夾：<code>前綴.gpkg</code>、'
        '<code>前綴_viewer.html</code>、<code>前綴_sections.qgz</code>、<code>前綴_map.png</code>＋<code>.pgw</code>，'
        '以及勾選的 CAD 格式：DXF（polyface mesh，每個地層一個圖層）、OBJ + MTL（含顏色與地形貼圖）、STL（每個地層一個檔案）。</td></tr>',
    para_re=r"<p>另可輸出（檔名可在對話框指定）.*?</p>",
    para='<p><b>剖面專案</b>：<code>前綴_sections.qgz</code> 只包含地質剖面圖（含圖例的地層、地形線、斷層、褶皺標示、圖框、'
         '刻度與標註）及一個 A3 列印版面，可直接輸出 PDF。它會另開一個 QGIS 視窗，目前的專案不會被關閉或更動。</p>\n'
         '<p><b>3D 檢視器</b>：<code>前綴_viewer.html</code>（three.js，可離線使用）可切換各地層、調整透明度與垂直誇大、'
         '東西／南北向切割，以及<b>剖面切割</b>：選擇剖面與要保留的一側，模型即沿剖面線切開，切面以剖面圖呈現，'
         '視角也會轉向切面。網址後加 <code>#cut=0:L</code>（或 <code>0:R</code>）可直接以切割狀態開啟，'
         '加 <code>#nopanel</code> 可隱藏面板以便截圖。</p>'),
"zh_CN": dict(
    sample_after="并可立即打开。</li>",
    sample_add="示例中也保留了各步骤的成果：<i>地層邊界預判線</i>（预判线）、<i>地層預判界線(修正後)</i>（编辑后的线）、"
               "<i>geology_Interpolation</i>（生成的地质图）与 <i>Checking_Point</i>（检核点），可直接试用各项工具。",
    step_re=r"<li><b>生成 3D 地质模型与地质剖面…</b>.*?</li>",
    step='<li><b>生成 3D 地质模型与地质剖面…</b>：对话框已自动填入地质图、<i>DEM</i>、<i>faults</i>、<i>fold_axes</i>、'
         '<i>bedding</i>、<i>Stratigraphic_Boundary</i>、<i>section_line</i> 与要贴在地形面上的显示中图层。'
         '选择<b>输出文件夹</b>与文件名前缀后点击 <b>运行</b>。地质剖面会以<b>新的 QGIS 窗口</b>打开'
         '（原本的工程不关闭、也不新增图层），3D 模型则在浏览器中打开。</li>',
    row_re=r"<tr><td>输出文件</td><td>.*?</td></tr>",
    row='<tr><td>输出文件夹、文件名前缀、3D CAD 格式</td><td>所有成果输出至同一文件夹：<code>前缀.gpkg</code>、'
        '<code>前缀_viewer.html</code>、<code>前缀_sections.qgz</code>、<code>前缀_map.png</code>＋<code>.pgw</code>，'
        '以及勾选的 CAD 格式：DXF（polyface mesh，每个地层一个图层）、OBJ + MTL（含颜色与地形贴图）、STL（每个地层一个文件）。</td></tr>',
    para_re=r"<p>另可输出（文件名可在对话框指定）.*?</p>",
    para='<p><b>剖面工程</b>：<code>前缀_sections.qgz</code> 只包含地质剖面图（含图例的地层、地形线、断层、褶皱标示、图框、'
         '刻度与标注）及一个 A3 打印布局，可直接输出 PDF。它会另开一个 QGIS 窗口，当前工程不会被关闭或更改。</p>\n'
         '<p><b>3D 查看器</b>：<code>前缀_viewer.html</code>（three.js，可离线使用）可切换各地层、调整透明度与垂直夸大、'
         '东西／南北向切割，以及<b>剖面切割</b>：选择剖面与要保留的一侧，模型即沿剖面线切开，切面以剖面图呈现，'
         '视角也会转向切面。网址后加 <code>#cut=0:L</code>（或 <code>0:R</code>）可直接以切割状态打开，'
         '加 <code>#nopanel</code> 可隐藏面板以便截图。</p>'),
"ja": dict(
    sample_after="すぐに開けます。</li>",
    sample_add="サンプルには各手順の成果も含まれます：<i>地層邊界預判線</i>（予測線）、<i>地層預判界線(修正後)</i>（編集後の線）、"
               "<i>geology_Interpolation</i>（作成した地質図）、<i>Checking_Point</i>（チェック点）。各ツールをすぐ試せます。",
    step_re=r"<li><b>3D 地質モデルと地質断面を作成…</b>.*?</li>",
    step='<li><b>3D 地質モデルと地質断面を作成…</b>：ダイアログには地質図、<i>DEM</i>、<i>faults</i>、<i>fold_axes</i>、'
         '<i>bedding</i>、<i>Stratigraphic_Boundary</i>、<i>section_line</i> と地形に貼る表示中のレイヤが自動で入ります。'
         '<b>出力フォルダ</b>とファイル名の接頭辞を選び <b>実行</b> を押すと、地質断面は<b>新しい QGIS ウィンドウ</b>で開き'
         '（現在のプロジェクトは閉じず、レイヤも追加しません）、3D モデルはブラウザで開きます。</li>',
    row_re=r"<tr><td>出力ファイル</td><td>.*?</td></tr>",
    row='<tr><td>出力フォルダ、接頭辞、3D CAD 形式</td><td>すべて同じフォルダに出力します：<code>接頭辞.gpkg</code>、'
        '<code>接頭辞_viewer.html</code>、<code>接頭辞_sections.qgz</code>、<code>接頭辞_map.png</code>＋<code>.pgw</code>、'
        'およびチェックした CAD 形式：DXF（polyface mesh、地層ごとのレイヤ）、OBJ + MTL（色・地形テクスチャ付き）、STL（地層ごと）。</td></tr>',
    para_re=r"<p>このほか（ファイル名はダイアログで指定）.*?</p>",
    para='<p><b>断面プロジェクト</b>：<code>接頭辞_sections.qgz</code> は地質断面図（凡例付きの地層、地形線、断層、褶曲記号、図枠、'
         '目盛、注記）と A3 印刷レイアウトだけを含み、そのまま PDF 出力できます。別の QGIS ウィンドウで開くため、'
         '現在のプロジェクトは閉じず変更もしません。</p>\n'
         '<p><b>3D ビューア</b>：<code>接頭辞_viewer.html</code>（three.js、オフライン可）で地層の表示切替、透明度、垂直誇張、'
         '東西／南北の切断、そして<b>断面で切断</b>ができます。断面と残す側を選ぶと断面線に沿ってモデルを切り、'
         '切り口に断面図を表示して視点を向けます。アドレスに <code>#cut=0:L</code>（または <code>0:R</code>）を付けると'
         '切断した状態で、<code>#nopanel</code> を付けるとパネルなしで開きます。</p>'),
}

for lang, c in T.items():
    p = os.path.join(HELP, lang, "index.html")
    s = io.open(p, encoding="utf-8").read()
    if "_sections.qgz" in s:
        print(lang, "already updated")
        continue
    i = s.index('id="steps"')
    j = s.index(c["sample_after"], i)
    k = j + len(c["sample_after"]) - len("</li>")
    s = s[:k] + c["sample_add"] + s[k:]
    for key in ("step", "row", "para"):
        new, n = re.subn(c[key + "_re"], lambda m: c[key], s, count=1, flags=re.S)
        assert n == 1, (lang, key)
        s = new
    io.open(p, "w", encoding="utf-8").write(s)
    print(lang, "ok")
