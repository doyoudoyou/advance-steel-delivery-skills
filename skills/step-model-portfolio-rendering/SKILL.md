---
name: step-model-portfolio-rendering
description: "Use when rendering STEP models for website portfolios."
---

# STEP model portfolio rendering

## Source handling
- Inventory every supplied model into JSON. Preserve each model basename as its project title; do not merge suffixed variants without direction.
- In shell-embedded Python, construct UNC paths with `Path(chr(92)*2 + 'server/share/folder')` when quoting could collapse backslashes. A malformed single-backslash path is not an SMB authentication failure.
- Copy to a local workspace, hash source and copy, and never alter originals. Save large deliverables in a newly named private NAS output directory, not a public webroot.
- Model renders and site photographs are separate media types. Supplied photographs can guide approximate presentation colors, not establish dates, contractual scope, completion status, or exact finishes.
- Preparing render assets does not by itself authorize publishing a new portfolio or uploading raw CAD to a public website.

## Conversion
1. Discover the installed Blender and GPU; run a separate factory-startup background instance, leaving open user scenes untouched.
2. Use a workspace-local Python venv. `cadquery-ocp==7.8.1.1` is verified on Windows. OCP 8.0.1 returned an unregistered `Bnd_Box::Limits` from `Bnd_Box.Get()`, and cast names differ; pin the working version or inspect live APIs instead of altering geometry to bypass binding errors.
3. Use `STEPControl_Reader`; verify read status, roots transferred, nonempty shapes and target units. Default `SystemLengthUnit()==1.0` means millimetres; verify rather than assuming source units.
4. Set explicit absolute and angular tessellation tolerances, e.g. 0.35 mm / 0.18 rad for building-scale imagery. Apply face TopLoc transforms and reverse triangle winding for `TopAbs_REVERSED`.
5. Preserve every imported solid and face. OCCT can split one source `MANIFOLD_SOLID_BREP` into several disconnected bodies, including tiny fragments. Require all source roots to transfer and record root-to-solid counts; never discard fragments to force entity and solid counts to match.
6. Fail on empty roots, untriangulated or omitted faces. Compare all imported face counts with meshed faces. Share vertices inside each source face for curved shading but preserve separate boundaries for hard edges.
7. Store units, source hashes, tessellation settings, recentering and XY rotation in evidence. Preserve gravity/Z; an XY-only PCA alignment changes presentation, not source geometry.

## Rendering and verification
- Derive all construction geometry from STEP. Studio ground and lights are staging, not project terrain. Never invent decks, railings, supports, buildings or landscaping to make a model look complete.
- Label presentation materials and approximate paint colors as such, not as approved/as-built specifications.
- For this user's portfolio, provide at least two different full-model angles and four detail views per model. Preserve verified full views when only more closeups are requested. Render details from independent, genuinely closer cameras at distinct physical regions; do not pass overview raster crops or four near-identical junction views off as coverage.
- Fit overview cameras using every vertex and verify projected limits. For closeups, choose real geometry anchors, vary scale as well as position, and ray-test visibility before rendering; never hide foreground construction to expose a target. Inspect whether each detail communicates useful geometry.
- When a small source anchor has zero visibility, inspect first-hit face/solid IDs and distances before relaxing anything: a bolt-sized seed may be inside an opaque tube. Retarget to a nearby actually visible source surface, probe points on its original triangle, rerun first-hit ownership/distance checks, and record surface-patch scope separately from whole-component framing. Keep all construction visible and visually verify the replacement closeup; never mark the hidden original anchor as visible.
- Use geometry distribution to validate normalized camera seeds: bridges can have different deck/support heights along their length, so a fractional-height target can fall below the actual structure and snap to the wrong end. Inspect local component heights and choose distinct real anchors rather than guessing structural levels.
- Record Blender/Cycles version, GPU, samples, camera, image dimensions, timing and provenance. Use restrained denoising; do not erase fine rods, bolts or gaps with postprocessing.
- Preserve high-resolution PNG separately from WebP. Use contain sizing in portfolio cards instead of cropping the ends of long bridge models.
- Persist batch results, aggregate counts in code against the manifest, recheck source hashes, and verify output hashes after NAS copying. Never declare a partial batch complete.
- Visually inspect each project's views for clipping, missing surfaces, poor contrast and uninformative details. An attractive thumbnail alone is not geometry validation. If a contact sheet suggests a gap, inspect the full-resolution overlap and alternate angle, then compare importer/mesher face counts; occluded edges are not proof of missing geometry and must never be filled by guesswork.

## Delivery
Build a private review gallery and exact-title `projects.json`. Omit unknown year/client/site/scope fields instead of inventing them. Mark imagery as model rendering, not construction photography. Attach a compact WebP/gallery ZIP if full-resolution imagery exceeds chat limits, and give the verified private NAS folder for originals. Distinguish finished render assets from any unperformed website publication.
