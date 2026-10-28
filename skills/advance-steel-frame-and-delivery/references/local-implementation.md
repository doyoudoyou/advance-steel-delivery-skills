# 本機可參考實作（不是直接執行清單）

本機同名根目錄：`<USER_HOME>/Documents/AdvanceSteelTools`（存在但僅 CSV，並非完整工程）。歷史正式根目錄：<USER_HOME>/Documents/AdvanceSteelTools，保留為來源 evidence，不是本機執行路徑。
本機缺 `AGENTS.md`、`DEV_STATE.md`、`config/production-tools.json`、`tools/`、`workflows/`、`templates/`、`src/`、`jobs/`；以下歷史 runs／腳本／delivery 不宣稱已在本機。操作前依 `autocad-automation` 本機 preflight 逐件檢查所選腳本和工作副本，缺件 fail closed。
歷史隔離工作集：runs/case-a-final-submittal-v2；原始桌面模型不得改。

用read_file檢查實作，用search_files找實際輸出；不得複製舊expected_sha256來掩蓋來源變更。以下腳本含工作集常數、圖名、handle或UI身分，屬run-specific，不直接重跑、不包裝成通用CLI：

- revise_standards_uniform.py、standards-uniform-common.lsp：ED等比例框與原生列印、工程快照比對、reopen證據。
- capture_publish_handoff.py：本次native plot與臨時DSD唯讀擷取。
- center_user_recheck_print.py、center_final_three.py：plot origin置中，工程不動。
- trial_as005_center.py：只有當次AS-005布局適用的等比試排經驗。
- parts-modelspace-v1/explode_remaining.py：native singleton Batch explode；舊固定HWND需重新發現，checkpoint續跑需驗證對應來源。
- parts-modelspace-v1/convert_all.py：呼叫shared converter，33張逐張存檔重開；可參考result schema，不把原生標題比例套到其他圖。
- delivery/CaseA-submittal-uniform-frame-manifest.json：歷史14頁來源映射，未来使用者重排版需重新出圖更新。
- delivery/CaseA-complete-project-review-v3.zip：歷史完整審查包，非最終工程驗收基準。

歷史失敗做法不要重用：revise_standards.py資訊欄Y=0.70、AS-005壓低資訊欄、未通過視覺的Layout試印、未修復空白P-10的Window trial。
97%或1.10為當次幾何結果，非本skill固定參數。

