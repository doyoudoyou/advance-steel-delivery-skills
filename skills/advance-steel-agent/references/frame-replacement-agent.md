# 圖框更換 Agent（Frame Replacement Agent）

## 任務定位

專責處理鋼構施工圖 DWG 的舊圖框移除、指定圖框套用、BOM／圖形重新配置、配置空間清理、PDF 出圖及交付驗證。適用於單張或批次構件圖、安裝圖與標準圖。

## 必要輸入

- 待處理 DWG 或壓縮包
- **該專案專屬的新圖框 DWG／可插入圖框來源，必須由使用者事先提供；不得沿用其他專案圖框或由 Agent 自行猜選**
- 至少一張配置參考圖（例如 B-1.dwg）
- 圖名、圖號、張數、版次、日期的來源規則
- BOM 目標位置與圖形可用區域；未指定時先由參考圖量測，不猜座標

## 安全規則

1. 每個專案只能使用該專案專屬圖框。套用前先在目標 A3 Layout 中量測圖框 extents，確認紙張方向、單位、插入比例及有效邊界適當；圖框未提供、尺寸不明、超出 A3、明顯過小或需非等比例縮放時 fail closed，先取得使用者確認。
2. 原檔只讀，所有修改在可追溯工作副本進行。
3. 先盤點 Layout、圖框、標題欄、OLE、Viewport、BOM、主圖及配置範圍，再修改。
4. 只刪除已分類為舊圖框／舊標題欄／圖框外無效物件的實體；主 Viewport 不可因越界而直接刪除。
5. 圖框外物件採「完全位於有效 A3 範圍之外」判定；記錄 handle、類型、圖層及 extents。未知物件停止，不盲刪。
6. 圖形與 BOM 干涉時先平移圖形；仍無法容納才允許等比例縮放。不可非等比例縮放、不可超出圖框、不可壓到 BOM 或標題欄。
7. 標題欄必須以穩定、唯一的 semantic `Tag` 識別欄位，只更新 `TextString`／AttributeReference 顯示值；**不得**把 `Tag` 改成顯示文字。若 legacy 圖框沒有可靠 tags，先在版本化圖框副本離線正規化並重開驗證；正式批次不得依座標猜欄位。
8. Missing SHX 等已知資訊提示可依既有安全流程處理；未知對話框 fail closed。

## 執行流程

1. 解壓並建立 `source/`、`work/`、`output/`；建立 SHA-256／檔案清單。
2. 以 AutoCAD Core Console／受信任 .NET 外掛讀取每張 Layout 的實體類型、範圍、屬性與文字。
3. 由參考圖量測：A3 圖框有效範圍、BOM 左下定位點、標題欄欄位、圖形安全區。
4. 分類並刪除舊框、舊標題欄、reserved-area／無效 OLE，以及完全落在框外且非 Viewport 的物件。
5. 插入指定圖框；匹配圖名、圖號、張數、版次、日期與構件編號。
6. BOM 移至參考圖的左下位置；重算 BOM 與圖形實際 bbox。
7. 有干涉時平移圖形；空間不足時採單一等比例縮放並重新置中。
8. 儲存、關閉、重新開啟；再次檢查框外非 Viewport 物件數、圖形／BOM bbox 與標題欄。
9. 使用 `Plot area = Layout`、A3 橫式、1:1、不置中出圖。
10. PDF 文字檢查＋高解析度首尾／異常頁視覺 QC；批次需產生 contact sheet 與逐張 JSON／CSV 報告。

## 特別防錯

- 批次 promotion 前的代表件不可只挑容易圖：必須由完整 inventory／歷史轉換報告量化挑選至少涵蓋最小圖形面積、最大圖形寬度／位移、最小縮放比／最大 BOM、最高圖元密度、不同構件族群與末頁三位數圖號。每張仍要獨立 work copy、backup、fresh reopen、PDF 語意與視覺 QC；代表件全通過也不等於已具備 115 張 checkpoint/resume/retry 批次授權。
- Resumable batch 必須使用 OS-level exclusive writer lock，並記錄 source/frame/plugin/tool SHA-256、每張 attempt 與輸出 identity；resume 前先重驗所有 passed artifacts，任何 tamper／source drift 都 fail closed。`retry_failed` 必須顯式搭配 `resume`，只重跑 failed mark，passed mark 的 attempt count 與 DWG/PDF hash 不得改變。代表性 batch phase 應硬限制 2–10 張，未完成 cover/index/merged-PDF/full-regression gates 前不得解除成 115 張。
- 範例案T frame semantic schema 使用六個唯一 tags：`XX_DRAWN_BY`、`XX_REVISION`、`XX_DATE`、`XX_TITLE`、`XX_DRAWING_NUMBER`、`XX_SHEET`。Legacy x≈205–267 的寬座標規則會同時命中 `繪圖` 與`送審版本`，曾把繪圖人誤改成 `第A版`；不得再使用該規則。正規化後應以 PDF 文字或視覺 QC 確認 `彭聖崴` 與 `第A版` 各只出現一次。
- 配置空間的遠端 BlockReference／文字即使不在頁面上，也可能把出圖範圍拉寬，使圖框與主圖縮在一側。刪除前先證明其 bbox 完全在圖框外；刪除後重新開檔驗證框外非 Viewport 數量為 0。
- Plot 成功不代表圖面完整。必須確認 A3 圖框接近填滿整頁，且主圖、標題欄、BOM 沒有裁切、空白半頁、黑塊或縮成小點。
- Advance Steel 原生圖形、尺寸、剖面、標籤與 BOM 不得因換框流程被轉成不必要的普通圖元。

## 驗收輸出

- 修正版 DWG
- Layout／A3／1:1 PDF
- 轉換清單：刪除實體、圖框來源、BOM 位移、圖形位移／縮放、標題欄值
- 重開驗證：實體計數、框外非 Viewport 數、bbox、DBMOD／儲存狀態
- 視覺 QC 總覽與最終報告

只有在 DWG 重開、PDF 語意與視覺檢查均通過後，才能回報完成。
