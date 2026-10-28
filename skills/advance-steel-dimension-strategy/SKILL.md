---
name: advance-steel-dimension-strategy
description: Use when designing Advance Steel automatic dimensions.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [advance-steel, dimensions, drawing-style-manager, shop-drawings, qc]
    related_skills: [advance-steel-knowledge-router, advance-steel-agent, steel-drawing-analysis-workflow, eircad-advance-steel]
---

# Advance Steel Dimension Strategy

## Purpose

Design, review, troubleshoot, and validate automatic or parametric dimensions in Advance Steel drawings. Convert fabrication intent into a controlled set of `Dimension Request` definitions and dimension chains.

This skill is a decision and validation system. It does not authorize editing a live Drawing Style database, production prototype, model DWG, or generated detail. For implementation, use copied settings and disposable model/detail worksets under the applicable operational skill.

## Evidence Model

Keep three evidence classes separate:

1. **Official current/versioned:** Autodesk Help and Autodesk Support for the named release.
2. **Legacy structural reference:** the older GRAITEC Drawing Style Manager Guide, used for the hierarchy and terminology that still must be checked in AS2025/AS2027.
3. **Community/practitioner:** Autodesk Community, EIRCAD, and GRAITEC articles. Use for troubleshooting patterns, then reproduce.

Load `references/source-index.md` when external evidence or a source refresh is needed.

## Core Mental Model

A reliable automatic dimension is built from the outside inward:

```text
Drawing Style
└─ View
   └─ Dimension Strategy
      ├─ Dimension Chain 1
      │  ├─ Dimension type / presentation
      │  └─ Dimension Definition
      │     ├─ Direction
      │     ├─ Arrangement
      │     └─ Point Selection Rules
      └─ Dimension Chain 2 ...
```

Definitions:

- **Dimension Strategy:** the combination of dimension chains used by one detail view.
- **Dimension Chain:** one dimension type plus one dimension definition.
- **Dimension Definition / Dimension Request:** selects what is dimensioned, in what direction, and where the chain is arranged.
- **Point Selection Rule:** filters model objects and chooses contour, feature, hole, system, center, extreme, or reference points.
- **Dimension Style:** controls graphic appearance such as units, precision, text and arrows. The prototype stores it; Management Tools defaults link automatic dimension types to it.

Do not fix a point-selection problem by changing the graphical dimension style.

## Design Principle: One Chain, One Fabrication Question

Every chain must answer one named question:

- What is the finished main-part length?
- Where is this attached part from the selected datum?
- What is the hole-group edge distance and pitch?
- What are the cope or notch extents?
- What is the transverse offset in this section?
- What overall check dimension closes the chain?

If a chain answers unrelated questions, split it. Use `Do not combine with other dimensions` or separate-per-item behavior when similar collinear chains must remain distinct.

## Mandatory Workflow

### 1. Write the Dimension Contract

Before touching DSM, record:

```yaml
drawing_scope: assembly | single_part | general_arrangement
object_family: beam | column | plate | box_column | other
view: front | top | bottom | section | cut | plan | elevation
fabrication_question: <one question>
datum: physical_end | reference_face | centerline | system_line | grid | level
measured_object: main_part | attached_part | hole_group | feature | contour
point_policy: all | first_last | extreme | center | feature | contour
chain_type: linear_relative | linear_absolute | relative_and_absolute | ordinate | angle | radial | arc | slope
arrangement: global_or_local + side + combined_or_separate
fallback: automatic | AS_parametric_manual | explicit_note
acceptance: <numeric, native, update and visual checks>
```

A field that remains unknown is a design decision, not an implementation detail.

### 2. Confirm View and Model Object Recognition

Autodesk recommends understanding `Model Objects`, object presentation, and labeling before customizing automatic dimensions. Confirm that the intended beam, plate, hole, bolt pattern, feature, or attached part is recognized in the selected view.

A missing or misclassified object cannot be repaired reliably by adding random point rules.

### 3. Start From Desired Output

