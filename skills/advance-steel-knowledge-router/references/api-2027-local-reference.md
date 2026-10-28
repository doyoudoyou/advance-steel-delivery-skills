# AS2027 Local Managed API Reference

**Captured:** 2026-08-06  
**Installation root:** `C:\Program Files\Autodesk\AutoCAD 2027\ADVS`  
**Authority:** locally installed Autodesk XML documentation for this AS2027 installation.

This reference stores names and fingerprints only. It does not copy full XML documentation.

## File Fingerprints

| XML | Bytes | SHA-256 |
|---|---:|---|
| `ASMgd.xml` | 390360 | `78f2deb8ca793e32138d80a0764ffb0ddd6654a2a6a696b2956d7076ae46c1f3` |
| `ASObjectsMgd.xml` | 404396 | `044ff8f395557a260c5979b47b70b70e2069875da72f486acd035478cb181d5d` |
| `ASCADLinkMgd.xml` | 364651 | `3a09872ceccc957c7cc4e03aed36eb9ed38794295424c1ddcc2510798db83695` |
| `ASGeometryMgd.xml` | 3915 | `1dbed455f7a037ee25bd37280b1700e8f651c0de351000b21a26cb28887acb64` |
| `ASModelerMgd.xml` | 50084 | `5c5b07d1dcbfc1aafb8cea177bb7d663789728446b26d071d7942c5b9c88a511` |
| `ASProfilesMgd.xml` | 71268 | `c1bc5856535a71a768076e9878433c2e280b953dc7f13ae4c1c613ba5ead2f48` |

If a fingerprint changes after an Autodesk update, re-run member discovery before relying on this reference.

## Matching Assemblies Present

- `ASMgd.dll`
- `ASObjectsMgd.dll`
- `ASCADLinkMgd.dll`
- `ASGeometryMgd.dll`
- `ASModelerMgd.dll`
- `ASProfilesMgd.dll`
- `ASMgdJoints.dll`
- `ASExchangeMgd.dll`
- `ASSettingsMgd.dll`
- `DotNetRootsMgd.dll`
- `Interop.AstSTEELAUTOMATIONLib5.dll`

Assembly presence is not permission to load it from an external process. Prefer an in-process Advance Steel/AutoCAD .NET command for model APIs.

## Selected Documented Members

### Model and database access (`ASObjectsMgd.xml`)

Documented in the installed XML:

- `Autodesk.AdvanceSteel.CADAccess.DatabaseManager.ExportToACIS(Autodesk.AdvanceSteel.CADLink.Database.ObjectId[], System.String)`
  - XML summary: exports elements to an ACIS SAT file.
- `Autodesk.AdvanceSteel.CADAccess.FilerObject.markChanged(System.Boolean)`
- `Autodesk.AdvanceSteel.ExternalDb.ASModelProxy.UpdateObjects(...)`
- `Autodesk.AdvanceSteel.ExternalDb.ASModelProxy.AddNewObjects(...)`
- `Autodesk.AdvanceSteel.ExternalDb.ASModelProxy.GetOldNewHandlesMap`

The `ASModelProxy` summaries indicate that object sets and relations must be complete/consistent and that newly added objects may receive different IDs. Treat any save/update operation as mutation requiring a disposable model and explicit identity mapping.

### Native physical bodies and contexts

Distinguish installed XML availability from installed DLL metadata and reproduced runtime semantics:

- `ASObjectsMgd.xml` documents `Autodesk.AdvanceSteel.ConstructionTypes.AtomicElement.GetModelerBodyList(BodyContext.eBodyContext, out ModelerBody[])` and `GetModeler(BodyContext.eBodyContext)`.
- Installed AS2027 DLL metadata exposes `Autodesk.AdvanceSteel.Modeler.ModelerBody.getBrepInfo(out Point3d[], out ModelerBody.FaceInfo[])`, body `Volume`, and face `OuterContour` / `InnerContours`.
- Installed `BodyContext.eBodyContext` metadata includes `kDetailed`, `kNormal`, `kExactDetailing`, `kMaxDetailed` and `kCollision`. Verify the available enum in the active installation; do not assume a context from another release exists.

For a read-only comparison, build against the installed assemblies, execute `GetModelerBodyList` for each explicitly selected context inside `new DocumentAccess(null, true, false)` without Commit, and serialize each context separately with exact native identities, frames, finite system-line definition, body volumes, vertices and all face loops. Check the pinned document, unchanged saved DWG hash, clean state and read-failure list after the probe.

Observed on AS2027 copied circular HSS models: `kExactDetailing`, `kMaxDetailed` and `kCollision` could add rounded cross-section corner geometry and change body volume while preserving the angular facet stations and local radial-wall contact intervals seen in `kDetailed`. Treat this as versioned observed behavior, not a guarantee for every member. Inspect which geometry changed rather than assuming greater vertex count means finer arc subdivision.

Keep a smooth finite-arc result, a faceted-body result and any certified approximation bound as separate evidence. Native volume matching an exported contour mesh validates that representation's reconstruction; it does not establish that a larger local gap is harmless tessellation error. Route actual inclusion acceptance and finite-footprint calculations to `autocad-automation`'s existing `references/native-bolt-inclusion.md`; do not duplicate execution policy here.

### Derived documents (`ASMgd.xml`) — read-only types; see the crash note in Drawing automation before calling any entry point

Documented types and members include:

