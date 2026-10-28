---
name: advance-steel-agent
description: "Use when building or operating controlled Advance Steel agents."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [advance-steel, autocad, ai-agent, steel-detailing, automation, frame-replacement, drawing-index, pdf-delivery]
    related_skills: [autocad-automation, advance-steel-knowledge-router, steel-drawing-analysis-workflow]
    scope: class-level umbrella for Advance Steel AI Agent workflows
---

# Advance Steel Agent

Use this skill when the user wants Hermes to learn, design, build, or operate an AI Agent workflow for Autodesk Advance Steel steel-detailing tasks: reading structural data, planning model creation, drawing centerlines, creating members, verifying the model, preparing drawings/BOMs, or building a deeper Advance Steel integration.

This skill is intentionally a **class-level umbrella**. Keep one-off project details in `references/` and reusable scripts/templates under `scripts/` or `templates/`.

## Core principle

Do **not** treat the agent as a random command typer. Treat it as a controlled steel-detailing assistant with a data pipeline:

```text
source drawings / user tables
→ structured project data
→ confirmation only for unresolved engineering ambiguity, new mutation authorization or promotion
→ scripted modeling actions
→ verification report
→ drawing/BOM workflow
```

The agent should avoid guessing structural geometry, section sizes, or connection intent. Ambiguous engineering inputs must be surfaced for confirmation.

## Recommended architecture

```text
User / Telegram / CLI
        ↓
Hermes conversation + planning layer
        ↓
Project data layer
  - project.yaml
  - grids.yaml
  - members.yaml
  - sections.yaml
  - operation logs
        ↓
Execution layer
  - Python + pywin32 for AutoCAD COM
  - Win32 API for recovery / UI support
  - C# in-process plug-in for reliable Advance Steel .NET API access
        ↓
Advance Steel / AutoCAD
        ↓
Verification + reporting layer
  - model_check.md
  - screenshots
  - DWG/PDF/BOM outputs
```

See `references/system-architecture.md` for the detailed roadmap and MVP breakdown.

## Safe operating rules

1. **Plan before modifying DWG.** Any operation that changes a drawing should have a short plan and expected verification result.
2. **Back up or work on a copy** before model-changing operations.
3. **Use data files for geometry.** Prefer `project.yaml`/`members.yaml` over natural-language coordinates.
4. **Require confirmation** for missing or ambiguous section, material, elevation, grid, or connection data.
5. **Verify after every modeling step.** Count relevant AutoCAD/Advance Steel entities and write a short report.
6. **Stop on unexpected modal dialogs or command prompts.** Do not blindly continue sending commands.
7. **Separate temporary test models from real project DWGs.** Use a 3-member sample only for first-time integration without a project probe contract. Existing project family probes replace this generic MVP; do not run both.
8. **Preserve registered workset structure.** For existing details, copy the model together with its complete `<model-stem>/` sidecar tree, including `Details/`, `Databases/`, revision/update metadata, and any other registered files; never treat a standalone moved detail DWG as registered.
9. **Require clean state and compensating rollback.** Mutating detail operations begin only at `DBMOD=0`. Assume a COM call may mutate the DWG and then throw: infer attempted displacement from complete before/after bboxes, roll back every observed mutation, compare full min/max bbox plus PaperSpace identity, and keep a hash-verified pre-operation backup. Save only after exact restoration; otherwise fail closed and restore the backup.
10. **Resume by artifact identity, not path existence.** Checkpoints must validate path, bytes, and SHA-256 from the latest completed stage. Existing registered worksets must also revalidate the backup root, copied model/detail, and the complete copied model-sidecar manifest (`Details`, `Databases`, revisions, update files, and peers); a missing or changed recovery backup stops resume before mutation.
11. **Never globally terminate or globally click in production.** Production runtime must not use `taskkill /IM acad.exe`, `SetCursorPos`, global mouse events, or unscoped keyboard input.
12. **Scope every UI surface to one Advance Steel instance.** Bind Document Manager, Plot Devices, execute, Save/PDF dialogs, and attention windows to the PID obtained from the selected document's application HWND; unknown, cross-process, or ambiguous windows fail closed.
13. **Final drawing acceptance uses native persistence.** Require save, `DBMOD=0`, close/reopen persistence, Document Manager native batch plot, and readable PDF evidence.
14. **Require a project-specific frame before frame replacement.** Every project must use its own frame supplied by the user in advance. Before mutation, validate its extents, units, orientation, insertion scale, and effective boundary in the target A3 Layout. Missing, oversized, undersized, ambiguous, or non-uniformly scaled frames fail closed pending user confirmation.
15. **Keep each repo on its product line.** When a side track grows into standalone scripts/SQL pipelines outside the product's deliverable (e.g. drawing pipelines inside the Live Link repo with no GH component), stop and offer the user a scope review; record the home in an ADR and add `FROZEN.md` (fixes only until moved) to the folder. Moving work into another repo that has uncommitted changes is the user's call.
16. **Report in Traditional Chinese (Taiwan)** for this user, even after long English tool output or a context compaction.
17. **Re-sync with the repo before any status report.** After a compaction or a gap, run `git log --oneline <last-known-commit>..HEAD` and read the new docs first; work may have landed outside the summary, and reporting the summary's state overclaims stale blockers. Correct an earlier wrong status explicitly in the next reply.