範例工程同工程分案（範例案A→範例案B→範例案C→範例案D→範例案E）的 detached DWG 流程：最新範本 `<USER_HOME>/Documents/範例案D_整理_20261006`（prepare/process/build_delivery/final_check + native/*.cs）；最新可重用版在 `C:/施工圖交付/範例案D/05_交付紀錄/scripts`（範例案B版的全部功能：兩頁圖號清單 NIDX、安裝圖修訂框自動清除、原生 HEADER 比例、A$C／HYPERSTEELPAGEFRAME 數框 fallback；另加單一 HEADER 多框共用比例 SHARED_SCALE → shared_scale.json）；範例案B版在 `C:/施工圖交付/範例案B/05_交付紀錄/scripts`；範例案E版在 `C:/施工圖交付/範例案E/05_交付紀錄/scripts`（原始碼在 `native_src/`），名稱參數化：只改 `stage_runtime.py` 的 B、ROOT、NAME、COVER_FROM（cover/index 文字經環境變數 ST_COVER_FROM／ST_COVER_TO／ST_INDEX_TITLE 傳入）；prepare.py 的 [G] 圖名表、EXEMPT／OFFSHEET handle 與 28 張數量斷言屬該案，換案必改。
- 執行順序：inventory_all.py（PAVINSPECT + STPROBE）→ prepare.py（jobs.json、圖框窗驗證）→ process.py 試作數個 key → process.py 全部 → build_delivery.py（輸出 03_待確認交付）→ make_contacts.py（接觸表目視）→ final_check.py（新解壓原生重開）。用 `AdvanceSteelTools/.venv/Scripts/python.exe`（含 pymupdf、PIL），並設 `PYTHONIOENCODING=utf-8`。
- 範例案B舊版（`Documents/範例案B_整理_20261001`）：圖號清單 37 列分 AL-001/002；安裝圖 PA-001/003 舊 REVISIONS 修訂表以 revision_cleanup_v3/clean.py（STREVREMOVE，原始碼 revision_cleanup_v3/native/StageRevision.cs）按 handle 刪除；D-1～D-5 左右兩框。圖框 donor＝範例案A delivery_ed_standard_v4 GA-001，標準圖＝同目錄 ED-001～004，封面＝前一分案已置中的封面 DWG。
- 舊 nativebin DLL（C:/ASCaseA、C:/ASCaseD）可能已不存在；從 .cs 重建（StyledCaseATool.cs；PAVINSPECT 在 範例案A standard_revision_20260928/cadtool/CadTool.cs），net10.0-windows，輸出到專案自己的 nativebin。
- 「比例：詳各視圖」用 donor 原字寬會壓到「圖號：」欄（範例案D交付也有此瑕疵）；長比例字串需縮 WidthFactor（0.75 可容納）並放大檢查。
- 同名案重做（NAME 與封面原案名相同）時 COVER_FROM＝NAME 的替換是 no-op，STCOVER 仍要求剛好 2 處、照常產出副本，可直接用。
- 換案複製腳本後，用 grep 掃前案殘留：前案名稱、來源張數斷言、EXEMPT／OFFSHEET handle、[G] 圖名表、final_check 的零件抽樣 key、build_delivery 的交付說明與「禁止出現的其他案名」清單（清單要排除本案 NAME，否則本案自己的名字會讓檢查失敗）。
- 安裝圖修訂框清除（prepare.py）：Page 層 Line/DBText 落在 X 342.26～408.95、Y 55.24～66.38 且含 `REVISIONS` 才加入 erase，另刪 Index/Date/Description/Author 文字；非安裝圖或沒有 REVISIONS 文字仍停下。
- 已交付後改零件圖框屬性：範本在 `C:/施工圖交付/範例案B/05_交付紀錄/scripts_parts_project`（survey.py 唯讀調查 PROJECT、apply.py 用 CaseETool 的 `STSETATTR`（環境變數 ST_BLOCK/ST_TAG/ST_FROM/ST_TO/ST_OUTPUT/ST_REPORT，舊值不符或不是剛好 1 個屬性就失敗）、repack.py 複製正式交付→只替換變更檔→重組零件冊→驗證變更集合剛好等於預期）。修改 CaseETool.cs 後須重建到 `C:/ASCaseE/nativebin/styled`，且要等使用該 DLL 的 accoreconsole 批次結束（檔案被鎖）。
- 零件 PROJECT 字高位置：`STATTRREAD`（唯讀輸出 HEADER 插入點及各屬性 Height/Justify/Position/AlignmentPoint/style 到 ST_REPORT）、`STATTRFIT`（已交付修訂：ST_TAG/ST_EXPECT/ST_HEIGHT/ST_DY）、`STPROJFILL`（新案 process.py 用：ST_NAME/ST_HEIGHT=2.5/ST_ALIGNY=18.5，回報 action=filled|refit|kept_other）。已交付修訂範本 `C:/施工圖交付/範例案B/05_交付紀錄/scripts_parts_project/fit.py`；新案含此步的完整流程範本：最新為 `C:/施工圖交付/範例案D/05_交付紀錄/scripts_C`（含 `EXCLUDED` 不收錄零件過濾、inventory probe 的 cached 跳過、`multi_note or '無'`），範例案C版 `C:/施工圖交付/範例案C/05_交付紀錄/scripts_B` 含圖紙外標記寫入交付說明；同名案重傳新版時改 build_delivery/final_check 的來源路徑、received hash 檔名、ZIP 版次後綴與 prepare 的來源張數。
- 換案清單（從 scripts_B 起步要改的全部位置）：stage_runtime.py 的 B/ROOT/NAME；prepare.py 的 [G] 安裝圖圖名表（key 是 [G] 檔號，如 124/125/126）、來源張數斷言、OFFSHEET 規則；build_delivery.py 的輸出資料夾／ZIP 名、來源路徑、張數、project 名、交付說明各段（含與前版差異句、封面句、前案專屬句如 S-01/S-1）；make_contacts.py 的路徑與檔名前綴；final_check.py 的來源路徑、received hash 檔名、零件抽樣 key。改完 grep 前案名稱，只允許出現在註解、COVER 路徑/COVER_FROM 與 OTHERS 清單。
- 範本 build_delivery 寫入 delivery_qc.json 的 `parts_original_sha256_equal` 是零件 byte-identity 時代的欄名；零件做 PROJECT 填值後此計數其實是「零件張數」，產生後改成 `parts_project_filled`／`parts_project_refit`（或直接修範本欄名），不要讓 qc 宣稱零件與來源相同。
- 重跑：build_delivery 斷言 03_待確認交付 目標與 ZIP 不存在、make_contacts 寫 05_交付紀錄/qa、final_check 斷言 `fresh_extract` 不存在；只改交付說明而重打包時，先清這三處再依序重跑三支腳本（process 結果有 qc.json 會自動跳過）。
- 不要對 HYPERSTEELPAGEHEADER 的 BlockReference 呼叫 `Explode` 或探測其 block definition 幾何：Core Console 會 access violation 閃退。格線位置改從 PAVINSPECT 的 reopened.json 讀，屬性用 AttributeCollection 讀；字高位置以單張試作的 300dpi PDF 局部目視定案（上碰標籤、下壓格線都算失敗）。
- 圖框窗檢查若失敗：先區分「圖紙外遠處孤立標記」（保留不動、不列印、列為來源警示）與「角度尺寸 extents 假性超框」（目視確認後按精確 handle 豁免），不可放寬整體窗。

範例案A需求範例：14頁送審冊、33零件另冊；封面無框、簽核空白；AS-001/002使用者自行調整後直接出圖；BOM重量文字由使用者後續處理。這些不是其他案的隱含授權。查新任務與專案現況，不把歷史P-10、框外細線等狀態永久當成尚未修好。
