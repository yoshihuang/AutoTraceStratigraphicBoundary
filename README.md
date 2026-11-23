# AutoTrace Stratigraphic Boundary (QGIS plugin)

地層邊界自動追蹤 · 地层边界自动追踪 · 地層境界自動トレース

Predicts stratigraphic boundary outcrop lines from outcrop points (dip / dip direction, upper / lower unit codes) and a
DEM using the **structure-contour method**. The lines stop at faults, and the plugin builds a geological map from the edited lines.

依**構造等高線原理**，由地層邊界露頭點（傾角、傾向、上下層代號）與 DEM 預判地層邊界線，遇斷層即停止並接於斷層上；
編修後可與斷層一起產生地質圖。

## Video tutorials / 操作影片

| Language / 語言 | Video / 影片 |
|---|---|
| 繁體中文 | [功能介紹與操作說明](https://youtu.be/5PLR4HU3O1w) |
| English | [Introduction and step-by-step operation](https://youtu.be/risDZpzG0dE) |

| # | Requirement / 需求 | Where |
|---|---|---|
| 1 | Points + DEM → lines extended to both sides along dip/dip-direction (temporary layer) | *Trace predicted boundary lines* (`core/tracer.py`) |
| 2 | Stop at faults and end on the fault | fault blocks + clipping (`core/tracer.py`) |
| 3 | Same upper & lower code → lines joined end to end | IDW-blended planes per block + gap joining |
| 4 | Edited lines + faults → new geology layer | *Build geological map* (`core/geology_builder.py`) |
| 5 | Download the sample project & GeoPackage | menu *Download sample project and data…* (`data/case_sample.zip`) |
| 6 | Principle & user guide | menu *Principle and user guide* (`help/<lang>/index.html`) |
| 7 | Geology → 3D geological model + geological sections, exported to GeoPackage and 3D CAD | *Build 3D geological model and sections* (`core/model3d.py`, `core/model_outputs.py`, `core/export3d.py`, `viewer3d/`) |

Languages: English, 繁體中文, 简体中文, 日本語. The language follows the QGIS locale and can be switched in the plugin menu.
Supports QGIS 3.22 – 4.x (Qt5 and Qt6).

## Layout

```
autotrace_strat_boundary/      ← the plugin (this folder goes into the zip)
  metadata.txt, LICENSE, __init__.py, plugin.py
  compat.py                    QGIS 3 / QGIS 4 enum & field-type compatibility
  i18n.py                      all UI strings (en / zh_TW / zh_CN / ja)
  core/tracer.py               structure-contour tracing (NumPy + GDAL contour)
  core/geology_builder.py      polygonize + unit labelling
  core/model3d.py              implicit potential-field 3D model (cubic RBF, faults, series)
  core/mesh.py                 marching tetrahedra (numpy)
  core/model_outputs.py        solids, interfaces, fault planes, terrain, sections
  core/export3d.py             DXF (polyface) / OBJ + MTL / STL
  viewer3d/                    offline three.js viewer template (three.js MIT licence)
  processing_provider/         Processing algorithms (toolbox, batch, models)
  help/<lang>/index.html       guide; help/img/*.png figures made from the sample data
  data/case_sample.zip          sample project (case.qgz, data.gpkg, DEM.tif)
dev/                           test & build scripts (not shipped)
```

## Development

Run the tests with the Python of a QGIS installation, e.g.

```
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_trace.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_geo.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_processing.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_gui.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_load.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_model3d.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_mesh.py
"C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" dev\test_model_alg.py C:\temp\m3d\c19_model.gpkg
```

`dev/make_sample.py` rebuilds `data/case_sample.zip` from the sample folder (empty temporary layers are dropped).

To try it in QGIS, copy (or symlink) `autotrace_strat_boundary` into
`%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` (QGIS 4: `...\QGIS\QGIS4\...`) and enable it in
*Plugins ▸ Manage and Install Plugins*.

## Publishing to plugins.qgis.org

1. Fill in `author`, `email`, `homepage`, `repository`, `tracker` in `metadata.txt` (the repository must be public, e.g. GitHub).
2. `python dev/package.py` → `dist/autotrace_strat_boundary-<version>.zip`.
3. Sign in at <https://plugins.qgis.org> with an OSGeo ID → *Upload a plugin* → choose the zip.
4. New plugins are reviewed by the QGIS team. Set `experimental=True` in `metadata.txt` for test versions, `False` for stable releases.

License: GNU GPL v2 or later.