## MVP workflow

For first-time integration without a project family-probe contract, start with a small 3-beam test model. Where a project contract exists, follow its fresh native-family probes and acceptance gates instead; do not add a second MVP run:

```text
1. Check AutoCAD / Advance Steel connection.
2. Validate project YAML.
3. Draw beam/column centerlines from YAML.
4. Verify centerline count and handles.
5. Create Advance Steel members from centerlines.
6. Produce a section-group report.
7. User or plug-in assigns sections/materials.
8. Verify model object counts and produce model_check.md.
```

## Data-driven project shape

Use YAML as the contract between the AI and modeling tools:

```yaml
project:
  name: sample_steel_frame
  unit: mm
  material: CNS SN490B

levels:
  - name: 2F
    elevation: 4000

members:
  beams:
    - id: B001
      mark: Sb1
      section: RH488x300x11x18
      material: CNS SN490B
      start: [0, 0, 4000]
      end: [6000, 0, 4000]
      camber_mm: 30

  columns:
    - id: C001
      section: H300x300x10x15
      material: CNS SN490B
      start: [0, 0, 0]
      end: [0, 0, 4000]
```

Validation minimums:

- every member has `id`, `section`, `material`, `start`, and `end`
- `start != end`
- units are explicit
- level/elevation is explicit when modeling multi-level structures
- section names come from the design documents or confirmed section database

## Reference Router

Keep this umbrella compact. Load only the reference required by the current phase.

| Need | Reference / Skill |
|---|---|
| Detailed system architecture and MVP roadmap | `references/system-architecture.md` |
| Bridge, COM, MCP, C# plug-in and execution mechanics | `references/execution-layer-guidance.md` |
| Frame replacement, cover/index and drawing-package agents | `references/steel-drawing-specialist-agents.md` |
| Accumulated AS2027 failure modes and verified runbook details | `references/pitfalls-and-runbook.md` |
| Frame replacement specification | `references/frame-replacement-agent.md` |
| Grasshopper-Advance Steel live-link plugin project (roadmap, AS2027 .NET facts) | `references/grasshopper-live-link-project.md` (at size limit: put new depth in a topical sibling file) |
| Live Link selection round-trip (Find Linked Component) and assemblies | `references/live-link-selection-and-assembly.md` |
| Live Link components fed by native GH geometry (Beam.ByCurve, mixed-kind sync RPC, trusted-server update) | `references/live-link-native-geometry-inputs.md` |
| Cover/index specification | `references/cover-index-agent.md` |
| Low-level COM, DXF, SCR and IPC mechanics | `autocad-automation` |
| Official/manual/local API research routing | `advance-steel-knowledge-router` |

## Responsibility Boundary

- This skill owns **orchestration, job contracts, safety policy, phase routing and acceptance**.
- `autocad-automation` owns low-level COM, DXF, SCR, MCP IPC and command mechanics.
- Task-specific Skills own their narrower domain rules; do not copy those procedures back into this umbrella.
- Inside `AdvanceSteelTools`, project `AGENTS.md`, `config/production-tools.json`, the selected job and workflow are authoritative.

## Hermes skill strategy

When teaching Hermes a new Advance Steel procedure:

1. First capture the **SOP** in this skill or a reference file.
2. Then create deterministic scripts for repeated actions.
3. Keep project-specific geometry, drawings, and command transcripts in `references/`, not in the main SKILL.md.
4. Promote only stable, reusable patterns into the main skill body.

## Acceptance Summary

Before reporting completion, require all applicable gates:

1. Accepted/production baseline remains unchanged; all mutation occurred in a complete disposable work copy with fresh registered details where required.
2. Exact source model, document, sidecar registration, object identity and native class were verified.
3. Unknown modal state, ambiguous mapping, unsupported profile/family or incomplete evidence failed closed.
4. The result remains native Advance Steel data rather than screenshot, exploded geometry, label text or attribute-only substitution.
5. Save, close and reopen persistence passed.
6. Final state is `CMDACTIVE=0`, `CMDNAMES=''`, `DBMOD=0` unless an explicitly documented disposable no-save export contract defines DBMOD as not applicable after close.
7. Drawing acceptance includes Document Manager native plot, readable PDF and required visual/semantic evidence.
8. Evidence includes hashes, counts, manifests, failure records and rollback/restore proof appropriate to the selected workflow.

## Support files

- `references/system-architecture.md` — detailed AI Agent architecture, MVP, phases, and risk controls.
- `references/execution-layer-guidance.md` — bridge, COM, MCP, C# and execution-layer guidance.
- `references/steel-drawing-specialist-agents.md` — frame, cover/index and drawing-package agent runbook.
- `references/pitfalls-and-runbook.md` — accumulated AS2027 pitfalls and verified recovery rules.
- `references/frame-replacement-agent.md` — 圖框更換、BOM 配置、框外物件清理、Layout 出圖與 QC 專責 Agent。
- `references/cover-index-agent.md` — 封面、圖號表、多頁 Layout、完整施工圖合併與驗證專責 Agent。
