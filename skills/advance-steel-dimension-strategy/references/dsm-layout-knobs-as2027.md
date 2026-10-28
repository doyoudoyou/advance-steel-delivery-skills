# AS2027 drawing-style layout knobs: what actually moved the result (column assembly test)

These were verified on one tube column (Plum Tree T-1, A3, process 33021 → step 33022 → style 33001), generated from a copy of the model. They are not proven for other members or models.

## Scale
- Scale was being overridden by `DetailProcessStep.AlternativeScales`. Factory set 13 (1:5/10/15/20) overrode the view's 1:25, and AS picked 1:20.
- Fix: set the USER step's `AlternativeScales` to 16 ("None"). 1:25 then held.
- For a family with tall members, point the USER step at a USER scale set instead (`DetailProcessScales` row + one `DetailProcessScalesItem` per scale, e.g. 0.04 and 1/30): AS picks a larger scale from the set only when the sheet does not fit, so the 4930 column took 1:30 while 4530 columns kept 1:25. The pick is not predictable: a same-height sibling stayed 1:25 and touched the frame top. When every sheet must fit, give tall members their own process/step with a one-scale set and route them by computed assembly length, instead of trusting the auto-pick.

## Upside-down column
- `DetailStyle.DetailOrientation` 1, 3 and 4 gave identical drawings: pixel-identical between 3 and 4, and visually identical for 1.
- `CoordSystemSelector` has only one value (1) across all 205 factory steps, so there is nothing to try.
- The factory process 3 drawing (style 6) was also upside down. This is not a USER-row bug.
- Swapping the beam's start and end via beammod.sync was refused, because connected welds and bolts can't follow.
- `SystemAndBox` 1 "Object Front" → 2 "Object Rear" made ONE column upright, but it is not a fix: across seven identical-type columns with the same style, identical main-part CS, `Angle` 0 and bottom→top start/end, some came out vertical and some horizontal. The only difference was the plan rotation of the attached plates, so AS orients the sheet from the whole assembly, not the main-part axes. Check orientation on several marks of the family before accepting any style-level orientation knob.
- The native per-assembly control is `_AstM14SetAssemblyDetCS` (palette Tools → "Define assembly detailing direction"; model DWG only): UCS X = sheet horizontal, Y = sheet vertical for the front view. It is stored per assembly and survived a renumber that kept the marks. Unattended recipe (requires TILEMODE=1): `post-generation-native-dims.md` → Assembly detailing direction; with it set on every mark and the front view on Object Front, the whole family came out upright. Keep the style's SystemAndBox and the assembly direction decision together (Rear on top of a set direction turns the sheet upside down) and regenerate the whole family after either changes.
- The user's original upright drawings were flipped by hand (confirmed by the user). The `.upd` sidecar records the machine, process and style used.

## Views outside the frame
- Cause was view count, not a placement knob. With 5 views (factory column style) the stack overflowed; with 3 (front, bottom, sections) the top still stuck out ~22 mm; with only front + sections (`[Number of items]`=2) the whole sheet fit inside A3 at 1:25 (extents 420 × 283 mm). Trim views one at a time and re-plot extents before touching placement.
- After the front view is switched to Rear, the factory 'bottom' view shows the top connection, not the base plate; the base plate is already shown by a section, so drop that view.
- Placement knobs, for reference if trimming is not enough: `ViewArrangeStrategy` only sets spacing between views (0–40 mm); `DetailStyle.ObjectPosition` (0/1/3/4) has unknown meaning; the factory prototype `UK-ASSEMBLY-A3.DWG` (FilenameSelector 20007 → `DetailFilenameSelector.Prototype`) has a paper-space viewport 724.75 × 341.33 mm, taller than the A3 frame. This viewport did NOT stop AS from switching to a larger alternative scale when the sheet overflowed, so try a scale set before building a private prototype. A private prototype means copying that DWG under a new name plus a USER filename-selector row; never edit the factory file.

## Method that worked
- Change one knob per round, from a PS1 script: dry run, stop LocalDB, back up 4 files, then a single-transaction UPDATE guarded by the expected old value, and read back that factory rows are unchanged.
- After each change, regenerate only that handle.
- Check the result with an accoreconsole `-PLOT` of the Extents to PDF. `-EXPORT CURRENT` only plots the layout window and hides content outside the frame.
