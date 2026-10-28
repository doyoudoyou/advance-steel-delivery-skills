---
name: advance-steel-frame-and-delivery
description: "Use when replacing CAD frames or packaging AS drawings."
version: 0.1.0
platforms: [windows]
metadata:
  hermes:
    tags: [advance-steel, drawing-frame, native-plot, explode, delivery]
    related_skills: [autocad-automation, pdf]
---

# Advance Steel 換框、出圖與完整交付

適用：整套專案換框、圖號與檔名整理、原生 PDF、零件 ModelSpace 1:1 DWG 分類及完整交付。只要求流程說明或審查時不執行 CAD 修改。此 skill 不授權新的前景操作、保存未存檔或更動 production baseline。

## 專案工作根目錄與暫存清理

- 預設工作根目錄為 `D:\施工圖交付\專案名稱`（本機無 D: 槽時改用 `C:\施工圖交付\專案名稱` 並在回報中說明）；`專案名稱` 是佔位名稱，執行前使用已確認的實際專案名稱。使用者指定其他路徑時，以本案指定路徑為準；尚無實際名稱時先詢問，不擅自建立名為「專案名稱」的資料夾。
- 所有可控制的專案產物依下列固定結構集中在工作根目錄下，保留資料夾名稱與順序：

```text
D:\施工圖交付\專案名稱
├─ 01_接收原檔/       原始 DWG、PDF、ZIP、圖框及參考資料
├─ 02_工作暫存/       解壓、修改副本、試排、測試輸出
├─ 03_待確認交付/     提供使用者檢查的 DWG、PDF、ZIP
├─ 04_正式交付/       已確認的交付版本
└─ 05_交付紀錄/       檔案清單、來源對照、驗證結果及清理紀錄
```

- 接收原檔保留不動，修改、解壓、試排及測試皆使用工作暫存中的副本；暫存按批次分目錄，避免跨批次覆蓋或誤清。
- 專案輸出、報告、截圖、腳本、可配置的暫存與交付包都放在上述根目錄。工具自身快取、系統暫存及無法配置位置的軟體產物不在此承諾內；遵守執行環境的 scratch 規則，必要的專案證據另存到交付紀錄。
- 正式交付必須包含所需模型、sidecar、外部參考及其他依賴，不可依賴即將清除的工作暫存。交付前依既有驗收流程核對完整性、檔案清單、hash、ZIP read-back及適用的原生重開。
- 只有使用者明確確認本批次交付後，才執行本批次暫存清理；交付確認不授權刪除其他批次。先唯讀列出精確目標及影響，核對沒有開啟中檔案、交付唯一副本或尚未保存的必要證據，並確認目標實際路徑位於 `02_工作暫存/` 的本批次子目錄內，不沿 junction／symlink 清除根目錄外的內容。
- 使用者的「交付確認後清除本批次工作暫存」為此範圍的條件式清理授權；條件未成立、範圍不明或存在必要依賴時停止並詢問。永久刪除遵守工具的破壞性操作核准機制。接收原檔、正式交付與交付紀錄永遠保留；`03_待確認交付/` 不自動納入清理。
- 清理前將本批次必要驗證證據與清理清單保存至 `05_交付紀錄/`，完成後讀回核對暫存清理結果及保留檔案完整性，再回報實際刪除與跳過項目。不要以已打包或已產生PDF代替使用者的交付確認。

## 同工程衍生分案（「用一樣的流程」）

使用者上傳 detached DWG ZIP 並說是某案的同專案衍生工程時，不重新設計流程：
1. 先找最近的同工程整理資料夾（`Documents/*_整理_YYYYMMDD`，以及 `C:\施工圖交付\<前案>\05_交付紀錄\scripts`），讀其 prepare/process/build_delivery/final_check 與交付說明；沿用圖框 donor、ED 標準圖、已置中的封面 DWG（只替換案名文字）。步驟與路徑見 references/local-implementation.md。
2. 同名案若曾交付過（使用者重傳新版來源），先以 sha256 比對新舊來源（相同／變更／新增／移除）並在回報列出，全部依新來源重做；沿用前次已確認的決策（圖號前綴、圖號清單超過 20 列分 AL-001/AL-002、安裝圖舊修訂表清除方式、圖名），不另行發明。
3. 新圖名（例如安裝圖依內容命名）屬自行判斷時，在回報中列為「需確認」。重傳版新增構件時 GA 流水號會依自然排序整批位移；在回報列出新舊圖號對照並提醒現場若已用舊圖號要注意，不為保留舊號而跳號（除非使用者要求）。
4. 先跑封面、圖號清單、一張構件圖、一張多框安裝圖試作並目視，再跑全部。
5. 交付包放 `03_待確認交付`；使用者回覆可交付後，hash 核對搬到 `04_正式交付`，再清本批次 `02_工作暫存`（清單存 `05_交付紀錄`），重核接收原檔 hash。使用者單字回覆「交付」「可以交付」即為此搬移＋本批次清理的確認。
6. 每案完成後把本批腳本（含 jobs.json、construction_index.json）複製到 `05_交付紀錄/scripts`，作為下一分案的起點。

