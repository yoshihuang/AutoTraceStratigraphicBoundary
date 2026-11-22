# -*- coding: utf-8 -*-
"""Guide update for 1.4: one layer set and one QGIS project per section, local section coordinates."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELP = os.path.join(ROOT, "autotrace_strat_boundary", "help")

REP = {
"en": [
    ("<code>prefix_sections.qgz</code>, ", "<code>prefix_section_&lt;name&gt;.qgz</code> (one per section), "),
    ('<p><b>Sections project</b> – <code>prefix_sections.qgz</code> contains only the section sheet',
     '<p><b>Section projects</b> – every section line gets its own layers in the GeoPackage '
     '(<code>section_&lt;name&gt;_units / _profile / _faults / _frame / _labels</code>, e.g. <code>section_A_A_units</code>) '
     'and its own project <code>prefix_section_&lt;name&gt;.qgz</code>, which can be opened separately. Each section uses '
     'its own coordinates: <b>x = distance from the section start (0 at the left edge), y = elevation</b> '
     '(× V.E. when it is not 1), so the left end of the ground line lies at the ground elevation of the section start. '
     'A project contains only that section'),
    ("It opens in a separate QGIS window, so the current project is neither closed nor changed.",
     "The first one opens in a separate QGIS window, so the current project is neither closed nor changed."),
    ("<tr><td>section_units / section_profile / section_faults / section_frame / section_labels</td><td>The section sheet, placed below the map in the map CRS (x = distance, y = elevation × V.E.), ready for a print layout</td></tr>",
     "<tr><td>section_&lt;name&gt;_units / _profile / _faults / _frame / _labels</td><td>The sheet of each section in its own layers; local section coordinates: x = distance from the section start (0), y = elevation × V.E.</td></tr>"),
    ("drawn below the map in QGIS.", "x = distance from the start, y = elevation."),
],
"zh_TW": [
    ("<code>前綴_sections.qgz</code>、", "<code>前綴_section_&lt;剖面名&gt;.qgz</code>（每個剖面一個）、"),
    ('<p><b>剖面專案</b>：<code>前綴_sections.qgz</code> 只包含地質剖面圖',
     '<p><b>剖面專案</b>：每條剖面線在 GeoPackage 中都有各自的圖層'
     '（<code>section_&lt;剖面名&gt;_units／_profile／_faults／_frame／_labels</code>，如 <code>section_A_A_units</code>），'
     '並各自存成 <code>前綴_section_&lt;剖面名&gt;.qgz</code>，可分別開啟預覽。每個剖面使用自己的座標：'
     '<b>x＝自剖面起點起算的距離（左緣為 0），y＝高程</b>（垂直誇大不為 1 時乘上倍率），'
     '因此地形線左端的 y 值即為剖面起點的地表高程。每個專案只包含該剖面的地質剖面圖'),
    ("它會另開一個 QGIS 視窗，目前的專案不會被關閉或更動。", "第一個剖面專案會另開一個 QGIS 視窗，目前的專案不會被關閉或更動。"),
    ("<tr><td>section_units／section_profile／section_faults／section_frame／section_labels</td><td>地質剖面圖，以地圖座標繪於地質圖下方（x＝距離、y＝高程×垂直誇大），可直接放入列印版面</td></tr>",
     "<tr><td>section_&lt;剖面名&gt;_units／_profile／_faults／_frame／_labels</td><td>各剖面的地質剖面圖，各自成圖層；剖面座標：x＝自起點起算的距離（0 起），y＝高程×垂直誇大</td></tr>"),
    ("繪於 QGIS 地質圖下方。", "x＝自起點起算的距離，y＝高程。"),
],
"zh_CN": [
    ("<code>前缀_sections.qgz</code>、", "<code>前缀_section_&lt;剖面名&gt;.qgz</code>（每个剖面一个）、"),
    ('<p><b>剖面工程</b>：<code>前缀_sections.qgz</code> 只包含地质剖面图',
     '<p><b>剖面工程</b>：每条剖面线在 GeoPackage 中都有各自的图层'
     '（<code>section_&lt;剖面名&gt;_units／_profile／_faults／_frame／_labels</code>，如 <code>section_A_A_units</code>），'
     '并各自存为 <code>前缀_section_&lt;剖面名&gt;.qgz</code>，可分别打开预览。每个剖面使用自己的坐标：'
     '<b>x＝自剖面起点起算的距离（左缘为 0），y＝高程</b>（垂直夸大不为 1 时乘上倍率），'
     '因此地形线左端的 y 值即为剖面起点的地表高程。每个工程只包含该剖面的地质剖面图'),
    ("它会另开一个 QGIS 窗口，当前工程不会被关闭或更改。", "第一个剖面工程会另开一个 QGIS 窗口，当前工程不会被关闭或更改。"),
    ("<tr><td>section_units／section_profile／section_faults／section_frame／section_labels</td><td>地质剖面图，以地图坐标绘于地质图下方（x＝距离、y＝高程×垂直夸大），可直接放入打印布局</td></tr>",
     "<tr><td>section_&lt;剖面名&gt;_units／_profile／_faults／_frame／_labels</td><td>各剖面的地质剖面图，各自成图层；剖面坐标：x＝自起点起算的距离（0 起），y＝高程×垂直夸大</td></tr>"),
    ("绘于 QGIS 地质图下方。", "x＝自起点起算的距离，y＝高程。"),
],
"ja": [
    ("<code>接頭辞_sections.qgz</code>、", "<code>接頭辞_section_&lt;断面名&gt;.qgz</code>（断面ごと）、"),
    ('<p><b>断面プロジェクト</b>：<code>接頭辞_sections.qgz</code> は地質断面図',
     '<p><b>断面プロジェクト</b>：断面線ごとに GeoPackage 内の別レイヤ'
     '（<code>section_&lt;断面名&gt;_units／_profile／_faults／_frame／_labels</code>、例：<code>section_A_A_units</code>）'
     'と別プロジェクト <code>接頭辞_section_&lt;断面名&gt;.qgz</code> に保存し、個別に開いて確認できます。各断面は独自の座標を使います：'
     '<b>x＝断面始点からの距離（左端が 0）、y＝標高</b>（垂直誇張が 1 でない場合は倍率を掛けた値）。'
     '地形線の左端の y は断面始点の地表標高です。各プロジェクトはその断面の地質断面図'),
    ("別の QGIS ウィンドウで開くため、現在のプロジェクトは閉じず変更もしません。",
     "最初の断面プロジェクトを別の QGIS ウィンドウで開くため、現在のプロジェクトは閉じず変更もしません。"),
    ("<tr><td>section_units／section_profile／section_faults／section_frame／section_labels</td><td>地図座標で地質図の下に配置した断面図（x＝距離、y＝標高×垂直誇張）。印刷レイアウトにそのまま使えます</td></tr>",
     "<tr><td>section_&lt;断面名&gt;_units／_profile／_faults／_frame／_labels</td><td>断面ごとのレイヤに分けた断面図。断面座標：x＝始点からの距離（0 から）、y＝標高×垂直誇張</td></tr>"),
    ("QGIS で地質図の下に描かれます。", "x＝始点からの距離、y＝標高。"),
],
}

for lang, pairs in REP.items():
    p = os.path.join(HELP, lang, "index.html")
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        if b in s:
            continue
        assert a in s, (lang, a[:60])
        s = s.replace(a, b, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print(lang, "ok")

# tool help + option label
p = os.path.join(ROOT, "autotrace_strat_boundary", "i18n_model3d.py")
s = io.open(p, encoding="utf-8").read()
for a, b in [
    ("prefix_sections.qgz). The sections open in a new QGIS window",
     "one prefix_section_<name>.qgz per section, each section in its own GeoPackage layers with x = distance from 0 and "
     "y = elevation). The first section opens in a new QGIS window"),
    ("前綴_sections.qgz）；", "每個剖面一個 前綴_section_<剖面名>.qgz，各剖面在 GeoPackage 中各自成圖層，x＝自 0 起算的距離、y＝高程）；"),
    ("前缀_sections.qgz）；", "每个剖面一个 前缀_section_<剖面名>.qgz，各剖面在 GeoPackage 中各自成图层，x＝自 0 起算的距离、y＝高程）；"),
    ("接頭辞_sections.qgz）。", "断面ごとの 接頭辞_section_<断面名>.qgz。各断面は GeoPackage の別レイヤで x＝0 からの距離、y＝標高）。"),
    ('"en": "Open the sections in a new QGIS window (new project)"', '"en": "Open the first section project in a new QGIS window"'),
    ('"zh_TW": "以新的 QGIS 專案（另開視窗）開啟地質剖面"', '"zh_TW": "以新的 QGIS 視窗開啟第一個剖面專案"'),
    ('"zh_CN": "以新的 QGIS 工程（另开窗口）打开地质剖面"', '"zh_CN": "以新的 QGIS 窗口打开第一个剖面工程"'),
    ('"ja": "地質断面を新しい QGIS プロジェクト（別ウィンドウ）で開く"', '"ja": "最初の断面プロジェクトを新しい QGIS ウィンドウで開く"'),
]:
    assert a in s, a[:50]
    s = s.replace(a, b, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("i18n ok")
