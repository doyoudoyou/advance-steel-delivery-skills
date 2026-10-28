---
name: box-column-shop-drawing-annotation
description: "MUST load before any BOX column shop-drawing task."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [advance-steel, box-column, shop-drawing, dimensions, dsm, structural-steel]
    related_skills: [advance-steel-dimension-strategy, advance-steel-agent, autocad-automation]
---

# BOX 柱施工圖判讀與標註

## 使用範圍

BOX 柱施工圖讀圖、審圖、物件分類、原生 label／尺寸修改、DSM／Drawing Style、Point Selection Rule／qualifier、fresh generation 與 native plot 驗收前必須載入本入口。非 BOX 的一般鋼構任務不因含 DSM 名稱而套用 C-1 規則。

先區分只讀與修改；只讀分析不啟動 Advance Steel、不執行 V84 檢查／啟用、不產圖、不修改 DWG／AstorDetails。不得把載入技能視為修改授權。

## 核心判讀與尺寸規則

1. 按 BOM → Main Part → 底板／端板 → 附屬件 → 正交主視圖／剖面 → 從屬關係 → 標註目的 → 物理端點判讀。
2. Main Part 由 BOM、長向連續輪廓與最大剖面共同確認；不能只靠最長線。BOX 內輪廓是空腔與壁厚，不能當成獨立板件。
3. 底板／端板通常大於 BOX 斷面，帶孔群與周邊加勁件；連接板正視是完整板面、側視近似平行雙線，必須以正交視圖確認。
4. 加勁件通常短而重複，位置與底板、BOX 壁、孔或集中力對應。折板必須分清實長、水平投影與垂直投影。
5. 孔位以所屬板件為 datum，完整表達孔徑、數量、pitch、gauge 與邊距。虛線不能當中心線。
6. 先組立控制，再定位、製作尺寸與資訊標註。一條尺寸鏈只包含同一連續製作關係的物理控制點；板厚兩端須落在同一板的兩面。
7. 每條尺寸記錄用途、起終物件、真實端點、方向、視圖、預期值與容許差。不得混合不同深度、面或同 Model Role 的非目標零件；鏡像可改順序，不能改物理關係。
8. 獨立孔位／局部定位鏈與附件位於 Main Part 同一物理側；混合用途 native chain 先拆分，不得整組 MOVE 跨側。
9. 參考數字只供驗證，不能覆寫模型幾何。缺少 BOM、物件身分、視圖或端點依據時標示未知，停止依賴該資訊的標註；不得猜第一筆或固定座標。

## 按任務讀取

- **只讀判圖**：使用上述規則；需要詳細物件、線條、datum 定義時，以 `read_file` 讀取 `references/box-column-shop-drawing-annotation-principles.md` 中「核心原則」到「尺寸鏈規則」的相關段落。該參考的產圖／修改命令不適用於只讀任務，無須整份載入。
- **所有已授權修改／產圖**：先讀下列共同修改閘門及 `references/native-execution-and-dimensions.md`；再核對正式專案準則，讀取其中與操作相符的段落。
- **Label 移動／批次避讓**：另讀 `references/native-label-workflow.md`。
- **尺寸鏈 point 移除**：讀 `references/native-execution-and-dimensions.md` 的原生命令交易與回復段落。
- **DSM、fresh generation、保留手動 labels、C-1 regression**：另讀 `references/dsm-and-c1-regressions.md` 及正式準則；其中 C-1 專用數字、qualifiers 與 requests 不得套到不同模型。

## 正式來源與前置檢查

- 本機同名專案根：`<USER_HOME>/Documents/AdvanceSteelTools`（存在但工程未完整部署，目前僅 CSV）；來源歷史根為 `<USER_HOME>/Documents\AdvanceSteelTools`，不是本機操作路徑。
- 本機預期準則：`<USER_HOME>/Documents/AdvanceSteelTools/workflows/box-column-shop-drawing-annotation-principles.md`（缺失）。缺 `AGENTS.md`、`DEV_STATE.md`、`config/production-tools.json`、`tools/box_column_v84_standard.py`、`config/box-column-v84-standard.json` 與 workflow；修改／產圖前按 `autocad-automation` 本機 preflight 逐件核對，缺件立即 fail closed；只讀判圖可讀技能內參考，不因此執行 CAD。
- 技能參考：`references/box-column-shop-drawing-annotation-principles.md`。
- 操作前核對正式路徑存在、內容版本、source model/detail identity 與 registration；路徑存在本身不足以驗證正確專案。缺件或規格矛盾時 fail closed，不改用猜測路徑。正式專案最新準則優先；更新技能副本依 Skills 寫入審核，不自動修改正式來源。
- **僅新 BOX 圖產圖／DSM 分支**：預設 `BOX_COLUMN_V84_STANDARD`。先在正式專案工作目錄用 `terminal` 執行 `python tools/box_column_v84_standard.py`；只有 `success=true`、`after_failures=[]` 才可 fresh generate。設定清單 `config\box-column-v84-standard.json`。依專案已授權流程修正漂移，不能因讀圖自動 `--activate`。
- V84 是起始基準；新模型仍按實際 BOM、Mark、Model Role、幾何與端點調整 C-1 專用 selectors，不能強加固定尺寸。

## 共同修改閘門

1. Accepted／production baseline 保持不變。使用完整工作副本，含 model DWG、sidecars、detail registration 與可恢復備份；記錄 SHA-256、物件與檔案身分。不得只複製 standalone detail。
2. 依正式 controlled workflow 要求 fresh registered details；DSM／Drawing Style 修改必須由來源模型複本 fresh generate，Force Update 不能證明新 requests 生效。
3. 盤點 Main Part、附屬件、Mark、Model Role、handle、bbox、所屬視圖與端點語意。先單一 side／rule isolation，確認命中目標再批次套用。
4. 使用 native Advance Steel objects、native detail points／OSNAP END；保留原生 labels、leader 箭頭與 dimensions。禁止普通 AutoCAD DIM、MText／Leader 仿製、硬改 dimension text、遮罩或 PDF 後製偽造。
5. 使用者要求 DSM 修改時，手動新增 native detail dimension 也不能代替 DSM。重建 strategy 時保留原有專用 USER requests，成對檢查 Front／Top 掛接。
6. 修改後 Save／close／reopen，核對 native object counts、handles、端點及 registration。每張由 Document Manager native plot 驗收 PDF／PNG，核對文字 token、線條、圖框、碰撞與工程語意；COM PlotToFile／-PLOT 只作診斷。
7. 未知或驗收失敗時停止交付，依備份與正式 rollback 流程恢復並讀回確認。不得以無錯誤 log、單張成功或檔案非空取代完整驗收。

## 完成條件

- **只讀**：交付附 BOM／視圖／剖面證據的物件分類、尺寸端點與待釐清項目；無需製造不存在的 CAD 操作證據，也不把分析當成產圖完成。
- **修改／產圖**：所有適用共同閘門通過；每條尺寸有物理起終點及用途、native object 持久化、Document Manager PDF／PNG 通過，無重疊、超框、重複或無製作意義尺寸。報告含 source/work/output 身分、物件、端點、handles、預期／實際結果、備份與每張驗收證據。缺任何必要證據即列受阻，不能回報全部完成。
