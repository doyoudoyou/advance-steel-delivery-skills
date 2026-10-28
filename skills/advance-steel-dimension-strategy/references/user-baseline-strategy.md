# HH-DIM-BEAM-ASSY-V1.0

**Status:** user-approved dimension strategy baseline  
**Approved:** 2026-08-06  
**Primary release:** Advance Steel 2025  
**Research comparison:** AS2026 Help and installed AS2027; no backward assumptions  
**Scope:** beam assembly shop drawings only  
**Implementation status:** design complete; DSM implementation requires copied User definitions and disposable-model validation

## Objective

Produce fabrication-ready beam assembly dimensions with deterministic native point identity, low cleanup, stable detail updates, and a bounded fallback for exceptional geometry.

## Fixed Policy

| Decision | V1.0 policy |
|---|---|
| Drawing scope | Beam assembly shop drawings |
| Fabrication datum | Main-part physical end/contour extreme |
| Attached-part datum | Near physical face relative to selected main-part physical end |
| Hole-chain topology | Every hole center plus both physical-end reference points |
| Hole dimension type | `Linear, relative` |
| Repeated pitch | Show individual pitch values; `Group equal distances` off |
| Dimension placement | Hole chains above; attached-part set-out above and farther out; overall below; end features local |
| Ordinate dimensions | Blocked by default |
| Manual fallback | Advance Steel parametric dimensions only |
| Native acceptance | `CEN` point-by-point plus grip-to-center-cross verification |

## Datum Hierarchy

1. **Main-part physical end/contour extreme** for finished length and longitudinal hole edge distances.
2. **Attached-part near physical face** for longitudinal set-out.
3. **Hole center** for drill coordinates and pitch.
4. **Main-part centerline/system line** only when a future explicitly approved exception requires it.
5. **Grid/level** reserved for GA/erection strategies outside V1.0.

System-line coordinates cannot silently replace physical fabrication geometry.

## View Responsibility

### Front / Longitudinal View

Create separate chains for:

1. main-part overall length;
2. longitudinal hole-group edge/pitch/edge;
3. attached-part longitudinal set-out;
4. cope/notch/end-feature dimensions;
5. one outer closing/check dimension only when it adds fabrication value.

Do not combine holes, attached parts and end features into one chain.

### Top or Bottom View

Use only when it provides clearer native points for:

- flange-hole longitudinal pitch;
- transverse offset from flange/web physical geometry;
- attached parts not unambiguously represented in Front.

Do not duplicate a complete Front-view chain.

### Section / Cut View

Use for:

- transverse hole gauge;
- local plate projection or offset;
- geometry collapsed or obscured in Front/Top.

For a manual section, enable ORTHO before selecting the source detail view so the cut is perpendicular to the main-member longitudinal axis.

## Required Chain Definitions

### 1. Main-Part Overall

Name:

```text
XX_ASSY_FRONT_MP_OVERALL_X_GBA_V10
```

Contract:

```yaml
question: finished main-part length
measured_object: main_part
points: physical contour extremes without unrelated feature points
direction: main-part or view X
chain_type: linear_relative
arrangement: global, below, one combined chain
do_not_combine_with_local_chains: true
```

### 2. Longitudinal Hole Full-Pitch Chain

Name:

```text
XX_ASSY_FRONT_HOLE_PITCH_X_GTS_V10
```

Contract:

```yaml
question: left edge + every pitch + right edge
measured_object: one hole_or_bolt_pattern
points: every native hole center
references: left and right main-part physical extremes as reference
chain_type: linear_relative
arrangement: global, above, separate per pattern
group_only_related: true
do_not_combine: true
group_equal_distances: false
```

Required topology:

```text
PHYSICAL END → HOLE 1 → HOLE 2 ... → HOLE N → PHYSICAL END
```

A chain such as `67 / 600 / 81` is valid only when each shared point is the intended native hole center and the two outer points are the declared physical ends.

### 3. Section Hole Gauge

Name:

```text
XX_ASSY_SECTION_HOLE_GAUGE_Y_GTS_V10
```

Contract:

```yaml
question: transverse hole gauge and physical-edge offsets
measured_object: relevant hole_or_bolt_pattern
points: every relevant native hole center
references: physical flange_or_web edges as reference
chain_type: linear_relative
arrangement: global, designated outside side, separate per group
group_equal_distances: false
```