7. 零件圖框「專案名稱」（HYPERSTEELPAGEHEADER 的 PROJECT 屬性）是此使用者的常設要求：空白者填入本案名稱。原生字高 3.0 會壓到格底線，使用者要的是縮小：字高 2.5、BaseLeft 對齊點 Y=18.5（標籤底 Y≈22.6、格線 Y=18，上下都留空）。來源已是本案名者只統一字高位置（refit；使用者沒特別要求時也照做，整案可能全部已填、全部 refit，回報要說清「不用補填、只統一字高」），有其他值者保留不改並列出。新案在 process.py 的零件 copy 模式直接做（CaseETool `STPROJFILL`），零件因此不再與來源逐位元相同，交付說明要改寫該句並列出 filled／refit／kept 張數。
8. 已交付後的局部修訂：先唯讀調查全部目標檔現值；只改指定屬性，每張存檔→重開→逐 handle 比對其餘實體不變（含該屬性之 header 的 extent 例外）→重出 PDF→重組受影響的冊。新包以「除變更清單外逐檔 hash 與前版相同」驗證，放 `03_待確認交付` 用新檔名；確認後取代 `04_正式交付` 時舊版改名 `_舊版_<日期>_<說明>` 保留，不刪除。
9. 同名案重傳新版來源：新原檔放 `01_接收原檔/<批次名>/`，前版原檔與其 hash 清單保留；工作暫存與交付包用新批次名（如 `b02_revB`、`_B版_交付包.zip`），hash 清單另存 `received-<批次>-sha256.txt`。
10. 圖框窗檢查抱「工程實體不在任何頁」時，先列出全部超框實體的類型、文字與包絡範圍；若是遠離圖紙（數千 mm 外）的孤立標記文字，用「檔名＋類型＋文字＋座標門檻」精確規則列入 OFFSHEET（不移動、不刪、不列印），寫進交付說明與交付檢查 JSON，並在回報「需要你確認的」提醒使用者若應在圖內請修原檔——只記在 offsheet_warnings.json 使用者看不到。
11. 前版不在 `04_正式交付`（例如只在 `Documents/<案>_整理_<日期>`）時，建立標準五層結構，新版直接進 04，舊整理資料夾不搬不動，在回報說明。新舊來源比對用舊整理資料夾的 `source/*.dwg` 即時算 sha256。
12. `03_待確認交付` 的舊版資料夾搬不動（Permission denied）通常是使用者開著檔案：請使用者關閉後再複製保存到暫存區、再刪除，刪除前要核准；不強制結束使用者程序。
13. 重用前版腳本時，先 grep build_delivery 交付說明裡寫死的版本敘述（版次、日期、張數、「多頁共用比例」等針對某構件的句子），依本版盤點結果改寫；來源結構會變（例如多頁構件拆成新構件、某些構件改帶已換好的 A$C 框），沿用舊句會寫出錯誤說明。
14. 引用前版比例／圖號時只讀 `scripts/jobs.json` 的 `pages[].Scale`／`Number`，不要讀 `施工圖號_來源對照表.csv`——其第 4 欄是「施工圖冊頁次」，數字形似比例，曾被誤報成 1:10／1:11。
15. 零件圖身分核對：prepare 後、process 前，逐張比對檔名標記與 HYPERSTEELPAGEHEADER 的 `POS_NUM` 屬性（PDF 文字的 `Mkd X` 為旁證）；不符者再比對它與同標記檔的 hash、前版同名檔內容，以及原零件是否已從本批來源消失。檔名與內容不符是來源匯出錯誤，不自行改名、不靜默收錄；停下給使用者三選一：重新匯出（建議）／照收並在交付說明註明／不收錄。選不收錄時在 build_delivery 與 final_check 用同一個 `EXCLUDED={key:原因}` 過濾 jobs，零件張數斷言減去 EXCLUDED，原因寫進交付說明與交付檢查 JSON；原檔留在接收區不刪。之後使用者說「捨棄」＝不補發、不追蹤，決定另記在 `05_交付紀錄`，並指出已交付說明中「待補發」字句與決定不一致、詢問是否重打包，不擅自改正式交付。
16. 全套 inventory（每張 Core Console 開檔）會超過前景 terminal 逾時：一律背景執行＋notify。背景指令尾端的 `grep -c` 在 0 筆時 exit 1，通知的 exit code 不代表盤點失敗——先讀 log 與輸出數（如 inventory 目錄數＝來源 DWG 數）再判斷。work/probe 兩步都要「輸出檔已存在就 cached 跳過」，中斷重跑時先刪掉不完整的單張輸出目錄（只刪那幾張）再跑。final_check 開頭斷言 `fresh_extract` 不存在、build_delivery 斷言 03 目標不存在：重出交付包前先清 `03_待確認交付` 本批產物、`05_交付紀錄/qa` 與 `fresh_extract`。
17. 清理工作暫存後空資料夾常因 shell cwd 或使用者視窗而 `Device or resource busy`：清理指令先 `cd /c` 再 rm；仍失敗就回報「空資料夾待手動刪」，下次清理時順手 rmdir 前批的空殼。
18. 圖框容納預檢（inventory 後、prepare 前，對全部 [A]/[G]）：每張以 A$C 或 HYPERSTEELPAGEFRAME 範圍為準，列出框外實體數、類型統計、包絡範圍與文字樣本。分兩種：(a) 少數孤立標記文字遠在圖紙外 → 依第 10 條列 OFFSHEET；(b) 大量工程線／尺寸／剖面超出框（典型是新匯出的原生圖比例太大，構件長向立面畫出框外）→ 不可換框硬印。先用 STPLOTALL 以涵蓋全部內容的 window 出一張來源預覽 PDF 目視確認，再停下給使用者三選一：重新匯出成能放進 A3 的比例或拆張（建議，其他圖先做好、等補檔再打包）／不收錄並在交付說明註明／整張縮印（說明比例失效、字很小）。不要自行移動或縮放工程視圖。
19. 同名案重傳時，部分來源檔可能是前版交付 DWG 再存（已帶統一 `A$C` 框、比例 NTS、圖名已是本案格式）：照一般流程再換一次框，比例取框內 `比例：` 文字，並與前版 `jobs.json` 的 Scale 核對一致；在交付說明註明來源已帶統一框。來源 ZIP 夾帶的 `.bak` 等非 DWG 檔不納入處理與張數。
20. 腳本起點選擇：以「同一案」上次交付的 `05_交付紀錄/scripts*` 為底（保有該案專屬規則：圖號清單分頁、修訂表清除、安裝圖標題對應），再把其他案較新的通用改動（如零件 PROJECT 填值的 process.py、build_delivery/final_check 的零件 hash 判斷）移植進來；不要反過來拿別案腳本改案名，會漏掉本案規則。

