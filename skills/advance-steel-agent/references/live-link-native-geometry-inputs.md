# Live Link: creating AS objects from native Grasshopper geometry

Use when the user wants Live Link components to take native GH outputs directly (Curve -> beam, Surface/Brep -> plate).

## First: inventory before proposing
- Grep `src/AsLiveLink.Gh/*.cs` for `Add(Curve|Line|Arc|Plane|Brep|Surface)Parameter` and list which native outputs already plug in (Line -> StraightBeam.ByLine, Arc -> BentBeam.ByArc, open Polyline -> PolyBeam.ByPolyCurve, closed Polyline -> Plate.ByPolygon, Plane -> rectangular plates). Usually the gap is a *dispatcher* (one component that accepts any curve), free-form curves, faces/Breps, and arc-edged plates — not basic connectivity.
- AS beams come in only three kinds: straight, bent (single arc), poly (straight segments). Free-form curves need a user decision: refuse, or approximate within a tolerance. Ask that as a 2-option question, together with scope (beam first vs. beam + plate).

## Mixed-kind component pattern (Beam.ByCurve)
- Existing sync RPCs are one kind per component (`beams.sync`, `bentbeams.sync`, `polybeams.sync`), and each sync deletes the component's tagged objects not in its request — so one GH component cannot call several of them. Add one server RPC with a `Kind` per item (`curvebeams.sync`, `CurveBeamItem{Kind, Points}`) built on `SyncCore.Run` (XData tag + hash diff + all-or-nothing + DiscardAllChanges rollback); put Kind in the hash so a kind change rebuilds.
- Verify per item after WriteToDb: kind via type check (StraightBeam/BentBeam/PolyBeam), section `ProfName`, straight `SysLength`.
- GH classification order: invalid/closed/too short -> refuse; `IsLinear(modelTol)` -> straight; `TryGetArc` -> bent (start, MidPoint, end); `TryGetPolyline` -> poly; else approximate: `ToPolyline(tol,0,0,0)` (one poly beam; 2 points -> straight) or `ToArcsAndLines(tol, 1°, 0, 0)` + `Explode()` (one beam per segment). Report deviation with `Curve.GetDistancesBetweenCurves`.
- Any curve that cannot be handled -> send nothing (all-or-nothing on the GH side too); outputs `kind` (+"(approx)"), `curveIndex`, `deviation`. Bent beams ignore orientation — remark it.
- Pitfall: arcs+lines approximation at 1 mm tolerance fragments a ~5 m spline into ~24 bent beams; default to the polyline mode and say the arcs mode needs a coarser tolerance.

## Server change -> trusted-path server must be updated
- A new RPC means the server in `<WORKSPACE>/ASLL-trusted\server` (loaded without Load Once) lacks it. Back up that folder to scratch, copy the new Release `AsLiveLink.Server.dll` + `AsLiveLink.Contracts.dll` in, then test; tell the user the trusted server was replaced and where the backup is.

## Test checklist (headless Rhino + throwaway DWG)
Line/Arc/Polyline/Spline -> kinds read back via RPC `model.list` (not `component.list`; it returns kind/length per tagged object); re-solve = all unchanged; mode switch leaves exact curves unchanged; closed curve refused with `model.stats` equal before/after; tolerance change -> updated with larger deviation; unknown section rejected; component removed -> 0 tagged.