Longitudinal pitch and transverse gauge stay in separate chains/views.

### 4. Attached-Part Set-Out

Name:

```text
XX_ASSY_FRONT_ATTPL_NEARFACE_X_LTS_V10
```

Contract:

```yaml
question: longitudinal position of each attached part
measured_object: attached_part
point: near physical face relative to selected main-part datum
reference: selected main-part physical end
chain_type: linear_relative
arrangement: local, above, farther from view than hole chain, separate per item
do_not_combine: true
```

For an attached-part family where near face is not the fabrication control surface, create a separately named exception request. Do not redefine this shared V1.0 rule.

### 5. End Feature / Cope / Notch

Name:

```text
XX_ASSY_FRONT_END_FEATURE_X_LBS_V10
```

Contract:

```yaml
question: end-processing size and location
measured_object: main_part_end_processing
points: beam-end processing or explicitly selected feature/contour points
reference: affected physical end
chain_type: linear_relative
arrangement: local, nearest affected end, separate per feature
do_not_combine: true
```

Keep end-feature points out of overall and hole chains.

## Arrangement Layers

### Above the View

From nearest to farthest:

1. hole full-pitch chains;
2. attached-part near-face set-out chains.

### Below the View

- main-part overall chain;
- one outer closing/check chain only when necessary.

### Local to Member Ends

- cope, notch and other end-feature chains.

Use `S` separate-per-item for independent hole patterns and attached parts. Use global overlap avoidance for outer chains. Set `Do not combine with other dimensions` whenever collinear chains answer different fabrication questions.

## Hole-Pattern Rules

Accepted native topologies:

- every hole;
- first only;
- last only;
- first and last;
- above selections plus valid reference points.

V1.0 production default is **every hole plus both physical-end references**.

Blocked:

- arbitrary intermediate subset;
- displayed-circle inference without native center identity;
- a chain accepted only because arithmetic closes;
- grouped `n @ pitch = total` presentation;
- ordinate dimensions without a future approved strategy revision.

## Automatic and Manual Boundary

Automatic native chains cover recurring geometry. Manual dimensions are allowed only for:

- exceptional one-off features;
- sloped, curved or faceted geometry with no stable automatic request;
- bounded corrections where a broader automatic rule would over-match unrelated objects.

Manual dimensions must use Advance Steel parametric tools and preferred/native points. Plain AutoCAD dimensions fail V1.0 fabrication acceptance.

## Native Point Acceptance

For every hole chain:

1. select the native dimension;
2. expose grips;
3. check each shared control point individually;
4. snap/check `CEN` at the actual hole circle;
5. verify the grip overlaps the hole-center cross;
6. record the dimension handle, point count and ordered values;
7. repeat after update and save/reopen.

Correct arithmetic with one wrong native point is a failure.

## Production Acceptance Contract

A generated detail passes only if:

- each required chain exists exactly once;
- no unrelated points enter any chain;
- all hole centers and reference endpoints are native and verified;
- every chain uses the declared physical datum;
- different fabrication questions remain separate;
- no dimension/label/weld/BOM/frame collision occurs;
- clipping does not change values or point identity;
- a no-change update preserves count, values and placement;
- add/remove/move tests produce only intended point changes;
- reversed member creation direction does not reverse datum meaning;
- save/close/reopen preserves native dimensions;
- Document Manager PDF matches native drawing evidence.

## Implementation Order

1. Start from the closest acceptable beam assembly User drawing style.
2. Deep-copy the view dimension strategy and all dependent requests/point rules.
3. Rename every copied item with `XX_..._V10` semantic names.
4. Remove unrelated chains before adding new ones.
5. Implement one chain at a time in the order: overall, hole pitch, gauge, attached part, end feature.
6. Fresh-generate after each chain; do not validate only by updating an old detail.
7. Run the complete `test-matrix.md` lifecycle before promotion.
8. Keep the source style and rollback export untouched.

## Out of Scope

V1.0 does not define:

- beam Single Part drawings;
- BOX-column V84 drawings;
- column, plate, stair or rail strategies;
- GA/grid/level dimensions;
- ordinate dimensions;
- grouped repeated-pitch notation;
- production DSM mutation without a copied test environment.