回報格式：一句結論 → 兩冊頁數表 → 做了什麼（換框、封面、多框拆頁、零件 byte identity）→「需要你確認的」編號清單 →「還沒驗證的」→ 其他說明（路徑、工具位置）→ 下一步。

## 開源工具（detached DWG 路線）

本 repo 的 `tools/delivery-pipeline` 是這條路線的可執行實作：`DeliveryTool.dll`（Core Console 指令 DTINSPECT/DTPROBE/DTAPPLY/DTCOVER/DTINDEX/DTPLOTALL/DTCHECKFRAME/DTPROJFILL/DTSETATTR/DTATTRREAD）＋ `asdeliver` Python 步驟（inventory → prepare → process → build_delivery → contacts → final_check），所有案別差異寫在 `project.json`。工具沒有可靠依據時會停下，不會自己猜（缺圖名、缺比例、工程實體超出圖框窗、多出的 REVISIONS）。遇到這些情況，依本 skill 第 10、15、18 條問使用者，再把決定寫進設定檔的 `exempt`／`offsheet`／`excluded`。不可為了讓工具通過就放寬列印窗。

## 前置條件與範圍

- 載入 `autocad-automation`；PDF 合冊載入 `pdf`，桌面操作載入 `computer-use`。
- AdvanceSteelTools 以根目錄 AGENTS.md、DEV_STATE.md、config/production-tools.json 與對應 workflow 為準。先讀現有工作狀態及最新使用者要求，選最小有效 route、建立必要 State、跑適用 preflight。
- 先辨別主模型、sidecar、registered details、普通補充 DWG、既有輸出及目標交付範圍。
- 完整複製模型與同名 sidecar；保留登錄、DWG/UPD、Databases、prototypes。既有隔離工作集可續用，但先確認使用者修改與來源身分。
- 每次操作前取得精確 FullName、命令狀態、DBMOD 與備份/hash。未存檔不擅自 Save、Close 或 discard；先前單次保存授權不延伸到其他檔案。
- PDF 來源與最新 DWG 必須可對應。工程圖已由使用者重新排版時，舊 PDF 與舊碰撞警示不能直接當最新結果。

