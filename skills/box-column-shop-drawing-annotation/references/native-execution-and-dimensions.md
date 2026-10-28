# Native 執行、plot 與尺寸鏈修改

來源：本 skill 原入口的已驗證流程。僅供已授權修改／產圖使用；入口共同修改閘門全部適用。

## Advance Steel 執行閘門

1. 複製完整來源模型 DWG、model sidecars 與 detail registered workset 到測試資料夾。
2. 產圖／DSM 變更從模型複本 fresh generate，保持 model/detail registration。
3. 盤點 Mark、Model Role、handle、bbox、相對 Main Part 的位置。
4. 先做單一 side／單一 rule isolation trial。
5. 使用 native detail point／OSNAP END，不使用任意 paper coordinate。
6. 驗證每條尺寸建立後 `AstDimLineRepr` 的新增數量。
7. Save、關閉、重開驗證持久化。
8. 使用 Document Manager native batch plot 驗證 PDF／PNG。
   - 必須選取 `Details > Up to date > <detail.dwg>` 的實際 detail child，不得只選 `Up to date` 群組或右側 Properties row。
   - `Add to batch plot` 成功後，左樹會出現 root-level `Batch plot`；切換後右側應只顯示 batch item及可見的 3-button toolbar。
   - 3-button toolbar：中間是執行 native batch plot，右側是 Plot Devices；不得把 6-button Details header誤認為 batch toolbar。
   - 若前一次 Document Manager 流程失敗後，Advance Steel owner window 位於 minimized/off-screen（例如 `(-32000,-32000,...)`），DM 雖可見但 toolbar click 只會出現 tooltip、不會觸發；必須先 `SW_RESTORE` owner window，再重新開啟 DM。
   - 驗收 PDF 必須由上述 Document Manager流程產生；COM `PlotToFile`、`-PLOT`或PDF後處理只能作診斷，不能作正式驗收。
9. 檢查數值、位置、重疊、圖框及物理端點依據；未通過不得交付或替換已接受的工作成果。

## CAD 自動化效能閘門

- 不得用 60／120／300 秒 foreground timeout 代替狀態判斷。互動命令必須由持續存活的 controller 執行，並以 command log、`CMDNAMES`、目標檔案或 dialog 出現作事件完成條件。
- 單一 capability probe 最多 10 秒；命令／外掛未註冊、輸出路徑錯誤或 API 回傳 `eNotImplementedYet` 時立即停止該路徑，不得重複等待同一 timeout。
- 固定 `sleep` 原則上不得超過 1 秒；較長操作使用 0.25–0.5 秒 polling，並要求狀態連續兩次穩定。每 2 秒輸出目前 state、elapsed、timeout，讓使用者知道正在等什麼。
- Document Manager formal native plot 預設只做兩次：已知 baseline 一次、全部修改完成後 final 一次。單點／單 rule 中間試驗以 command log、entity inventory、Save/reopen 等低成本方式驗證；除非存在不可由物件狀態判斷的視覺風險，才增加 isolation plot。
- 同一 detail 的多個 dimension points 應在一次開檔 session 批次處理；不得每個點各自啟動／關閉／plot。
- 對 AS custom command，先在 disposable registered pair 上證明完整 prompt transaction（選取、`1 found`、Enter 次數、完成條件），再批次套用；不要邊猜 prompt 邊修改正式工作 pair。
- 只終止 automation 自己啟動的 AutoCAD PID；不得以全域 `taskkill /IM acad.exe` 作一般重試手段。

## 原生尺寸鏈移除 dimension point

使用 `_AstM4CommDetModDimRemove` 修正 `AstDimLineRepr` 時：

1. 必須從已開啟的 registered model context 以 `Documents.Open` 開 detail；不要單獨啟動／直接開啟 detail 後儲存，否則 Document Manager 可能把 detail 標為 `Not Set`。
2. 修改前備份整個 model/detail registered pair；只備份 detail DWG 不一定能恢復 model-side registration。
3. 命令提示 `Select the dimension line you want to remove:` 實際上是建立要移除的 dimension-point selection set。座標必須落在該點的原生 attachment line；command log 出現 `1 found` 才算命中。
4. 命中後必須提交 selection set。AS2027 實測需要兩次 Enter 才讓 custom command 完整返回；Esc 會取消整組選取，因此不會修改尺寸。
5. 移除某個 point 後，Advance Steel 會重新計算相鄰段。例如 `100 / 35 / 3@127 / 35 / 100` 移除兩個轉角 point 後會原生重算為 `135 / 3@127 / 135`。若誤刪同方向序列的第一點，會得到 `162 / 2@127`，應立即由 registered-pair 備份恢復。
6. COM `SendCommand` 在 selection loop 期間會阻塞；自動化時保持 background COM caller 存活，將焦點設到 detail 的 MDI child，再送 Enter，不要讓呼叫端 timeout／被殺死。
7. 完成後 Save、關閉 detail、回到 model，使用 Document Manager native batch plot驗證。必須比較修改前後 token counts，確認只有預期尺寸改變且 labels 未遺失。