Sketch or describe the required final chains first. Then build the minimum strategy that produces them. Do not start by editing an unfamiliar request and hoping its name matches.

For each chain:

1. choose the direction (sheet-relative `View X/Y` for horizontal/vertical-on-sheet chains; member-relative `Mp X/Y` only when the member axis maps to the sheet the way the factory request assumes);
2. choose the measured model-object filter, after reading the object set's member roles (factory role sets are often wider than their names; build a USER single-role set when needed);
3. add the minimum point type;
4. add reference points only when a measured point exists;
5. apply point position and visibility filters;
6. choose arrangement and separation;
7. select relative, absolute, ordinate, angle, radial, arc, or slope presentation.

### 4. Use Reference Points as Conditional Datums

`As reference` points provide dimension points only when other measured points exist. Use them for endpoints, extremes, system points, or centers that should anchor a chain but should not create a dimension by themselves.

Example: `Holes - All` plus `Main Part - Extreme as reference` creates an anchored hole chain only when holes are detected.

### 5. Keep Feature and Contour Semantics Separate

- `Object features` correspond to points from finite processing.
- `Object contour without features` includes the element contour and points resulting from infinite processing such as shortening or notches.
- Beam-end processing is a distinct use case when end contours and features must be dimensioned.

Choose the semantic target before selecting point types. Avoid `All points` unless the intended output truly requires every detected point.

### 6. Use Supported Hole-Pattern Topologies

For smart/updateable hole-pattern dimensions, use one of the supported shapes:

- all holes;
- first hole;
- last hole;
- first and last;
- any supported combination above with a valid reference point.

Do not dimension only arbitrary intermediate holes. On update, unsupported intermediate selections can be removed or remain stale depending on manual-dimension defaults.

For a full pitch chain, select every hole center. For an extent-only chain, select first and last. Do not mix the two intents in one unstable partial chain.

### 7. Select Arrangement Deliberately

Record each arrangement as:

```text
G or L   = avoid total geometry or only local geometry
T or B   = above/below; for vertical views this maps to left/right
A or S   = one combined chain or separate chain per detected item
```

Use automatic separation for separate features or attached objects. Use `Group only related dimensions` for groups that must remain associated. Do not combine collinear chains solely because their values or point positions are similar.

### 8. Separate Automatic and Manual Responsibilities

Priority:

1. automatic native chain from the drawing style;
2. Advance Steel parametric manual dimension for a bounded exception;
3. label or explicit note when a dimension type cannot represent the requirement safely.

Do not use plain AutoCAD dimensions on Advance Steel details for fabrication geometry. They do not follow view scale, clipping, movement, or native update behavior.

When a contract chain fails in the style after the diagnostic rounds (e.g. total-only overall length), route it to a scripted post-generation native dimension instead of more DSM guesses: load `references/post-generation-native-dims.md`. Plan the whole drawing as three layers: style chains (main), model roles written upstream so role-based rules match, and a short per-sheet post-generation list.

For manual AS dimensions:

- select the exact detail view first;
- use `Preferred for Manual Dimensions` whenever available;
- for holes, snap center by center;
- treat a red/non-preferred point as an update-risk signal;
- verify after update and save/reopen.

### 9. Protect Shared Definitions

A normal copy may retain references to shared sub-styles. Editing a shared dimension definition or point-selection rule can change every strategy that uses it.

For experiments and project-specific work:

- create a `User` strategy;
- deep-copy the strategy and dependent sub-styles before mutation;
- give each chain and request a unique semantic name;
- record upstream and downstream references;
- never edit an `Advance` system definition directly.

### 10. Validate With Fresh Generation and Update Variants

A dimension strategy is accepted only after:

1. fresh detail generation from a copied model;
2. native object inventory and chain count;
3. numeric/value check;
4. point/grip identity check;
5. visual QA for overlaps, clipping and wrong-side placement;
6. update with no model change;
7. controlled geometry variations;
8. save, close, reopen and recheck.

Use `references/test-matrix.md` for the minimum variants.