## 流程

### 1. 清點與分類

建立逐張 manifest：類別、registered name、DWG、UPD、原生圖號、顯示圖號、圖名、比例、hash、輸出路徑及警示。用程式去重並核對總數。
- 封面／目錄；ED 標準圖；GA 安裝圖；AS 構件圖；零件圖分流。
- 原生 GA/AS 改檔名使用 Document Manager，不以檔案系統 rename 或 SaveAs 代替。UPD 關聯一併驗證。
- 純 detached／exploded 來源的 DWG 數不等於施工圖頁數：同一 Layout 可能左右並排多張圖框。以圖框實際邊界與工程 extents 建立逐張 window，驗證所有工程實體完整落入至少一張 window；各實體圖面分別編號及列印，對照表記錄原 DWG 與分頁。交付保留多圖面的原 DWG 工程內容，對應個別 PDF 收齊所有分頁，不用固定左側 A3 window 漏掉右半張。
- 使用者要求零件只分冊、不換框／不重編號時，交付零件 DWG 與上傳來源維持 byte identity；原生列印／重開只能開一次性副本。施工圖清單只列授權分類，不能為了追溯把零件加回印刷目錄；技術 manifest 可保存來源與頁序。
- 換框前清點來源 SCALE／DRG_SCALE 屬性及視圖比例文字，保留明確來源的比例資訊，不以 donor 的 NTS 或泛稱取代已知值；PDF 若採含完整圖框的 A3 fit，需說明原圖比例與紙面列印適配的差別，不宣稱可量測1:1。
- 來源圖框已 exploded／封裝為普通 `A$C` block、無 SCALE 屬性時，在一次性副本讀取／Explode 該圖框的文字，保存原圖名、圖號、`比例：...` 與各次 block placement；不要因 attrs 為空就猜比例。來源資訊欄為 NTS、局部視圖另標 `Scale: 1:15` 等時，保留 NTS 與局部視圖標註兩者，不擅用局部比例覆蓋整張。多框由實際 placement 差值逐張建立 window，不能固定只支援兩框。
- 同一批構件圖可能混用兩種來源框：exploded `A$C` block，或原生 `HYPERSTEELPAGEFRAME`＋`HYPERSTEELPAGEHEADER`。數框時 A$C 為 0 就改數 HYPERSTEELPAGEFRAME；比例依序取 A$C 框內 `比例：` 文字 → HEADER 的 `SCALE` 屬性（如 1:7.5）→ 安裝圖「詳各視圖」／標準圖 NTS。同名案的新版來源可能已換框型，不能沿用前版的框型假設。一個 DWG 有多個 HYPERSTEELPAGEFRAME 但只有一個 HEADER 時，把該 SCALE 視為整個構件詳圖的比例套到每一頁，並在回報「需要你確認的」列出（第 2 頁起是否改標「詳各視圖」）。
- 來源只有 `HYPERSTEELPAGEFRAME` 邊框、無資訊欄或總比例時，以該框 placement 辨識頁面，不要求必有 `A$C` donor 類型；保留局部視圖比例，新增資訊欄可標「詳各視圖」，不可猜總比例或套用 donor NTS。
- 以精確來源檔名／路徑及 hash 核對零件唯一性；`S-01` 與 `S-1` 可能是不同零件。自然排序只決定頁序，不去掉前導零、不以數字化 sort key 去重，確保來源每一檔恰有一筆交付對照。
- 新顯示號用 SHEET_NO；保留 native drawing number、Assembly Number、Single Part Mark。零件不換框、不重編流水號，除非使用者另改規格。

