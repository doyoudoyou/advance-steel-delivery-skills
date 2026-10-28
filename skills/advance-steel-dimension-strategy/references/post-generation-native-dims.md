# Post-generation native dimensions (scripted, AS2027)

Use for a chain the drawing style cannot produce (e.g. total-only overall length, because point restrictions act per object; a single hole row). Result must be an AS-native `AstDimLineRepr`, never AutoCAD DIM. Re-run after every regeneration: a fresh style run overwrites the detail DWG.

## Recipe (verified on a column assembly sheet)

1. Back up the whole model folder (model DWG + `<model>\Details` + `Databases`) before touching the registered detail.
2. Start AS on the model copy with a no-op script (`FILEDIA 0`) — no Live Link server and no Load Once click needed, so it runs unattended. Wait for COM `GetActiveObject("AutoCAD.Application").ActiveDocument`, then ~20 s for AS idle.
3. Open the detail from that session with COM `Documents.Open(<model>\Details\<sheet>.dwg)` so the model/detail registration stays valid. Then poll (2 s steps, try/except) until `ActiveDocument.Name` is the sheet and `CMDACTIVE` reads 0 before any `SendCommand`: AS rejects COM calls ("call rejected by callee") while the sheet loads.
4. Inventory paper space: `AstDimLineRepr` count + bboxes, `AstAtomicDetViewRepr` handles + bboxes. Pick the view-geometry entity whose bbox spans the members to dimension (its handle is the view selector).
5. Resolve endpoints with AutoLISP `(osnap (list x y 0.0) "_end")` (or `"_cen"` for holes) at the candidate bbox corners; keep the returned Z (view depth) and pass it unchanged.
6. Create: `(progn (setvar "OSMODE" 0) (command "_AstM16CommDetAddUCSLinearDim" (handent "<view handle>") p1 p2 <placement pt> "" "") (princ))` via `doc.SendCommand`; poll `CMDACTIVE` = 0 in 0.5 s steps. Accept only if `AstDimLineRepr` count rose by exactly 1 (new handle on `AS_DIM_ON`). Add intermediate points with `_AstM4CommDetModDimAdd` when a chain is needed.
7. Verify the value: the COM object exposes only generic entity members (no value/point properties) and AS custom entities cannot be COPY+EXPLODEd (it silently leaves duplicate dims behind). So `doc.Save()`, then plot from the SAME AS session with `-PLOT` to PDF (`BACKGROUNDPLOT 0`; accoreconsole cannot render AS custom entities), read the PDF text layer with PyMuPDF grouped by x, and crop-render the view to check both ends align with the intended part edges.
   Before any model-DWG command, assert `ActiveDocument.Name` is the model: a detail left open by a failed plot silently becomes the target (selection count 0). Write each PDF to a new timestamped name; a previous PDF still open in a viewer makes `os.remove` fail and aborts the batch.
8. Close, restart AS, reopen the detail, re-count `AstDimLineRepr` and confirm the new handle persists. End AS by closing documents and calling COM `app.Quit()`; use `Stop-Process` on the PID you launched only if AS does not respond, because a forced kill shows the user a crash dialog. `Quit` with an unsaved model (e.g. after a TILEMODE switch) leaves AS open on a save prompt: save or close the model unsaved first, then re-check `Get-Process acad` before claiming AS is closed.
9. Formal acceptance still needs a Document Manager batch plot.

## Making it general (spec by part, not coordinates) — verified on an upright column

Tool: Live Link repo `tools/postdim/postdim.py <detail.dwg> <spec.json> [--save] [--preflight <drawing.preflight json> --assembly <mark>]`.

- Spec points: `{"part": "S-3", "corner": "BL"}` → front-view atomic bbox corner + `osnap _end`; `{"holes_in": "S-2", "pick": "lowest"}` → hole centre. One part has one atomic entity per view; front view = the main part's tallest atomic, and a part's front-view entity = its atomic nearest that x. Bbox corners reproduced the hand-snapped endpoints exactly. Marks resolve through Live Link `drawing.preflight` (handle, singlePart, mainPart, role) restricted to handles present on the sheet; `main` may be `role:Column`. Place dims relative to the front-view main part edge, not absolute paper points.
- Hole centres: `AstDetHoleRepr` is one entity per hole GROUP; its bbox centre snaps to an arbitrary row. Grid-scan `osnap _cen` (12×12) over each group bbox inside the part and pick the row from the distinct centres.
- Corners such as BL/TL and left/right placement assume the member is drawn upright. On a rotated sheet the dims still get created (count rises) but attach to wrong points and the expected values are absent from the PDF. Fix orientation first (detailing direction below); then one mark-based spec served a whole column family. Batch check: assert each expected value (e.g. member length + plate stack) is present in the PDF text layer per sheet, then eyeball one sheet at 150 dpi for end-point identity and frame overflow.