## User-Specific Hard Rules

These rules override generic examples:

- Beam-end hole chains must snap each shared control point individually with `CEN` at the exact hole center.
- Validate red grips against the hole-center cross. Numeric closure alone is insufficient.
- A chain that totals correctly but attaches to the wrong native point fails.
- For manual sections, enable ORTHO before selecting the source detail view so the section is perpendicular to the main-member longitudinal axis.
- Drawing orientation acceptance must use the defined project/view rule; left-right appearance alone is insufficient.
- Never move a registered detail DWG away from its model workset for testing.

## Deriving a Style From a User-Finished Drawing

When the user offers a finished, hand-tuned shop drawing as the target for a new style map / drawing style, run it as a propose-confirm-generate-compare loop, not one-shot inference. One drawing is one example: the same 4 dimensioned holes can mean `all holes` or `first-last + pitch`, which only differ on another member.

1. Generate a baseline from the nearest existing factory/HH style on a copied model; the user finishes THAT drawing with native AS dimensions/labels only.
2. Diff baseline vs finished (added / removed / moved chains, labels, views) and draft one Dimension Contract per chain; the user confirms each. Ask for 1-2 more members of the same type (different length / hole count) to disambiguate rules.
3. Map style-level facts directly (views, orientation, scale, sheet); arrangement only to the nearest AS arrangement strategy; manual label drags and plain AutoCAD dims cannot be reproduced and must be listed, not faked.
4. Do not promise automatic chain recovery: native AS dimensions in a detail DWG are `AstDimLineRepr` (`ASTXDIMLINE`) custom entities with no xdata and no public .NET access to their attached object or point type, so values and line positions are all that can be read. Plain AutoCAD dimensions in the same sheet (e.g. `AcDb2LineAngularDimension`) are manual additions; list them as "probably hand-added" and ask. The sidecar `<model>\Databases\revision_*.db` (SQLite, table `tObjDimPts`: Handle, DimType, coordinates) holds candidate dimension points, but its DimType codes are unverified; use it only as a hint.
5. Read the finished sheet from its delivered PDF when one exists (faster and clearer than the DWG): render with PyMuPDF from the AdvanceSteelTools venv (`page.get_pixmap(dpi=200)`), view the whole page, then zoom per view with `vision_analyze` `region` crops to read every chain value.
6. Write the draft as a repo doc (`docs/STYLE-CONTRACT-<mark>-DRAFT.md`): a views table (name / sheet position / orientation), a chains table (id, view, side, what is measured, values, inferred rule), labels, then numbered questions. Mark every cell **[讀]** (read off the sheet) or **[推]** (inferred rule needing confirmation); the questions must cover each ambiguous rule (all end points vs control points only), section placement (fixed vs AS auto layout), suspected manual dims, whether sibling marks share the rules, and the scale when the title block says NTS. Commit, then wait for the user's numbered answers before touching any style.
7. Implement as a deep-copied User style (step 9), via the user's existing backup-then-SQL tools, then validate per step 10 against the finished drawing chain by chain, including end-point identity. Do it in two gated passes: (a) layout only — views, orientation, fixed placement, scale — generate one sheet and get the user's OK; (b) then add dimension chains in batches, regenerating and comparing after each batch.
8. Plan the style rows read-only before any write: copy the factory `AstorDetails.mdf` from the install image (`C:\Autodesk\WI\...\advslp\ENU\AD\ADSK\ADVS\GBR\Steel\Data`) to scratch and attach it READ_ONLY to `(localdb)\MSSQLLocalDB` (never the AS instance); the live file is locked while AS's LocalDB runs, so compare/back it up only after AS is closed. Find the nearest factory style (e.g. column family `Column - front, top, bottom 1:10 CX`) and list its `DetailStyle.Request1..n` → `DetViewRequest` (Scale, ArrangeDir, DimStrategy, ObjReprMap). `DetViewArrangeStrategy` only stores view spacing, not positions; per-view side comes from `DetViewRequest.ArrangeDir` (0 main, 1 top, 2 bottom, 3 left, 4 right — inferred from factory view names, verify on a generated sheet). Choose a new key range above the factory maximum and clear of earlier user ranges, and abort the whole batch if any target key already exists.
9. Before the first write, state the exact rows to be added, the backup location, and require the user to close any AS they started (check `Get-Process acad`; never kill a process you did not launch), then wait for an explicit OK.
10. Check model roles before mapping chains to factory rules: many factory point rules select by Model Role, and parts with Role `-` match none of them. Read roles from a model copy; if they are missing, ask the user which role each part type gets (cap plate vs end plate etc. changes which rules include it) and set them only on the copy.
11. Write, generate one sheet and compare per `references/style-write-and-generate.md`; change one setting per round when the user asks, and run a factory-process control before blaming the USER rows.