### 2. 準備圖框

以使用者提供圖框建立專案專用 prototype，不能改全機 prototype。
- 設定工程資料、SHEET_NO、SHEET_TITLE；保留必要 legacy attributes。
- 原生 HYPERSTEELPAGEFRAME／HYPERSTEELPAGEHEADER 名称不得擅改。
- 簽核欄預設保留空白，不移植別案簽名／印章；封面是否有框依本案規格，範例案A範例要求無框。
- 圖框與資訊欄保持原始長寬比，等比例調整；禁止只縮 Y 值、壓扁字形。
- 封面送審內容文字必須落在實際儲存格上下框線內並保留間距；公司名稱在名稱列水平、垂直置中。以重新開啟的文字 bounds 與儲存格邊界核對，再看原生 PDF 高解析局部；不要只檢查全頁縮圖。舊 MText 可能保留異常 column width，造成 GeometricExtents 遠大於字形；先設 NoColumns 再調 Width／字高，避免用錯誤 bbox 反覆縮小文字。
- 封面必須用實際紙張／plot window 的中心驗證整體標題＋送審表格組合，不把來源 DWG 的排版中心當成紙張中心。計算 PDF 可見字形與表格框線的包絡，核對左右、上下留白；空白 MText 或異常分欄的巨大 bbox 不列入可見包絡。全頁接觸表的「無重疊」不能替代置中驗收。
- AutoCAD MText 段落置中控制碼使用 `\\pxqc;`，`\\qc;` 可能被當成可見文字；修改前後用 `MText.Text` 核對字面內容不變。只有 `ColumnType` 尚非 `NoColumns` 才切換，重設已是 `NoColumns` 的物件可能拋 `eNotApplicable`；空白文字不需修改分欄。保存後原生重開，再用 PDF 字形 bounds 核對置中與儲存格內間距。
- 比例及位置從當前工程範圍決定，97%、1.10、5 mm 等歷史試排值不得套成固定標準。

### 3. 換框與排版邊界

GA/AS 使用原生 prototype 流程，保留 AS native views、dimensions、labels、marks。普通 ED 在工作副本僅更動已識別圖框／資訊欄；以修改前後工程快照比對不變。
- agent 只在授權範圍調圖框、資訊欄、BOM 位置及列印偏移；工程視圖、比例、尺寸位置如需調整需取得使用者同意，並在調整完後提供給使用者審核。
- detached 圖的舊修訂表可能是紙空間獨立 `Page` 層文字及線段，不隨 HYPERSTEELPAGEHEADER 刪除而消失。換框後全套掃描 `REVISIONS`／修訂文字與周邊表格線，不能只刪 `Index`／`Date`／`Description`。依來源實體 handle、type、layer、文字、幾何範圍建立明確刪除清單；工程線可能穿過相同區域，不以矩形範圍刪除全部物件，也不遮白 PDF。原生保存／重開後證明其餘實體及圖框未變，重新列印並比對其他合冊頁不變；既有圖框短線是否為殘留以來源對照及向量／像素證據判斷，不依單張影像推論。
- 先平移；仍有裁切才考慮等比例調整圖框大小。縮框後若碰尺寸仍屬失敗。
- 純 detached 工程內容偏低、與新資訊欄會重疊時，可在授權的圖框修改範圍只下移資訊欄並延伸圖框下部邊線；文字及資訊欄不做非等比例縮放，工程視圖／尺寸／BOM 保持原位。逐張以來源 handle／屬性／幾何及保存後重開證明工程內容未變，不把圖框調整誤寫成工程排版變動。
- 接觸表視覺模型可能把留白誤判為 BOM 疊印或誤讀圖名；疑點先用單張高解析及 CAD／PDF 向量座標交叉確認，再決定修改。不可根據縮圖或影像模型的設計推論擅改來源 BOM 數量、重量或標記。
- BOM 移動 AstDetailBomWithBlockRepr 母物件，子表示隨動；不縮放、不炸開。
- BOM 左緣與資訊欄左緣對齊；BOM 底線與資訊欄上緣共線，無間距。不得為此讓工程圖穿入 BOM。
- BOM 重量字疊印若使用者明確接手，可記為豁免；其他工程碰撞與資訊欄疊印不隨之豁免。
- 不靠 generic COM bbox 或 Z=0 篩選判定 AS 詳圖無干涉；native bounds 可能是局部座標或 invalid extents。

