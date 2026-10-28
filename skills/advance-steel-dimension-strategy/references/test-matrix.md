# Dimension Strategy Test Matrix

Use a copied model with its complete sidecar workset and freshly generated details. Never move a registered detail DWG away from its model workset.

## Required Evidence Per Run

```yaml
advance_steel_version: <exact>
model_copy: <path and source hash>
drawing_style: <exact user style>
view: <name/type/orientation>
dimension_strategy: <exact name>
chain_definitions: <ordered names>
prototype: <exact file>
fresh_or_update: fresh | no_change_update | geometry_update | reopen
native_inventory: <dimension handles/counts/grips>
expected_values: <per chain>
visual_result: pass | fail + screenshot/PDF
cleanup: <exact agent-owned artifacts removed>
```

## Baseline Fixtures

### T0: No Target Feature

- Main part exists.
- No holes, attached part, or end feature for the tested request.

Expected:

- no orphan hole/attached-feature chain;
- overall chain remains if required;
- reference-only points do not create a chain.

### T1: One Hole Group, Two Holes

Expected:

- one hole chain;
- both centers selected;
- declared end/reference points included;
- no duplicate chain.

### T2: Repeated Pitch Group

Use three or more equally spaced holes.

Expected:

- all centers retained;
- grouped-equal presentation follows policy;
- native grips remain individually verifiable.

### T3: Multiple Independent Hole Groups

Expected:

- one chain per pattern when `S`/separate is intended;
- groups do not merge because they are collinear;
- each chain closes against its intended references.

### T4: Move Hole Group

Move the pattern along the longitudinal direction.

Expected:

- center grips follow the pattern;
- edge distances change correctly;
- internal pitches remain or change according to the model;
- no stale point remains.

### T5: Add and Remove Holes

Expected for an all-holes chain:

- new hole center appears after update;
- removed hole center disappears;
- every remaining center remains native.

Expected for first-last policy:

- endpoint selection adjusts without arbitrary intermediate points.

### T6: Attached Part Families

Test at least:

- one plate;
- two collinear plates;
- mirrored plate;
- absent plate.

Expected:

- selected face/center policy is consistent;
- separate-per-item behavior matches the contract;
- unrelated attached parts do not enter.

### T7: End Features

Test cope/notch at start, end, both, and none.

Expected:

- chain appears only where required;
- finite feature versus contour semantics produce the intended points;
- overall chain remains overall.

### T8: Reversed Member Creation Direction

Create equivalent geometry with opposite beam start/end direction.

Expected:

- drawing orientation rule is deterministic;
- datum meaning remains correct;
- left/right visual appearance does not silently reverse fabrication intent.

### T9: Clipped Long Member

Expected:

- AS dimension values remain model-true;
- clipping does not break point linkage;
- AutoCAD paper-space scale is not used as fabrication evidence.

### T10: Hidden/Visible and Section Cases

Expected:

- visibility filter includes only intended points;
- section gauge chain uses the correct projected/native centers;
- source section direction follows the orientation contract.

### T11: Sloped or Faceted Exception

Expected:

- automatic chain passes if stable;
- otherwise AS parametric manual fallback uses valid native points;
- no plain AutoCAD dimension is accepted.

## Lifecycle Matrix

Run each promoted fixture through:

| Phase | Required result |
|---|---|
| Fresh generate | correct count, values, points and arrangement |
| Update with no model change | no point/chain loss or movement |
| Controlled model change | only intended values/points change |
| Save and close | no pending DB modification |
| Reopen | native dimension inventory persists |
| Document Manager plot | final PDF visually matches native evidence |

## Native Point QC

For hole chains:

1. select the dimension;
2. expose native grips;
3. inspect every shared control point;
4. snap/check `CEN` at the actual circle center;
5. verify the grip overlaps the center cross;
6. record handle, point count and ordered chain values.

A mathematically closed chain with one wrong point fails.

## Visual QC

Check:

- dimension line outside geometry as intended;
- correct side for view orientation;
- no duplicate or stacked chains;
- readable text and arrows at plot scale;
- no collision with labels, welds, section symbols, BOM or frame;
- no clipped text or dimension extension lines;
- nearest-to-farthest layering follows chain purpose;
- manual fallbacks are visibly identifiable for review.

## Promotion Gate

Promote a strategy to production only when:

- all required fixtures pass;
- AS version and country build are recorded;
- shared sub-style references are isolated;
- fresh generation and update behavior both pass;
- save/reopen persistence passes;
- native point identity and final PDF visual QA pass;
- rollback package and source settings backup exist.
