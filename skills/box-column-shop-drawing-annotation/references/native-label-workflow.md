# 原生 label 操作與批次清理

來源：本 skill 原入口的實測流程；適用於已授權的 native label 修改。操作前先讀入口的共同修改閘門與 `references/native-execution-and-dimensions.md`。不得直接修改 production baseline。

## 原生 label 位置調整

Advance Steel detail 中的 `AstDetailTextRepr` 若直接使用 COM `Move`，文字、leader 與箭頭會整組平移，箭頭因此脫離原模型物件。

1. 修改前備份完整 registered model/detail pair，記錄 label 對應 `AstBlockReferenceEx` 箭頭 bbox 中心座標。
2. 預選該 `AstDetailTextRepr` 並先盤點 grips。一般完整 label 會有三個 grips：箭頭端點、文字左側／leader attach、文字右側；優先啟用「文字左側／leader attach」grip，直接用絕對紙空間座標移動文字，箭頭端點會保持在原模型物件。完整 label 不先做 COM `Move`。
3. 只有 mark-only compact label 僅顯示箭頭 grip、無獨立文字 grip 時，才先用 COM `Move` 整組平移，再啟用箭頭 grip，以 AutoCAD grip `STRETCH` 將端點精確送回步驟 1 的原始箭頭座標。文字會留在新位置，leader 重新連回原物件。
4. grip stretch 後 `AstBlockReferenceEx` handle 可能重建，不得沿用舊 handle；重新盤點 bbox，並以 Save／關閉／重開及 Document Manager native plot 驗證。
5. 文字應放在 view 外側與尺寸鏈之間的空白帶；leader 可以穿越空白，但不得跨尺寸文字、箭頭或其他 label。
6. AS2027 已驗證可不經螢幕 UI，直接使用現代 .NET Grip API：先以 `Entity.GetGripPoints(GripDataCollection, ...)` 盤點 grips，再建立只含「文字左側／leader attach」的 `GripDataCollection`，呼叫 `Entity.MoveGripPointsAt(selectedGrips, offset, ...)`。舊版 `Point3dCollection` overload 對 `AstDetailTextRepr` 會回傳 `eNotImplementedYet`，不得沿用。修改後仍須以 bbox、Save／close／reopen 和 Document Manager native plot 驗證。

## 多張 detail 的 label／dimension extension line 批次清理

1. 複製完整 registered model DWG 與同名 detail 資料夾到獨立工作目錄；不得把 C-2、C-3 等 standalone detail 搬到另一模型後直接修改。
2. 先對每張 baseline Document Manager PDF 解析文字 bbox 與向量線段。碰撞檢查必須把 `2x`、`5x`、`6x` 等數量前綴與 `S-*` mark 視為同一 label 文字群，不能只檢查 mark token。
3. 以該張圖自己的 paper/CAD affine mapping 將 PDF 文字位置匹配到 `AstDetailTextRepr` handle；不同 sheet 的 plot offset 可能不同，禁止把 C-1 的固定 offset 套到全部圖。應用多個已知 label bbox 擬合 offset，並要求匹配距離接近 0；距離異常時停止自動移動並人工確認。
4. 每個 detail 應先產生 handle／`dx,dy` plan，備份 detail，再一次批次移動所有 grip index 0。不得因不同 detail 出現相同 handle 而跨圖共用物件；handle 只在該 detail 內有效。
5. 每張修改後都要重新 native plot，重跑文字／垂直 extension-line 向量碰撞檢查，並比較 baseline/final 的 PDF 文字 token multiset，確認尺寸與標籤文字沒有增減。
6. 向量掃描可能把移動後 label 自己的垂直 leader attach segment 誤判成 dimension extension line；遇到邊界相交或移動後新增線段時，必須以局部高解析 crop 區分 own leader 與 dimension line。
7. 不能只追求向量碰撞數為 0。逐區檢查文字、底線、leader、dimension text、箭頭與 view geometry；尤其上方尺寸鏈附近的 `S-27`，向下移可能掉入視圖幾何，向上移則須確認 leader 不穿尺寸文字。
8. 完成後逐張 Save／close／reopen，盤點 `AstDetailTextRepr`、`AstDimLineRepr`、PaperSpace count 與 moved handles；最後輸出每張 before/after collision count、移動量、native plot 路徑及回復備份位置。
