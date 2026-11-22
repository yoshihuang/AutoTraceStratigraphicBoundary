# -*- coding: utf-8 -*-
"""Guide update for 1.2: folds, map drape, separate CAD output files (idempotent)."""
import io
import os
import re

HELP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "autotrace_strat_boundary", "help")

ROWS = {
    "en": '''<tr><td>Fold axial traces (trend, plunge, type, name)</td><td>At a fold hinge the bedding contains the fold axis, so points along every axial trace become attitude constraints (trend empty = along the trace, plunge empty = 0). Fold axes are drawn in the 3D viewer, marked on the sections and saved as <code>fold_axes_3d</code>.</td></tr>
<tr><td>Map layers draped on the terrain</td><td>Default: the layers visible in QGIS. They are rendered and draped on the terrain of the 3D viewer and the OBJ file, and saved as <code>*_map.png</code> + <code>.pgw</code>.</td></tr>
<tr><td>Output files</td><td>GeoPackage, DXF (polyface meshes, one layer per unit), OBJ + MTL (colours, textured terrain), STL (one file per unit, off by default) and the 3D viewer: each with its own file name and folder; skip any of them. Outputs left as temporary files are written next to the GeoPackage.</td></tr>''',
    "zh_TW": '''<tr><td>褶皺軸跡（趨向、傾沒角、類型、名稱）</td><td>褶皺樞紐處的地層面包含褶皺軸，因此沿軸跡的取樣點會成為位態條件（趨向空白＝沿軸跡方向，傾沒角空白＝0）。褶皺軸會顯示於 3D 檢視器、標示於剖面上，並存成 <code>fold_axes_3d</code>。</td></tr>
<tr><td>貼在地形面上的地圖圖層</td><td>預設為 QGIS 中目前顯示的圖層，繪製後貼在 3D 檢視器與 OBJ 的地形面上，並存成 <code>*_map.png</code>＋<code>.pgw</code>。</td></tr>
<tr><td>輸出檔案</td><td>GeoPackage、DXF（polyface mesh，每個地層一個圖層）、OBJ + MTL（含顏色與地形貼圖）、STL（每個地層一個檔案，預設不輸出）與 3D 檢視器，可各自指定檔名與資料夾，也可略過；保留為暫存檔者會存在 GeoPackage 同一資料夾。</td></tr>''',
    "zh_CN": '''<tr><td>褶皱轴迹（趋向、倾伏角、类型、名称）</td><td>褶皱枢纽处的地层面包含褶皱轴，因此沿轴迹的采样点会成为产状条件（趋向空白＝沿轴迹方向，倾伏角空白＝0）。褶皱轴会显示于 3D 查看器、标示于剖面上，并存为 <code>fold_axes_3d</code>。</td></tr>
<tr><td>贴在地形面上的地图图层</td><td>默认为 QGIS 中当前显示的图层，绘制后贴在 3D 查看器与 OBJ 的地形面上，并存为 <code>*_map.png</code>＋<code>.pgw</code>。</td></tr>
<tr><td>输出文件</td><td>GeoPackage、DXF（polyface mesh，每个地层一个图层）、OBJ + MTL（含颜色与地形贴图）、STL（每个地层一个文件，默认不输出）与 3D 查看器，可各自指定文件名与文件夹，也可跳过；保留为临时文件者会存在 GeoPackage 同一文件夹。</td></tr>''',
    "ja": '''<tr><td>褶曲軸跡（トレンド、プランジ、種類、名称）</td><td>ヒンジでは地層面が褶曲軸を含むため、軸跡上の点が姿勢条件になります（トレンド空欄＝軸跡の方向、プランジ空欄＝0）。褶曲軸は 3D ビューアに表示し、断面に記号を付け、<code>fold_axes_3d</code> に保存します。</td></tr>
<tr><td>地形面に貼る地図レイヤ</td><td>既定は QGIS で表示中のレイヤ。描画して 3D ビューアと OBJ の地形面に貼り、<code>*_map.png</code>＋<code>.pgw</code> として保存します。</td></tr>
<tr><td>出力ファイル</td><td>GeoPackage、DXF（polyface mesh、地層ごとのレイヤ）、OBJ + MTL（色・地形テクスチャ付き）、STL（地層ごと、既定は出力しない）、3D ビューアをそれぞれ別のファイル名・フォルダに保存でき、省略もできます。一時ファイルのままの出力は GeoPackage と同じフォルダに保存します。</td></tr>''',
}

for lang, rows in ROWS.items():
    p = os.path.join(HELP, lang, "index.html")
    s = io.open(p, encoding="utf-8").read()
    if "fold_axes_3d" in s:
        print(lang, "already updated")
        continue
    i = s.index('id="model3d"')
    m = re.compile(r"<tr><td>3D CAD[^<]*</td><td>.*?</td></tr>").search(s, i)
    assert m, lang
    s = s[:m.start()] + rows + s[m.end():]
    # outputs table: add fold_axes_3d next to the fault planes
    s = s.replace("<tr><td>section_fences_3d</td>",
                  "<tr><td>fold_axes_3d</td><td>%s</td></tr>\n<tr><td>section_fences_3d</td>" % {
                      "en": "Fold axial traces draped on the terrain",
                      "zh_TW": "貼合地形面的褶皺軸跡", "zh_CN": "贴合地形面的褶皱轴迹", "ja": "地形面に沿わせた褶曲軸跡"}[lang], 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print(lang, "ok")
