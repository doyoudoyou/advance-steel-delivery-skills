## 鋼構施工圖專責 Agents

「鋼構施工圖助手」除建模／製圖能力外，新增以下兩個可由總控流程派工的專責 Agent。遇到相符任務時，主 Agent 必須先讀取對應 reference，再開始修改 DWG 或合併 PDF。

### 1. 圖框更換 Agent

觸發條件：使用者要求刪除／更換／統一圖框、套用指定專案圖框、移動 BOM、排除圖框外物件、處理圖形與 BOM 干涉，或批次將構件圖改成同一交付樣式。

完整規格：`references/frame-replacement-agent.md`

核心責任：

- 在工作副本辨識舊框、標題欄、OLE、Viewport、BOM、主圖與圖框外物件
- 安全刪除舊框及完全在有效圖框外的無效物件；主 Viewport 不可盲刪
- 套用指定圖框並匹配標題欄內容
- BOM 移至參考樣式位置；干涉時先移圖、必要時才等比例縮放
- Layout／A3／1:1 出圖，重開 DWG，執行 bbox／框外物件／語意／視覺 QC

### 2. 封面與圖號 Agent

觸發條件：使用者要求製作或更換封面、製作／重排圖號表、依 PDF 內容更新圖號圖名構件編號、多頁圖號 Layout、或合併完整施工圖。

完整規格：`references/cover-index-agent.md`

核心責任：

- 使用者提供的封面優先；沒有封面時不虛構缺失的專案資料
- 以已核准 PDF 標題欄為圖號／圖名的語意來源，舊圖號表只供版面參考
- 圖號表超過容量時新增 Layout，不縮小既有表格字高與列高
- 預設依「封面 → 圖號 → 鋼結構標準圖 → 安裝圖 → 構件圖」合併
- 建立 PDF 書籤並驗證頁數、分類起訖、圖號集合、A3 尺寸、非空白頁、SHA-256 與 contact sheet

### 總控派工規則

1. 若同一任務同時包含換框、圖號與完整 PDF，先執行圖框更換 Agent，確定所有單張 DWG／PDF 通過 QC，再執行封面與圖號 Agent。
2. 盤點與唯讀檢查可平行；DWG 轉換、PDF 替換與最終封裝必須依相依順序執行。
3. 每個專責 Agent 都必須回傳可驗證的檔案路徑、頁碼／實體計數、錯誤清單與驗收證據；只有自我宣稱成功而沒有重開／出圖／視覺證據時，不得由總控回報完成。
4. 單頁修正時，優先精準替換該頁並保留其他頁、書籤、metadata 與順序。
5. 模糊數值、缺失圖號、未知 AutoCAD 對話框或無法分類的框外實體一律 fail closed，不猜測。

### Production Job（Phase 2A 已驗證）

`AdvanceSteelTools` 已註冊 `tools/run_steel_drawing_package.py`，對應 `as-agent` operation `steel_drawing_package`。Phase 1 規劃模式使用 `jobs/steel-drawing-package-case-t-plan.yaml` 與 `projects/case-t-project/steel-drawing-package.manifest.yaml`，盤點封面、圖號、ED、PA、GA 並產出 `package_plan.json`、`input_inventory.json`、`stage_plan.json`，不修改來源。

Phase 2A 僅允許 `options.phase: frame_pilot` 搭配一個明確 `pilot_mark`。入口會：建立來源與 frame template 的 SHA-256 backup／fingerprint 與獨立 work copy → 核對 active document path 與核准 template hash → 使用 `XX_SteelDrawingPackagePlugin.dll` 單一 transaction 刪舊框／插新框／移 BOM／必要時縮移主圖 → **只有 transaction 成功後由 C# 明確 SaveAs，SCR 不得無條件 QSAVE** → apply report 必須 `saved:true`、`DBMOD=0` → 另一個 Core Console process 重開並再次要求 `DBMOD=0` → Layout／1:1／不置中出 PDF → 驗證 PDF 可讀 → 確認來源與 frame template SHA 都不變 → 原子且不覆寫地發布 DWG/PDF。任一失敗需從 backup 原子回復 staged work copy，且不得發布 final output。Viewport 預設保留；只有 manifest 明確 `erase_viewports: true` 才能刪除。Legacy 座標式標題欄規則只允許單張 pilot 明確 opt-in；批次前必須改成唯一 semantic `tag_equals`，且不得把 Attribute `Tag` 改成顯示值。

範例案T B-2 pilot 已證明：舊框為 0、新框為 1、BOM anchor 精確、來源 SHA 不變、DWG 重開持久、A3 Layout PDF 及視覺 QC 通過。批次 apply、封面／圖號生成、全卷合併仍封鎖，直到代表性 fixtures、resume/retry 與整卷 QC gate 通過。

範例案T案可用入口：

```text
jobs/steel-drawing-package-case-t-plan.yaml
projects/case-t-project/steel-drawing-package.manifest.yaml
```

標準執行：

```bash
as-agent preflight jobs/steel-drawing-package-case-t-plan.yaml
as-agent run jobs/steel-drawing-package-case-t-plan.yaml --offline
as-agent verify <run-dir>
```

不得把 dry-run 成功描述為已修改 DWG 或已重新合併 PDF；必須明確回報它只證明來源 contract、圖號集合、排序與階段計畫通過。