## Writing and Checking a USER Style

Load `references/style-write-and-generate.md` for the backup-then-transaction write recipe, the rows a new assembly style needs, one-sheet generation + PDF review (extents plot to see overflow), and known traps (alternative scale sets override view scale; `DetailOrientation` does not flip columns and `SystemAndBox` = Rear fixes only some marks, see Sheet Orientation Gate; extra factory views overflow the frame; reading `.upd` to tell hand edits from style output).

Layout round order that converged: scale (step `AlternativeScales` -> None) -> orientation (front view `SystemAndBox`) -> view list trimmed to the contract (this alone fixed frame overflow) -> placement only if still needed -> only then dimension chains, in small batches (overall + segment chain first), each with a written plan of exact USER rows/keys and the user's OK before writing. `references/dsm-layout-knobs-as2027.md` lists which knobs had an effect. One knob per round, each with backup, dry run, read-back, regenerate, compare, and a doc section + commit; report each round as a table (check / result) with the next step as two numbered options. Before any progress inventory or review, run `git log <last commit you know>..HEAD` and read the docs those commits touched: the same work may have advanced in another session (e.g. a Telegram session), and reporting from memory gives stale status. Correct your earlier statement explicitly when it turns out stale. When the user asks for a progress inventory (盤點), answer with three tables: stages (done / in progress / not started, with doc section), chains (status per contract chain), and unresolved technical difficulties (difficulty / current state / where it is stuck), then the two options; when a chain has failed several rounds, offer a one-sheet diagnostic (see reference) instead of another single-value guess. When asked to re-review the overall development (重新檢討), write it as a repo doc (`docs/<PROJECT>-REVIEW-<date>.md`: current status table with evidence, problems such as direction drift from the roadmap / single-member validation / machine-local state / doc contradictions, recommendations with a decision table of options), add a dated pointer at the top of the roadmap and of any status doc it supersedes, update memory with the new status, then end with the open decision as two numbered options.

## Post-Generation Native Fallback (verified AS2027, T-1)

For chains the style cannot express (total-only, single hole row), add native `AstDimLineRepr` after generation with the Live Link repo tool `tools/postdim/postdim.py <detail.dwg> <spec.json> [--save]` (doc `docs/POSTDIM-PROBE.md`). It maps atomic view reprs to model handles with the AtomicModelHandleProbe DLL, takes part bbox corners + `osnap _end`, and calls `_AstM16CommDetAddUCSLinearDim`. Pitfalls: open AS on the MODEL and open the detail from that session; `AstDetHoleRepr` is one object per hole GROUP, so its bbox centre snaps to an arbitrary row: grid-scan `osnap _cen` over the group and pick the row. AS dims expose no value via COM, so verify through a `-PLOT` PDF text layer plus a visual check. NETLOAD prompts unless the DLL sits in a `TRUSTEDPATHS` folder (`<WORKSPACE>/ASLL-trusted\...` was added on the AS workstation). Do not COPY+EXPLODE AS dims to read them; this leaves stray duplicate dims.

Specs name parts by mark (resolved via `drawing.preflight`) and hole rows, not coordinates; corner specs assume an upright member. For a whole family, run the repo `tools/postdim/pipeline.py` (direction → generate → post-dims → PDF checks in one run, in background); post-dims must be re-applied after every regeneration.