- Part ownership of each view entity: the existing NETLOAD probe `Documents\AdvanceSteelTools\tools\AtomicModelHandleProbeDynamic` (command `HHPROBEALLATOMICMODELHANDLES`) maps every `AstAtomicDetViewRepr` handle to its model handle via P/Invoke (`AstAtomicDetViewRepr::cast` → `AstRepr::beginTransaction` → `AstAtomicDetView::getModelHandle`). Copy it to scratch and change its hard-coded report path before building (`dotnet build -c Release`, net10.0-windows).
- Candidate exports in `ADVS\ASDetailingObjects.dbx` for the next step (names only, signatures from mangled symbols): `AstDetView::transformModelToPaperspace(AstGeomPoint3d&)`, `AstAtomicDetView::getEndPointsForManualDimension`, `AstAtomicDetView::getCenterPoints`, `AstAtomicDetView::getView`. List more by regex-scanning the DLL bytes for `\?[A-Za-z_0-9]+@(AstDetView|AstAtomicDetView|AstDetail)@@` (no `strings`/dumpbin needed).
- Before NETLOADing a self-built DLL into an unattended AS session, put its folder in `TRUSTEDPATHS` (or load it from an already-trusted folder): an untrusted DLL raises a load-confirmation dialog that blocks every later COM call until a human answers, and the session looks hung.

## Assembly detailing direction (`_AstM14SetAssemblyDetCS`)

Model-DWG command that sets the front-view direction of an assembly drawing (UCS X → sheet horizontal, Y → sheet vertical). Verified unattended on 7 columns: all came out upright with the style front view on Object Front (`SystemAndBox` 1).

Recipe per assembly (Live Link repo `tools/postdim/detcs_one.py <mark> <AstBeamRepr handle>`):
1. Assert `ActiveDocument` is the model DWG, then `doc.SetVariable("TILEMODE", 1)` and check it reads 1. **The command only works on the Model tab**: in a layout it says `This command only applies to model DWGs`, and when preselected it exits cleanly with `CMDACTIVE 0` while storing nothing — a clean exit is not evidence.
2. UCS via COM `doc.UserCoordinateSystems.Add(origin, xPoint, yPoint, name)` + `doc.ActiveUCS = ucs` (an `UCS 3` sent in LISP produced a different axis set). For a column: X = horizontal direction of the connection plate face (plate `xAxis` from `extract.plates`), Y = world up.
3. Preselect the main part repr: `(sssetfirst nil (ssadd (handent "<AstBeamRepr>")))` (repr handle from Live Link `select.handles` → PickfirstSelectionSet; it differs from the AS model handle).
4. Send `_AstM14SetAssemblyDetCS\n` from a separate short-lived process (SendCommand may block); then UCS back to World and `doc.Save()`.
5. Regenerate and view every sheet; there is no read-back API (user can check right-click main part → Show Assembly CS).

- Do not pass the entity as a command argument `(command "_AstM14SetAssemblyDetCS" (handent ..))`: AS waits for input and rejects all COM calls.
- The style front view's `SystemAndBox` is applied on top of this direction: with Rear (2) a correctly set assembly comes out upside down, so use Front (1).
- Renumbering (single + main part detection, marks unchanged) kept the stored direction: a regenerated sheet stayed upright. Renumbering that changes marks or merges assemblies is untested (forum reports say it can reset), so after such a run regenerate one previously-rotated mark and re-run the recipe if it turned.

## One-command pipeline

Live Link repo `tools/postdim/pipeline.py <model copy.dwg> --asm T-1 T-2 ... [--process <key>] [--spec <json>] [--no-detcs]` chains: start AS with the trusted server → `drawing.preflight` → detailing direction per assembly → `RunDetailProcess` (old sheets moved to `<out>\prev`) → `postdim.py` per sheet → `-PLOT` PDF → text-layer checks, writing `<model dir>\pipeline_<ts>\report.json` incrementally and stopping the AS it started in `finally`.
- Derive the expected total from the model, not a hand list: top of the top plate contour z minus bottom of the base plate (contour face z minus thickness when its normal points down). Spec dims may carry `"expect": <value>` for fixed values (e.g. 80).
- A 7-sheet run takes longer than the terminal foreground cap: launch it with `background=true, notify=true` and read `report.json` for progress; if a foreground run is cut off, read the report, stop the AS PID it logged, and relaunch in background.
- Persistence check after a batch: `tools/postdim/reopen_check.py` reopens every sheet in a fresh AS and confirms the post-dim handles are still present.
- Tall members can overflow the frame at the style's fixed scale (a 4930 mm column at 1:25 on A3 put the top plate and its width chain ~10 mm above the frame); eyeball the tallest mark of each family, and solve it in the style (scale/placement), not with post-dims.

## Open points
- Decide per chain whether the segmented style chain stays when a total-only post dim is added.