### 4. 保存與原生出圖

修改後 Save/Close/Reopen，讀回比例、位置、物件類別、marks、DBMOD；只有通過的版本可接續出圖。
- PDF：GA/AS/零件採 Document Manager 原生 Batch plot，核對 exact DWG、layout、queue 與本次原生 report/DSD/PDF。
- GA/AS 的交付 DWG 必須另外使用 Document Manager 原生 Batch explode；不能僅交原生配置 DWG 副本。逐張核對精確圖名、完整來源路徑與 singleton queue，保留原始 DetailsExploded 輸出。
- 在獨立匯出副本中，將指定 Layout 的圖面物件（工程內容、圖框、資訊欄、尺寸、標註與 BOM 表示）複製到 ModelSpace 後存檔。排除 viewport 容器；存在多個候選 Layout、無法識別的 viewport 依賴或既有 ModelSpace 內容時先釐清，不盲目重複複製。
- GA/AS 此步為 Layout → ModelSpace 複製，保留原有尺寸、相對位置與比例，不自動還原成工程 1:1，也不自行刪除 Layout 物件。禁止直接套用會放大比例並清空 Layout 的零件 convert_exploded_layout_to_model_1to1 流程；如需1:1或清空配置，另取得明確需求。
- 複製後核對物件數量、內容及幾何比例，完成 Save/Close/Reopen、DBMOD=0，再將已保存並關閉的 detached DWG 從輸出暫存區移至與 Current-sheet-PDF/ 同層的 DWG/ 資料夾（不是 PDF 目錄內的子資料夾）。逐張以manifest綁定PDF↔DWG，不猜對應、不移走原生 Details 或 raw Explode 證據。
- 目的地缺少對應PDF或已有同名DWG時先停止並處理版本／碰撞，不覆蓋。移動前後hash須一致，讀回目的地驗證；發布中斷須有可恢復紀錄。
- 封面、目錄、ED 可走已驗證 AutoCAD 原生/Core Console 列印，不用重畫 PDF 代替 DWG。
- 使用者指定「拿既有封面 DWG 修改」時，直接複製該 DWG，在副本修改已辨識的文字及框線，保留原單位／送審表格實體；不得改用舊 PDF 白塊遮蓋或重新畫 PDF 代替。核對來源 hash、未修改實體、save/close/reopen 後原生列印，交付可編輯封面 DWG 及對應 PDF。更換合冊封面時驗其餘頁像素不變。
- 詳見 references/native-export.md。工具可能在 Document Check 前保存模型；先檢查實作與授權，不能承諾不保存卻直接呼叫。
- Core Console 的 `.scr` 以 ASCII 命令和 ASCII 路徑載入 .NET DLL；中文路徑可能在 NETLOAD 被錯誤解碼。來源／輸出中文路徑改由環境變數指向 UTF-8 JSON job，或用原生程序參數傳遞。不要把輔助腳本命名 `inspect.py`，它會遮蔽 Python 標準庫 `inspect`，使 PyMuPDF 等套件匯入失敗。
- Core Console 不支援 ActiveX（`vla-*`／`vlax-get-acad-object` 會中斷 LISP）；唯讀盤點用 `entnext`/`entget`/`dictsearch (namedobjdict) "ACAD_LAYOUT"`。`.scr` 中含空格的 Layout 名稱會被拆成多個輸入，`-PLOT` 等指令改在 LISP 內用 `(command ...)` 傳完整字串，輸出路徑經 `getenv` 傳入。
- NETLOAD 回報 `Unable to load ... assembly` 時先唯讀診斷：`(getvar "SECURELOAD")`／`TRUSTEDPATHS`、`reg query HKCU\\Software\\Autodesk\\AutoCAD /s /f TRUSTEDPATHS`（看作用中的 profile，AS 為 `<<ADVS>>`），再用 Core Console NETLOAD 一個 AutoCAD 安裝目錄內的 DLL（如 AcLayer.dll）對照；安裝目錄可載、工具目錄不可載＝安全載入阻擋。重建 DLL 不會解決。診斷指令若需核准而逾時，停下等使用者，不換寫法重試。
- 安全載入阻擋時給使用者二選一：(1) 使用者自行在 選項→檔案→信任的位置 加 `<工具目錄>\\...`；(2) 使用者明確授權後由 agent 改。授權範圍只限：先 `reg export` 該 profile 的 Variables 到 `05_交付紀錄`，只在作用中 profile 的 TRUSTEDPATHS 加工具目錄，SECURELOAD 永不改；改完以 NETLOAD 實測，回報變更與備份路徑，並請使用者決定保留或移除。不得把 DLL 搬進 AutoCAD 安裝目錄繞過。
- 呼叫 Core Console 時 DWG、`.scr`、報告路徑一律傳絕對路徑；相對路徑會讓 accoreconsole 回報 `"x.scr": Can't find file.`，指令完全沒跑卻 returncode 0，只能從「報告檔不存在」看出。
- 即使命令在另一路徑 `SaveAs` 且 `.scr` 用 `QUIT`/`_N`，Core Console 試驗仍可能回寫開啟的 input DWG；原始圖與已驗收輸出永遠只讀，命令先開一次性副本，試驗後核對來源 hash 與最終 ZIP hash。僅比較紙空間持久化時排除 layout 自動 viewport `Number=1` 的重算差異，其他實體以 handle、類別、文字、屬性及容差內幾何逐筆比對。
- 已完整的框優先只改 plot origin 置中，不為了 PDF 留白再移工程物件。列印比例等比，保留工程設定。
- 每張檢查四邊、空白頁、圖名圖號、字形、工程與 BOM/資訊欄干涉。局部疑點以高解析裁切與 PDF 向量交叉核對。
- 失敗試排保留證據，只還原明確備份目標；不回復整個模型抹去使用者新增變更。

