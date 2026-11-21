# AutoTrace Stratigraphic Boundary (QGIS plugin)

地層邊界自動追蹤 · 地层边界自动追踪 · 地層境界自動トレース

Predicts stratigraphic boundary outcrop lines from outcrop points (dip / dip direction, upper / lower unit codes) and a
DEM using the **structure-contour method**. The lines stop at faults, and the plugin builds a geological map from the edited lines.

依**構造等高線原理**，由地層邊界露頭點（傾角、傾向、上下層代號）與 DEM 預判地層邊界線，遇斷層即停止並接於斷層上；
編修後可與斷層一起產生地質圖。

| # | Requirement / 需求 | Where |
|---|---|---|
| 1 | Points + DEM → lines extended to both sides along dip/dip-direction (temporary layer) | *Trace predicted boundary lines* (`core/tracer.py`) |
| 2 | Stop at faults and end on the fault | fault blocks + clipping (`core/tracer.py`) |
| 3 | Same upper & lower code → lines joined end to end | IDW-blended planes per block + gap joining |
| 4 | Edited lines + faults → new geology layer | *Build geological map* (`core/geology_builder.py`) |
| 5 | Download the sample project & GeoPackage | menu *Download sample project and data…* (`data/c19_sample.zip`) |
| 6 | Principle & user guide | menu *Principle and user guide* (`help/<lang>/index.html`) |

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
  processing_provider/         Processing algorithms (toolbox, batch, models)
  help/<lang>/index.html       guide; help/img/*.png figures made from the sample data
  data/c19_sample.zip          sample project (C19.qgz, GeoPackage, DEM)
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
```

To try it in QGIS, copy (or symlink) `autotrace_strat_boundary` into
`%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` (QGIS 4: `...\QGIS\QGIS4\...`) and enable it in
*Plugins ▸ Manage and Install Plugins*.

## Publishing to plugins.qgis.org

1. Fill in `author`, `email`, `homepage`, `repository`, `tracker` in `metadata.txt` (the repository must be public, e.g. GitHub).
2. `python dev/package.py` → `dist/autotrace_strat_boundary-<version>.zip`.
3. Sign in at <https://plugins.qgis.org> with an OSGeo ID → *Upload a plugin* → choose the zip.
4. New plugins are reviewed by the QGIS team. `experimental=True` is recommended for the first versions.

License: GNU GPL v2 or later.
