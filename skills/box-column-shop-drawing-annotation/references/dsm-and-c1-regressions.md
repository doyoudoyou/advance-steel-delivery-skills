# DSM 與 C-1 實測回歸案例

來源：本 skill 原入口。以下具名 selectors、requests 與尺寸只屬原案例；以正式專案最新資料及 matching view/model identity 為準，禁止移植固定數字到新模型。修改前先讀入口共同修改閘門、`references/native-execution-and-dimensions.md` 與正式專案準則。

## DSM 更新後保留手動原生 labels

- Document Manager `Force update` 可能保留既有 detail 的舊 dimension request composition；不可把 Force Update 視為新 DSM point rules 已套用的證據。
- Dimension strategy composition 改變時，應 fresh generate detail 並先驗證 native plot。
- 若需保留舊 detail 已核准的原生 labels，可把舊 detail 複製成唯一檔名，與 fresh detail 同時開啟；刪除 fresh detail 中相對應的 `AstDetailTextRepr`，再使用來源 document 的 COM `CopyObjects` 複製到 fresh detail `PaperSpace`。
- AS2027 不要把 DWG 路徑附加在 Start Menu `.lnk` 後啟動；捷徑可能不轉交路徑並讓 COM 持續拒絕呼叫。應直接執行 `acad.exe /language en-US /product ADVS /p <<ADVS>> <destination.dwg>`，等待 `PaperSpace.Count` 可讀後，再透過 `Documents.Open` 開啟唯一檔名的來源 detail。
- C-1 實測中，複製 `AstDetailTextRepr` 可保留原生文字、底線、leader 幾何、箭頭目標及 paper-space 位置；仍必須 Save／關閉／重開，並用 Document Manager native PDF 驗證內容與 leader。
- 不得複製普通 MText／Leader 仿製品；未通過完整 dimension regression，不得接受轉移結果。

## 同一 Model Role 的剖面尺寸隔離

- 同一剖面若 S-127、S-19 等零件都使用 `LugPlate` Model Role，不要假設單一 qualifier 能同時正確服務所有方向；`MpGeomRestriction` 與 point-position 對不同投影方向的行為可能不同。
- C-1 B-B 已驗證的組合式做法：在目前保留的 B-B 投影中，restriction `1` 實際選到垂直 S-19，restriction `8` 實際選到 S-127；不可依 MP restriction 名稱猜零件，必須以 label leader 與板面 extension lines 驗證。上方 request 應掛 restriction `8` 的 S-127 points，下方 request 應掛 restriction `1` 的 S-19 points。右方 S-19 使用精確 qualifier `32313`（`LugPlate` + `XX_C1_S19_360x170x15`）與 restriction `4`，避免 S-127 endpoint 混入。
- 若 right chain 使用 broad `LugPlate`，錯誤特徵是混入 S-127 的 `220`；若只使用分離的 `Ref. Mp TopRight/BottomRight`，則可能遺失 S-19 下表面到 BOX 下端的末段。C-1 正確右鏈使用精確 S-19 qualifier `32313` 加一個 `Objects=14 / PointType=1001 / PointGeometricRestrictions=0` 的 BOX all-extremes selector，完整得到 `206 / 15 / 180`。B-B 最終驗證基準：上方 S-127=`230 / 15 / 156`、右方 S-19=`206 / 15 / 180`、下方 S-19=`180 / 15 / 206`、左方無尺寸。
- 幾何 filter 的 `ModelRole` 必須與模型一致。對 LugPlate，`DetObjQualifierSetItem.ModelRole` 應為 `LugPlate`；設成 `-` 可能讓 qualifier 完全選不到物件。修改後一定要 fresh generate，不能只看 SQL rows。

## Hidden geometry 與專用 requests

- BOX 內隔板在正交視圖中若被 BOX 壁遮蔽，DSM point rule 必須顯式納入 hidden geometry；C-1 Top View 已驗證做法為 `Objects=7`（built-in Stiffeners）、`VisibilityStatus=2`、`PointType=1`。`VisibilityStatus=0` 不會產生內隔板尺寸；改用廣泛 Attached Parts qualifier 會混入非目標附屬件控制點。C-1 S-20 下方關係鏈的左 datum 是 **S-27 外側端點**，不是 Main Part 左端；已驗證專用 selector 為 `Objects=32269`（S-27 qualifier）並沿用 `Mp - Extreme, Left` 的幾何限制，模型原生結果為 `6307 / 18 / 452 / 18 / 50`。
- 使用者要求修改 DSM／Drawing Style 時，禁止以手動新增 `AstDimLineRepr`、native detail dimension 或一般 AutoCAD DIM 代替；必須修改 DSM，並由來源模型複本 fresh generate 驗證。
- 重建／合併 `DetViewDimStrategyItems` 時，必須盤點並重新掛回原有的專用 USER requests（例如端板專用 chain）；若同一物理尺寸在 Front／Top 各有獨立 request，必須成對驗證兩個 strategy 的掛接，不可只恢復其中一個。C-1 已驗證案例：Front strategy `32225` 必須掛 request `32265`，Top strategy `32226` 必須掛 request `32266`，兩者皆產生左側端板 `125 / 400 / 125`。PDF regression 必須分區檢查兩個視圖，不能只檢查其中一組文字。新增 request若使用既有 `Group` 且 `AllowCombine=True`，可能跨 request吞併其他尺寸，應使用未占用的隔離 group並以 native plot比較驗證。