### 5. 零件 DWG／PDF

依使用者選擇區分原生配置 DWG 副本與 ModelSpace 1:1；不能把 copy 當成 1:1 匯出。
- 已有有效原生 PDF 時，DWG 可直接 Batch explode，不強制先重跑 Batch plot。
- 精確單張入列、核對完整 Details 路徑及 singleton queue 後才 Execute。
- 保留 DetailsExploded 原始輸出，再使用 shared runtime 的 convert_exploded_layout_to_model_1to1。
- 比例必須有原生 SCALE／viewport 證據；多比例或未知值停止，不猜。
- 驗證每個 layout entity 搬入 ModelSpace、entity count、paper layout 清空、Save/Close/Reopen、DBMOD=0。此流程含圖框／標註，不自動等於無標註 CNC 幾何。
- 輸出屬 detached delivery，不取代原生 registered detail。轉換成功不代表空白 PDF 修好或工程尺寸完整性驗收通過。
- 按 references/classification-and-package.md 分類，PDF/DWG 成對且不覆蓋來源。

### 6. 合冊與完整交付

用 manifest 建立頁序，只採已確認最新 PDF；逐頁核對合併結果與來源。
- 範例案A案範例：14頁=封面、目錄、4ED、3GA、5AS；33零件另冊，不列送審目錄。其他專案從清單重算，不硬套數字。
- 完整模型、sidecar 與原生 Details 同交；分類 1:1 圖另置。
- 按 references/classification-and-package.md 的資料夾契約打包。
- 用程式核對檔案唯一性、數量、DWG/UPD配對、逐檔 hash、ZIP read-back及包裝期间來源未變。
- 最終工程驗收需在新解壓位置原生重開，核對 Document Manager 全部登錄與關聯，以及適用原生出圖/視覺項目。僅ZIP驗證完成只能交審查版，明列未完成門檻。

## 完成與回報

交付附件／精確路徑、完成範圍、實際驗證與剩餘警示。局部修正不等於全套通過；ad-hoc不等於canonical suite。相同程式與證據hash未變且沒有新疑點，不因重複通知無限重驗或重跑CAD。

## 本機流程來源

現有可參考實作與已知失敗值見 references/local-implementation.md；它們是經驗來源，不是可直接重跑的通用腳本。每次重查路徑、handle、PID、目前比例及工作集身分。