## Sheet Orientation Gate

Before building chains or post-dims for a member family, generate EVERY mark of the family once and check orientation. One upright sheet proves nothing: AS orients assembly sheets from the whole assembly (attached-plate rotation), so a style-level knob that fixed one mark (front view `SystemAndBox` = Rear) left siblings horizontal or upside down. The per-assembly control is the model-side `_AstM14SetAssemblyDetCS`; recipe and limits are in `references/post-generation-native-dims.md`. It only works with `TILEMODE=1` (model tab): in a layout it prints `This command only applies to model DWGs`, and a scripted call finishes with no error but changes nothing, so set and assert TILEMODE first (repo `tools/postdim/detcs_one.py`). With it set per mark (UCS X = attached plate face, Y = up), keep the front view on Object Front; T-1..T-7 all came out upright.

## Point Classification Schema

Load `references/point-selection-schema.md` when you need how AS classifies dimension points (DSM table columns Objects / PointType / position restrictions, the +1000 reference flag, and how `tObjDimPts.DimType` likely maps).

## Reusable Chain Patterns

Load `references/chain-patterns.md` when selecting automatic chain semantics for overall size, hole pitch, hole extent, gauge, attached-part set-out, end features, plates, columns, GA, or sloped/curved geometry.

## Baseline Strategy

Load `references/user-baseline-strategy.md` for the user-approved `HH-DIM-BEAM-ASSY-V1.0`. It defines the beam assembly design baseline. It is not a production DSM implementation until copied User definitions pass the complete fresh/update/reopen test matrix.

## Naming Convention

Use names that expose intent and placement:

```text
XX_<scope>_<view>_<object>_<purpose>_<direction>_<arrangement>_Vnn
```

Examples:

```text
XX_ASSY_FRONT_MP_OVERALL_X_GBA_V01
XX_ASSY_FRONT_HOLE_PITCH_X_GTS_V01
XX_ASSY_SECTION_HOLE_OFFSET_Y_GTS_V01
XX_ASSY_FRONT_ATTPL_SET_OUT_X_LBS_V01
```

Do not rely on opaque copied names such as `Copy of Mp X - Extreme GTA`.

## Failure Diagnosis

| Symptom | First check |
|---|---|
| Missing chain | Direction first (a member-Y chain on a column front view is depth and draws nothing); then any single point rule that finds nothing drops the whole chain — swap one rule at a time for a proven one |
| Extra segments from parts you did not mean | Object set members (role set includes base plate / blank role / shear studs); replace with a USER single-role set |
| Overall chain split into per-part segments | Point restrictions act per object (both ends of each part); request `[Group]`, `AllowCombine` and strategy-item `HideDimensionPoint` do not merge it — add a scripted post-generation native dim (see reference) |
| Chain appears with no target feature | Reference point used as measured point or over-broad point type |
| Too many points | `All points`, feature/contour overlap, visibility too broad |
| Wrong attached part | Point position relative to object vs main part |
| Chains merged | A/S arrangement, group-related, do-not-combine |
| Wrong side | T/B setting and vertical-view mapping |
| Wrong datum | Absolute/ordinate origin and main/total assembly reference |
| Manual points disappear | Non-preferred points or unsupported partial hole pattern |
| Update gives stale value | Invalid manual point retained; native grip did not follow geometry |
| Editing one rule changes other styles | Shared sub-style was copied rather than deep-copied |
| Good values but bad fabrication instruction | Wrong point identity, wrong view, or mixed fabrication questions |

## Completion Criteria

A proposed dimension strategy is complete when:

- every chain has one fabrication question and one declared datum;
- every request names object filter, direction, point types, visibility, position and arrangement;
- automatic/manual responsibility is explicit;
- shared-definition risk is eliminated or recorded;
- test geometry covers present, absent, moved and count-changed features;
- native point identity and visual output are verified;
- AS version, source style, prototype and generated-detail evidence are recorded.
