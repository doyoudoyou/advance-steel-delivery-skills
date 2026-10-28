# 原生出圖與 Explode 執行注意

## 專案入口

先讀目前版本，確認 CLI 與 config/production-tools.json：
- tools/as_document_manager_native_plot.py：原生 Batch plot 與可選 explode；確認 model_saved_before_astdoccheck 副作用。
- tools/as_part_drawing_export.py、tools/as_all_part_drawing_export.py：成對匯出／queue orchestration。
- tools/as_runtime/part_drawing_export.py::convert_exploded_layout_to_model_1to1(source, output, scale_factor=None, layout_name=..., timeout=...)：保留 raw DWG、建立獨立1:1 DWG。從 native title-block scale 解比例；未知或不一致 fail closed。
- tools/as_runtime/dm_state.py：選列、Add to explode；tools/as_runtime/dm_explode_queue.py：精確singleton檢查。

以 terminal 執行 `as-agent preflight <job.yaml>`，必要 `as-agent run <job.yaml>`／`as-agent verify <run>` 依 operation 契約。缺視覺證據不能寫假PASS，不得為通過移除必要 gate。

## GA/AS 必要交付分支

GA/AS 同時交付原生PDF與獨立DWG。DWG使用下述原生Batch explode精確佇列流程，保留raw DetailsExploded，僅在另存匯出副本操作。將指定Layout的圖面物件複製至ModelSpace，保留原比例／相對位置及Layout內容；排除viewport容器，處理viewport依賴前不得默認所有工程內容均在PaperSpace。複製前後比對新增ModelSpace物件數量、幾何與內容，存檔關閉重開後DBMOD=0。

此GA/AS分支不使用零件1:1 converter：該converter會乘SCALE比例並刪除PaperSpace內容，不符合單純「複製後存檔」要求。未明確要求時不得自行放大或清空Layout。

驗證後移動匯出DWG至與 `Current-sheet-PDF/` 同層的 `DWG/` 資料夾，例如 `<delivery>/Current-sheet-PDF/GA-001.pdf` 對應 `<delivery>/DWG/GA-001.dwg`，不建在PDF目錄內。以圖號及manifest明確對應，不從整本合冊路徑猜單張位置；拒絕覆蓋、核對移動前後hash及exact-target read-back。原生registered DWG/UPD與raw Explode保持原位置。PDF仍經原生Batch plot，Batch explode不代替PDF出圖。

## PDF 證據

比對本次 exact DSD DWG/layout、原生報告、輸出mtime/hash/內容。wrapper returncode0不代表內層native_exit0；PDF存在不等於本次成功。
Publish log job ID可跨session重複，按連續JS..JF界定一次工作。臨時DSD可能快速刪除或共享鎖，必要用既有唯讀捕捉器，不改publish文件或猜對應。
空白頁保留警示。Window試印有內容只代表試印有圖，不能直接取代Extents空白頁並聲稱完整。Layout列印亦不是必然解法，必須看實際PDF。

## Batch explode 精確操作

1. 確認啟用模型為完整隔離副本；原生登錄圖名與完整Details路徑一致。
2. 選單一detail→Add to explode→Batch explode。
3. 讀回列表，要求剛好一個requested filename；讀路徑排除同名其他專案。不要整批加入再刪除非目標。
4. 執行 native toolbar；觀察完成狀態及新DetailsExploded檔案稳定，不用固定sleep宣稱完成。
5. 每張append checkpoint並保存queue、scale、source/output hash。中斷後只接受經證據識別的既有輸出，不把任意存在檔案當成功。
6. 出現額外列、空列或unknown dialog先停；重新讀狀態。空列不表示已執行，更不能跳過驗證直接Execute。
7. 後續轉換需關閉已知DM對話框使CAD可用；不盲按OK以免觸發殘留Batch plot，不擅自處理未知保存提示。

## UI 與恢復

使用computer-use背景優先與verify/escalate規則；前景需要當次授權。核對工具回報的實際送出座標與目標窗口：某些driver會把已是native的座標再次按DPI縮放，可能點到taskbar。不要反覆試點或怪罪AS。
允許的替代為專案既有原生視窗控制，先定位正確process/window與控件、讀回列表。不要固定PID/HWND/螢幕座標，也不要以工具替換規避安全批准。
僅 `.select()` 可能未刷新owner-drawn右側清單；需要可驗證控件點擊與重新讀取。先核對真實狀態，再修改通用工具。不得global kill或安裝Ponytail。
