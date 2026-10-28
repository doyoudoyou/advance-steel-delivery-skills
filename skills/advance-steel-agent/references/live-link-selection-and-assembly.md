# Live Link: selection round-trip and assemblies (AS2027)

Split out of `grasshopper-live-link-project.md` (that file is at the size limit; add new Live Link depth here or in another topical file).

## Before probing a new phase
- Grep the repo for RPCs / XData fields that already carry the data (`PipeServer.cs` case list, `ModelQuery.cs`), and grep the existing references for enum values already measured, before writing "unknown" in a probe doc. Static sigdump results are labelled "static, not run on AS" until a debug probe reads them back.

## Find Linked Component (AS object -> GH component)
- No new AS API needed: `select.current` returns each selected AS object with `linkedTo` = the `ASLL_LINK` XData ComponentId, which is GH `InstanceGuid.ToString("N")`; the tag also carries the item index.
- GH side: read `select.current` -> find the component in the active GH document whose `InstanceGuid` matches -> select it and zoom the canvas to it; output name, ComponentId, ItemIndex.
- Cases to report, not fail on: baked object (tag removed -> "not linked"), component in another GH document (id known, not found), one component owning several objects (show ItemIndex).
- Order: build this first (GH-only, no server change, so no Load Once); canvas check = user selects an object in AS, presses the trigger, sees GH jump to the right component.
- Implemented as `FindLinkedComponent` (QueryComponentBase, Selection category): `run` input fires only on the false->true edge (keep `lastRun`; a held true must not re-query), plus a right-click "Find from AS selection" calling the same public `Find()`. Select via `x.Attributes.Selected`, zoom via `Instances.ActiveCanvas.Viewport.Focus(attrs)` only when `canvas.Document == OnPingDocument()`.
- Adding a component: add its icon entry in `IconPainter.cs` and bump the component count in `tests/gh/version_test.py`; add a NAMING-AUDIT line when the name is not from Dynamo.

## Testing selection features headlessly
- Simulate the user's AS selection with RPC `select.handles` (sets the implied selection on the objects' repr entities), then solve the component; cover: one owner, several owners with their handles, a baked object (unlinked), an owner in a second `GH_Document` (not in this document), empty selection, and a `model.stats` before/after check proving read-only.
- Headless Rhino has no canvas, so the test can only assert `Attributes.Selected`; scrolling/zooming and real hand-picked PickFirst selection stay "unverified" until a user canvas check.
- When the change is GH-only, start AS with a script that NETLOADs the server from the user-approved trusted path (`<WORKSPACE>/ASLL-trusted\server\AsLiveLink.Server.dll`): no Load Once click needed. First confirm that server build contains every RPC the test calls (its commit vs. the RPCs used).
- If scratch was pruned, the empty test drawing `asll_run/base_GBR.dwg` is a plain copy of `C:\ProgramData\Autodesk\Advance Steel 2027\GBR\Shared\Support\Templates\ASTemplate.dwt`.
- Back up the installed plugin folder before copying the dev .gha in, restore it after, and `cmp` the .gha to prove the restore; stop only the AS/Rhino PIDs the run started.

## Assemblies
- AS has no assembly object: an assembly = main part + parts connected at shop level.
- `AtomicElement` (ASObjectsMgd): `IsMainPart` get/set, `Assembly` string (meaning unprobed), `GetMainPartPositionNumber(...)`, `MainPartNumber` / `MainPartPrefix`, `GetConnectedObjects(out ids, eAssemblyLocation)` / `GetConnectedElements`, `GetQuantityInModel(eSingpartState, eAssemblyLocation)`. eAssemblyLocation: kOnSite=0, kSiteDrill=1, kInShop=2; connected parts are listed only at the queried level, so query kInShop for shop assemblies.
- `BuildingStructure.ObjectsGroup` (`create(parent, name)`, `getObjectsIDs()`) is a separate grouping, not an assembly.
- Plan (Tekla parity): read-only `assembly.read` (main part, members, main-part number) verified on a known assembly in a model copy (expected members listed before the run, including shear studs/welds), then Add to Assembly = shop-level weld/bolt connect + set `IsMainPart`, with read-back.
