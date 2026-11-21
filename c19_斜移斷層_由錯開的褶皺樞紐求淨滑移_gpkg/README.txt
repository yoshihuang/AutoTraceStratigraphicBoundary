地質圖判釋工作台：QGIS GeoPackage 範例

來源：斜移斷層：由錯開的褶皺樞紐求淨滑移
座標系統：EPSG:3826（TWD97 / TM2 121）。內建範例的座標為示範用的虛擬位置。

圖層與欄位：
  geology（MultiPolygon）: unit_code, unit_name, strat_order, series, thick_m, kind
  aureole（MultiPolygon）: name  （接觸變質帶）
  subcrop（MultiPolygon）: unit_code, unit_name, strat_order, series, thick_m, kind  （潛露圖）
  faults（LineString）: name, dip, dip_dir
  fold_axes（LineString）: type, label, fold, trend, plunge  （褶皺軸跡）
  fold_domes（Point）: type, label  （穹窿與盆地）
  contours（LineString）: elev, index
  bedding（Point）: dip, dip_dir, overturned, unit_code
  cleavage（Point）: dip, dip_dir  （軸面劈理）
  boreholes（Point）: name
  section_line（LineString）: name
（本範例沒有的圖徵，對應圖層保留為空圖層，方便當作範本。）

位相檢核：
  geology: 通過（31 條共用邊界、0 個多邊形環錯誤、面積 4000000 m²）
  地質區與潛露圖的多邊形以共用邊界組成，彼此不重疊、無縫隙，且完整覆蓋圖幅。

使用方式：
1. 在 QGIS 中開啟 .gpkg（拖曳到圖層面板即可），圖層會自動套用內含的樣式。
2. 參照這些圖層的結構，把自己的地質圖整理成相同格式：地質區必須是多邊形且有地層代號欄位；位態點要有傾角與傾向（或走向）；等高線要有高程欄位。
3. strat_order（1＝最老）、series（不整合以上為較大的數字）、thick_m（m）與 kind（sed／ign）若有填寫，匯入時會直接採用，不再自動推定。修正模型時改這幾個欄位即可。
4. 在工作台「匯入 GPKG」分頁上傳修正後的檔案，網頁會自動判斷圖層用途並建立模型。