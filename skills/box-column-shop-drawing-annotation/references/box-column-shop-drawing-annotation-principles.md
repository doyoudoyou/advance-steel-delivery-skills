# BOX 柱施工圖讀圖、線條分類與標註準則

- 版本：2.1
- 歷史專案正式來源：`<USER_HOME>/Documents\AdvanceSteelTools\workflows\box-column-shop-drawing-annotation-principles.md`（來源 evidence，非本機路徑）。
- 本機預期準則：`<USER_HOME>/Documents/AdvanceSteelTools/workflows/box-column-shop-drawing-annotation-principles.md`，目前缺失；本機根僅 CSV，亦缺 `tools/box_column_v84_standard.py`、`config/box-column-v84-standard.json` 及正式專案閘門檔。只讀可使用本技能規則；任何修改／產圖先逐件確認存在及版本，缺件 fail closed。
- 預設 DSM／Drawing Style：`BOX_COLUMN_V84_STANDARD`
- 案例基礎：業主 C-1 BOX 柱施工圖

> 任何 BOX 柱分析、DSM、Point Rule、原生尺寸或 AS 自動化工作前，必須先閱讀本檔及專案正式來源。

## BOX 柱 V84 預設標準

- 所有新 BOX 柱構件圖預設用 V84 profile fresh generate：`DetailStyle 32220`，style map `31003 / Order 5 / ObjQualifierSet 1`，固定 A3、1:15。
- 開工前必須執行 `python tools/box_column_v84_standard.py`；只有 `success=true`、`after_failures=[]` 才能產圖。style map 漂移時才使用 `--activate`。
- 設定清單與 golden artifacts：`config/box-column-v84-standard.json`。
- V84 是 DSM／Drawing Style 起始基準；C-1 專用幾何 qualifiers 和尺寸數字不得硬套到其他 BOX 柱，必須按新模型 BOM、Mark、Model Role、幾何及物理端點調整。
- 禁止複製 standalone C-1 detail 作為新柱圖面；必須複製來源模型並由 registered model context fresh generate。
- 最終仍須補齊原生 labels、全圖避讓、Save／close／reopen、Document Manager native plot 與 regression。

## 核心原則

1. 先理解構件語意，再建立尺寸。
2. 以 BOM、Part Mark、兩個主視圖、剖面、引線及模型資料交叉確認零件身分。
3. Main Part 是母構件；底板、連接板、加勁板、固定件與折板都要說明從屬關係。
4. 每條尺寸必須記錄起終物件、真實端點、方向及下料／鑽孔／組立／安裝用途。
5. 只接受連結到真實 detail geometry 的 native AS dimension。
6. 參考圖只能用來理解製作關係，不能把參考數值強加到不同模型 revision。
7. 視圖鏡像時順序可反向，但物理參考關係不能改變。
8. 組立圖只表達組立、定位、孔群、方向及必要焊接關係；不重複單件圖已完整負責的外形尺寸。
9. 每一方向先指定唯一主 datum；長向尺寸依局部／定位／總尺寸三排配置。
10. North 與 West 各自只負責其面向附件與孔群；A-A 負責底板／孔群，B-B 每條 side chain 只允許一個物理用途。
11. 附屬件與孔位標註必須和零件位於 Main Part 的同一物理側，但只移動／建立真正服務該附屬件的獨立 native chain。Top View 中連接板在上方，僅其孔群、孔距、孔邊距及局部定位鏈放上方。若現有 `AstDimLineRepr` 同時混有 Main Part 長度、柱端定位及孔距，必須先按物理用途拆分／重建；禁止把整個混合尺寸物件 MOVE 到 Main Part 上方。

## 讀圖順序

```text
BOM → Main Part → 底板／端板 → 連接板／加勁板／固定件／折板
→ 正交主視圖 → 剖面 → 零件從屬關係 → 標註目的
→ 真實端點 → 原生尺寸 → 另一視圖與尺寸總和驗證
```

## 物件分類

### Main Part

- BOM 中唯一大型 BOX 構件。
- 長向視圖中最長且連續的主輪廓。
- 剖面中最大的封閉斷面。
- 其他板件與孔群以它為 datum。
- BOX 內輪廓代表空腔與壁厚，不是獨立板件。

### 底板／端板

- 單件大型厚板，外形大於 BOX 斷面。
- 長向視圖中垂直柱軸；剖面中包住 BOX。
- 標註長、寬、厚、BOX 位置、孔徑、孔數、pitch、gauge、邊距及周邊加勁件。

### 連接板

- 正視為完整板面，側視為兩條接近平行線，剖面為窄矩形。
- 標註長、寬、厚、數量、距柱端、突出量、孔群、安裝面及焊接關係。

### 加勁板／短加勁件

- 短、重複，沿 BOX 或底板周邊配置。
- 位置通常與底板、孔群、連接板或集中力相對應。
- 標註尺寸、數量、配置面、間距及焊接邊。

### 固定件／折板

- 剖面呈斜邊、折角、回折或不規則輪廓。
- 必須區分斜邊實長、水平投影及垂直投影。
- 禁止用 aligned length 取代真正需要的水平／垂直定位尺寸。

### 孔／螺栓特徵

- 正視孔面為圓＋中心十字；側視為虛線或窄投影。
- 標註孔數、孔徑、排數、pitch、gauge、首末孔邊距。
- 以孔所在板件的板邊／中心為 datum。

## 線條分類

