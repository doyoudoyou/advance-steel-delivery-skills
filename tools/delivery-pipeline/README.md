# delivery-pipeline

Config-driven tools for re-framing **detached** Advance Steel shop drawings (DWG exported from Document
Manager, e.g. `[G] - 101 (A3).dwg`, `[A] - C-1 (A3) 01.dwg`, `[S] - P-1 (A3) 01.dwg`) and packaging a
checked delivery. This is the tool side of the `advance-steel-frame-and-delivery` skill.

It does **not** touch an Advance Steel model, UPD files or Document Manager registration. Source files
are only read: each step copies them to a throw-away input first and checks the source hash afterwards.

## Requirements

- Windows, AutoCAD / Advance Steel 2027 (`accoreconsole.exe`). Older versions need a different
  `TargetFramework` and reference path in the `.csproj`. Not tested on older versions.
- .NET 10 SDK to build `native/DeliveryTool`.
- Python 3.11+ with `pymupdf` and `pillow` (`pip install -r requirements.txt`).
- A **donor drawing**: one DWG whose `A3 Advance Steel` paper layout contains your company frame as an
  `A$C…` block with a title text and a scale text such as `比例：NTS`. You supply this; none is included.
- Optional: a cover DWG, a set of standard drawings (ED), and a font file for the drawing list (`kaiu.ttf`
  by default).

## Build and trust the DLL

```bat
cd native\DeliveryTool
dotnet build -c Release -p:AutoCADDir="C:\Program Files\Autodesk\AutoCAD 2027" -o C:\DeliveryTool\bin
```

With `SECURELOAD=1` (the default), NETLOAD only loads DLLs from trusted locations. Add `C:\DeliveryTool\bin\...` to
**Options → Files → Trusted Locations** yourself. Do not lower `SECURELOAD`. The DLL path must be ASCII.

## Configure

Copy `project.example.json` and fill it in. Main keys:

| key | meaning |
|---|---|
| `root` | project root; folders `01_接收原檔 … 05_交付紀錄` are used under it |
| `batch`, `source_dir` | batch name and folder with the received DWGs |
| `donor.title_text`, `donor.scale_text` | exact texts in the donor frame to replace (must occur exactly once) |
| `donor.number_pos` | `[x, y, height, widthFactor]` of the drawing number inside the frame; measure it on your donor |
| `categories` | file-name prefix → kind (`erection`/`assembly`/`part`), regex for the id, number format, title template. Erection titles must be listed explicitly; a missing one stops `prepare`. |
| `revision_cleanup` | optional exact rule for an old revision table (layer, box, marker text); otherwise any `REVISIONS` stops `prepare` |
| `parts.fill_project` | fill blank `PROJECT` attribute of part headers with `name` (`false` = parts copied byte-identical) |
| `exempt`, `offsheet` | per-handle exceptions when the page-window check fails (see skill rules 10 and 18). Never widen the window to make an error go away. |
| `excluded` | `{job key: reason}` for sheets the user decided not to deliver |
| `forbidden_texts` | names of other projects that must not appear on any re-framed sheet |

## Run

```bat
set PYTHONIOENCODING=utf-8
python -m asdeliver.inventory  project.json          REM read-only, cached per sheet
python -m asdeliver.prepare    project.json          REM jobs.json; stops on anything it can't decide
python -m asdeliver.process    project.json COVER AL-001 GA-001 PA-001   REM trial run, then look at the PDFs
python -m asdeliver.process    project.json          REM all
python -m asdeliver.build_delivery project.json      REM -> 03_待確認交付 + ZIP
python -m asdeliver.contacts   project.json          REM contact sheets in 05_交付紀錄/qa — look at them
python -m asdeliver.final_check project.json         REM fresh unzip + native reopen
```

Moving the package to `04_正式交付` and cleaning `02_工作暫存` are left to you (or your agent, after you
confirm). The skill describes the rules.

## What gets verified

- Source hash unchanged after every Core Console run, and again at the end (`received-<batch>-sha256.txt`).
- After saving, each output is reopened. Every entity that was not deliberately erased is checked for the same
  handle, type, layer, text, block, attributes and extents (within 1e-6).
- PDFs: not blank, correct number/title/project name, no `REVISIONS`, no text from other projects,
  no vector graphics outside the paper. Book pages are pixel-compared with the single-sheet PDFs.
  The drawing-list pages contain every number once and list no parts.
- ZIP: `testzip` plus a hash check of every member. `final_check` reopens the extracted DWGs and compares them
  with the production read-back.

**Not verified:** visual layout quality (overlaps with BOM or info band, text touching lines). Check the
contact sheets and zoom in on doubtful pages. Dimensions are not re-measured.

## Known limits

- One paper layout per DWG (`layout`, default `A3 Advance Steel`). A3 window and offsets are configurable
  via `page_window`, but only A3 has been used.
- The drawing-list table geometry (columns, 10 mm rows, 20 rows/page) is fixed in `DTINDEX`.
- Index pages are drawn on a copy of the cover DWG with its content erased and the project frame applied.
- Do not call `Explode` on `HYPERSTEELPAGEHEADER` in Core Console: it crashes. The tools never do.