- `Autodesk.AdvanceSteel.DerivedDocuments.DerivedDocumentExtension.GetInfo(...)`
- `Autodesk.AdvanceSteel.DerivedDocuments.DerivedDocumentExtension.GetDerivedObjects(...)`
- `Autodesk.AdvanceSteel.DerivedDocuments.DerivedDocumentInfo.GetPrototypeName`
- `DerivedDocumentInfo.GetRevisions(...)`
- `DerivedDocumentInfo.GetApprovalStatus`
- `DerivedDocumentInfo.GetApprovalComment`
- `DerivedDocumentInfo.GetApprovalDate`
- `DerivedDocumentInfo.GetDwgNo(...)`
- `Autodesk.AdvanceSteel.DerivedDocuments.DerivedObjectDetailInfo.GetDetailType`
- `DerivedObjectDetailInfo.GetMainPartsDetailed`
- `DerivedObjectDetailInfo.GetSinglePartsDetailed`
- `DerivedObjectDetailInfo.GetHandle`
- `DerivedObjectDetailInfo.GetScale`
- `DerivedObjectDetailInfo.GetProcessDescription`
- `DerivedObjectDetailInfo.GetStyleName`

The installed XML describes `DerivedObject` as representing document objects such as details, NCs, and BOMs. This is useful for inventory and read-only evidence, but registered-detail state and model sidecars still control whether a drawing operation is valid.

### Drawing automation (runtime-tested in-process, AS2027 GBR)

There is no public API to create or edit drawing styles. The working route is to drive AS's own processes:

1. **Number first.** `Autodesk.AdvanceSteel.Services.EqualParts.RunEqualPartsDetection(out pp, out sp, out mp)` numbers without a dialog in about 150 ms. By default only single parts are numbered; for assembly drawings call `EqualPartsParameters.GetCurrentParameters()`, set `DetectMainParts = true`, then `SetAsCurrent()`. Read the marks back with `AtomicElement.GetSinglePartPositionNumber()` / `GetMainPartPositionNumber()`; unnumbered parts return `Not defined`. Do not trust `KernelServices.IsNumberingUpToDate()`: it returns 1 even when the parts have no mark. A process run on unnumbered parts returns in a few ms, raises no error and writes no drawing.
2. **Run the process** with `KernelServices.RunDetailProcess(processKey, ObjectId[])`, called outside any `DocumentAccess` or lock. `processKey` is the `<n>` in `_AstM4CommDetailingProc_ Standard <n>` from `...\Steel\Support\Toolbars\AstProcessesData.xml`; user-made processes are listed there too and work the same way. Output goes to `<model folder>\<model name>\Details\`, plus `Databases\revision_*.db`. List the files before and after the run to get the new DWGs. `SendStringToExecute("_.ASTM4COMMDETAILINGPROC ...")` produced nothing in testing, so use the API call.
3. **Cameras need a drawing style.** A `ConstructionHelper.Camera` is skipped silently unless both `DetailStyle` and `DetailStyleLocation` are set; the defaults are -1, and Type or Scale alone is not enough. The two numbers are `<location> <style>` from `_astm4CommDetailing_ Standard <location> <style>` in `AstDetailsData.xml`. Use a "Cameras - Selected" process (e.g. 73–76) with the camera id: it gives exactly one drawing. "Cameras - All" also re-draws earlier cameras. Running a process again on the same camera makes a new drawing, not an update.
4. The camera's view direction is against its CS Z. `setXYExtents` takes `eXYExtents.kAutomatic` / `kFixed`; `setZClipping` takes `eZClip.kNone` / `kUpper` / `kLower` / `kBoth`. All of them read back exactly.

**Crash:** `KernelServices.GetDerivedDocumentsForDwg(CADDocumentManager.GetCurrentDatabase())` killed the AS process (on a model with no drawings). Never call it; list drawings by scanning the `Details` folder instead.

`EqualPartsParameters.SetAsCurrent()` changes did not survive an AS restart (seen once). Still restore them yourself after a run.

## What This Evidence Proves

- The named file and assembly exist in this AS2027 installation.
- The selected member/type names appear in the installed Autodesk XML.
- The hash identifies the exact documentation snapshot inspected.

## What It Does Not Prove

- that an API was available in AS2025 or another release;
- that a call is safe from external Python;
- required `DocumentAccess`, document lock, transaction, disposal, or main-thread rules;
- that a mutation persists after save/close/reopen;
- that a detail is registered when its standalone DWG was moved;
- that a forum code sample matches this API snapshot.

## Runtime Validation Gate

Before promoting a new API member into production automation:

1. Confirm member name in matching local XML.
2. Build against the installed matching DLL set.
3. Execute in-process on a copied model with its complete sidecar workset.
4. Require the intended document, `CMDACTIVE=0`, and `DBMOD=0` before mutation.
5. Record native handles/IDs before and after.
6. Save only after a successful transaction and explicit verification.
7. Close/reopen and verify persistence.
8. For drawings, use native Document Manager output and visual QA.
9. Preserve source hashes and delete only exact Agent-owned disposable artifacts.

## Citation Shape

When citing this reference in an answer, use:

```markdown
Installed AS2027 XML evidence:
`C:\Program Files\Autodesk\AutoCAD 2027\ADVS\<file>.xml`
SHA-256: `<hash>`
Member: `<fully-qualified member name>`
Runtime status: tested / not tested
```