| 線條 | 判讀 | 驗證 |
|---|---|---|
| 長且連續粗實線 | Main Part 外輪廓 | BOM＋主視圖＋剖面 |
| 封閉雙層方框 | BOX 外／內輪廓 | 壁厚與空腔 |
| 接近平行雙線 | 板厚或 BOX 壁 | 正交視圖 |
| 短矩形重複 | 加勁／固定扁鋼 | 數量、Mark、剖面 |
| 斜線／折線 | 折板／固定件 | 另一視圖＋Mark |
| 圓＋中心十字 | 孔 | 孔徑、數量、所在板 |
| 虛線 | 隱藏邊／背面孔／內部板 | 不可當中心線 |
| 點畫線 | 中心／對稱軸 | 可作 datum |

## Datum 優先順序

1. 底板面／柱端面。
2. BOX 中心線。
3. BOX 外壁／內壁。
4. 所屬板件板邊。
5. 孔中心。
6. 折板真實折點／端點。

## 標註層級

1. 組立控制尺寸：總長、Main Part 長度、最大突出量。
2. 主要定位尺寸：連接區距柱端、板件相對 BOX、底板與孔群位置。
3. 製作尺寸：板厚、板面尺寸、加勁件、折板投影、孔距及邊距。
4. 資訊標註：Mark、數量、材質、焊接、方向及剖面名稱。

## 尺寸鏈規則

- 一條鏈只表達一組連續製作關係。
- 板厚的兩個延伸點必須落在同一塊板的兩面。
- 尺寸鏈總和應對應外部控制尺寸。
- 不得混合不同深度、不同面或同 Model Role 的非目標零件。
- 同角色有多片零件時，要用位置、Mark、qualifier、Main Part side 等條件隔離。
- 視圖鏡像只改變順序，不改變參考物。

## 業主 C-1 B-B 個案（非通用固定數值）

```text
Top:    206 / 15 / 180
Middle: 50 / 190 / 160
Left:   180 / 15 / 206
Right:  151 / 62 / 162
Bottom: 156 / 15 / 229
```

- `15` 是相關薄板板厚。
- `62` 是折板端點的垂直投影，不是 aligned length。
- 其他分段將板件／折板定位到 BOX 控制邊。
- North／West 與 South／East 方向相反時順序可鏡像。
- 以上數字只屬 C-1；其他 BOX 柱必須重新讀取幾何。

## 業主 C-1 Top View DSM 同側實作（已驗證）

C-1 USER Top View 使用 `DetViewRequest 32222`／`DimStrategy 32226` 時：

- `DetViewDimRequestLinear 32251` 是上方連接板孔群／板邊鏈，必須 `ArrangeAbove=1`。
- `DetViewDimRequestLinear 32253` 是 `6715` 總長鏈，維持 `ArrangeAbove=0`。
- `DetViewDimStrategyItems` 中 `Key=32226, RequestLinear=32251` 只能保留一筆；重複掛載會造成重複／合併污染。已驗證保留 Order `11`，總長 `32253` 使用 Order `17`。
- 禁止 post-process MOVE 混合尺寸鏈。修改 DSM 後必須重啟 AS，從模型複本 fresh generate，再用 Document Manager native plot 驗證。
- 已修正工具 `tools/apply_c1_a3_1_15_dsm_style.py`，不得再把 `32251` 與 `32253` 一起設為 `ArrangeAbove=0`。

## Advance Steel 強制流程

1. 複製來源模型 DWG到測試資料夾。
2. 從模型複本 fresh generate，保持 model/detail registration。
3. 盤點 Main Part、附屬件、Mark、Model Role、handle、bbox、相對位置。
4. 為每個尺寸建立語意表：目的、起點、終點、方向、視圖、預期及容許差。
5. 先做單一 side／單一 rule isolation trial。
6. 確認只命中目標物件後才整合。
7. 使用 OSNAP END／native detail point，不用任意 paper coordinate。
8. 驗證每條尺寸新增的 `AstDimLineRepr`。
9. Save、關閉、重開驗證持久化。
10. 使用 Document Manager native batch plot。
11. 檢查尺寸值、位置、重疊、圖框與物理端點依據。
12. 全部通過後才套用正式 registered detail。

## 禁止事項

- 複製參考 DWG 尺寸／區塊到正式 detail。
- 硬改 dimension text、普通 AutoCAD DIM、遮罩或 PDF 後處理偽造結果。
- 沒有物理端點依據的任意座標標註。
- 找不到 detail／view 時選第一筆或固定座標繼續。
- 把所有附屬件 contour points 混入同一 rule。
- 未備份即修改正式 DWG 或 AstorDetails。

## 驗收

- [ ] Main Part 經 BOM、主視圖及剖面確認。
- [ ] 各附屬件有 Mark／幾何依據。
- [ ] 每條尺寸有起終物件與物理端點。
- [ ] 孔數、孔徑、pitch、gauge、邊距完整。
- [ ] 折板尺寸方向正確。
- [ ] 尺寸為 native `AstDimLineRepr`。
- [ ] Save／重開後存在。
- [ ] Document Manager native PDF／PNG 通過。
- [ ] 無重疊、超框、重複或無製作意義尺寸。
- [ ] 附屬件的獨立孔位／局部定位鏈位於 Main Part 的同一物理側；混合用途尺寸物件已先拆分，沒有整條跨側搬移。
- [ ] 報告保存物件、端點、handle、預期及實際結果。

> BOX 柱標註必須先辨識物理功能，再依柱端面、BOX 中心／壁面、板邊、孔中心及折點建立具製作意義的原生尺寸；不得照抄參考數值或強制標註無語意輪廓點。
