# 範例案T分類規則與交付資料夾

規則來源：專案 workflows/material-classification-agent.md、tools/as_runtime/material_classification.py。未來以最新版與使用者明示修訂為準。

## 分类

- H：H/RH/BH/HEA/HEB/HEM。
- HB：明確RHS/SHS；BOX不自動推為HB。
- L：角鋼；C：槽鋼；LC：輕型鋼，優先於L辨識。
- PL：PLT/PL/PLATE。
- FB：FB/FL/FLAT BAR，有兩個斷面尺寸且至少一邊可被5整除；不符歸OT。
- PP：PP/OD/CHS/PIPE/ROUND PIPE；RB：RB/ROUND BAR/SOLID ROUND。
- OT：未知、不匹配、特殊profile或需確認。
- PL按第一個斷面尺寸作厚度；FB按第二個斷面尺寸，資料夾 `<thickness>t`。
- PL不可因寬度/厚度可被5整除就改成FB。不靠檔名猜分類。
- 優先native profile證據；PDF文字可用既有parser。空白PDF無profile時不能捏造，保留OT待確認或另查native證據。
- 建立manifest绑定mark、registered detail、profile依據、分類、PDF/DWG source/destination/hash。
- 只為實際輸出建立資料夾。拒絕覆蓋；配對原子發布或失敗回復；source只讀。

## 建議交付契約

```text
<delivery>.zip
├─ README-請先閱讀.txt
├─ package-manifest.json
├─ Project/
│  ├─ <model>.dwg
│  └─ <model>/
│     ├─ Databases/
│     ├─ Details/                 # registered DWG/UPD
│     ├─ Prototypes/
│     └─ 圖冊補充圖/             # 封面、目錄、ED等
├─ PDF/
│  ├─ <submission-book>.pdf
│  └─ <parts-book>.pdf
├─ Current-sheet-PDF/            # 最新送審單張，不含零件
│  ├─ GA-*.pdf / AS-*.pdf        # 實際檔名以manifest為準
├─ DWG/                         # 與Current-sheet-PDF同層，GA/AS獨立匯出
├─ Classified-parts/
│  ├─ H/ HB/ L/ C/ LC/ PP/ RB/ OT/ # 只建立有輸出的類別
│  ├─ PL/<thickness>t/
│  ├─ FB/<thickness>t/
│  ├─ classification-manifest.json
│  ├─ DWG-export-manifest.json
│  └─ README.txt
└─ Evidence/                     # 原生出圖、轉換、readback證據
```

保留模型所需原生sidecar依賴，但交付包排除已確認的舊版PDF與歷史「圖冊PDF」資料夾；使用者不接受舊PDF混入交付。僅保留manifest指定的最新合冊、單張及分類零件PDF，同步更新README與package-manifest。清理限交付輸出，不自行刪除來源專案或歷史驗證資料；未知原生依賴不可任意刪除。用ZIP read-back確認舊PDF路徑不存在、保留檔案hash不變。排除bak與dwl/dwl2等備份鎖檔需顯式規則；不把未存實驗模型混入主Project。

## GA/AS PDF與DWG配對位置

GA/AS匯出DWG放在與Current-sheet-PDF同層的DWG資料夾，例如 `<delivery>/Current-sheet-PDF/GA-001.pdf` 對應 `<delivery>/DWG/GA-001.dwg`。不得建立 `Current-sheet-PDF/DWG/`。檔名以已核對圖號／manifest對應為準。
這些是原生Batch explode後將Layout內容複製至ModelSpace、保存驗證後移入的detached輸出，不是Project/Details內的原生詳圖，也不自動標示工程1:1。零件Classified-parts成對分類流程維持獨立，不受本GA/AS目錄規則改動。

## 驗證

- 程式列舉完整清單、dedupe、核對DWG/UPD配對與PDF/DWG配對，不手算總數。
- 合冊頁數/順序/來源hash，逐頁比對來源（適用時raster-match）。
- ZIP testzip＋每個member hash讀回，包裝前後source hash一致。
- 工程模型可重開與所有DM登錄必須在解壓後實驗位置另驗，不能用檔案數當登錄數。
- 成功匯出與變更前後hash驗證不同於工程尺寸/視覺驗收；README明列blank PDF、未驗證碰線、使用者豁免及未跑的native gates。
