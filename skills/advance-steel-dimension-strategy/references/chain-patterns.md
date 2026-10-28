# Reusable Dimension Chain Patterns

These patterns are design primitives. Replace `<...>` with target-version definitions and verify by fresh generation. Do not assume a named country-build request exists because the semantic pattern exists.

## Pattern 1: Main-Part Overall

**Question:** What is the finished overall size in the selected direction?

```yaml
measured_object: main_part
points: extreme size or contour extremes
direction: object/view X or Y
chain_type: linear_relative or linear_absolute
arrangement: outside local-detail chains; keep separate
```

Use physical contour extremes for fabrication length unless the office standard explicitly requires system-line coordinates. Do not let feature points enter the overall chain.

## Pattern 2: Hole-Group Full Pitch Chain

**Question:** What are both edge distances and every pitch inside one hole group?

```yaml
measured_object: one hole/bolt pattern
points: all hole centers
references: selected main-part physical extremes as reference
chain_type: linear_relative
arrangement: separate per pattern; group only related; do not combine
presentation: group_equal_distances only when it improves shop readability
```

Expected topology:

```text
EDGE_1 / PITCH_1 / ... / PITCH_n / EDGE_2
```

All selected centers must be native/smart points. This is the default pattern for a required chain such as `67 / 600 / 81`; values are case data, not universal constants.

## Pattern 3: Hole-Group Extent Only

**Question:** Where does the group start and end?

```yaml
points: first and last hole centers
references: one or both main-part extremes
chain_type: relative or absolute
```

Use this when pitch is specified elsewhere or repeated-pitch notation is deliberately omitted. Do not select an arbitrary subset of intermediate holes.

## Pattern 4: Hole Gauge / Transverse Offset

**Question:** What is the transverse hole spacing or offset from the fabrication datum?

Use a top/bottom/section view that shows the hole centers unambiguously. Direction is usually view/object Y, not the longitudinal X chain. Keep the longitudinal pitch and transverse gauge in separate views/chains.

## Pattern 5: Attached-Part Set-Out

**Question:** Where is an attached part relative to the main part?

Declare the target point explicitly:

- near physical face;
- far physical face;
- centerline;
- hole group center;
- system/reference line only when required.

```yaml
measured_object: attached_part
reference: selected main-part datum
arrangement: separate per attached item or group only truly related items
```

Avoid a broad `all attaching parts` request unless all detected parts share the same fabrication question.

## Pattern 6: End Feature / Cope / Notch

**Question:** What dimensions define this end processing?

Use beam-end processing, finite feature points, or contour points according to the actual geometry. Keep feature extents separate from overall length and hole pitch.

Test positive and negative cases:

- feature exists at start only;
- feature exists at end only;
- features at both ends;
- no feature;
- feature size changes.

## Pattern 7: Plate Overall and Features

Separate:

1. plate overall length/width;
2. hole layout;
3. internal contour/cutout;
4. edge bevel or special processing;
5. thickness as label or dedicated view convention.

Do not dimension every contour vertex automatically. Select only points needed to manufacture and inspect the plate.

## Pattern 8: Column Assembly

Typical responsibilities:

- overall column length/elevation datum;
- base plate overall and bolt-hole layout;
- bracket/beam connection elevations;
- cap plate and top feature set-out;
- section-local offsets.

Use a stable vertical datum declared by the project. Do not mix global elevations and local fabrication lengths in an unlabeled chain.

## Pattern 9: General Arrangement

GA chains answer erection/set-out questions:

- grids to member center/system lines;
- bay dimensions;
- level/elevation marks;
- main offsets.

They should not duplicate shop fabrication hole/feature chains. Confirm whether the project uses system line, physical face, or centerline as the erection datum.

## Pattern 10: Sloped, Curved and Faceted Geometry

Automatic dimensions are preferred when a stable request exists. Otherwise use AS parametric manual dimensions:

- slope/angle: declared reference line and direction;
- true arc: center/radius/arc workflow;
- faceted CHS/polybeam: 3-point manual method may be required;
- no plain AutoCAD dimension for fabrication output.

Require a geometry-change update test because non-orthogonal/faceted points are more failure-prone.

## Layering Convention

From nearest to farthest from the view:

1. local feature or hole pitch;
2. attached-part set-out;
3. main-part overall/closing check.

This is a baseline, not a fixed graphic rule. Reverse sides if labels, weld symbols, sections or project standards require it. Preserve chain separation by purpose.

## Pattern Selection Decision

```text
Need a dimension?
├─ Fabrication overall → Pattern 1
├─ Every hole pitch → Pattern 2
├─ Hole-group extent only → Pattern 3
├─ Transverse/gauge → Pattern 4
├─ Attached part → Pattern 5
├─ Cope/notch/end processing → Pattern 6
├─ Plate manufacturing → Pattern 7
├─ Column assembly → Pattern 8
├─ Erection/GA → Pattern 9
└─ Sloped/curved exception → Pattern 10
```
