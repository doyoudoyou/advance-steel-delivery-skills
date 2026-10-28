# Advance Steel AI Agent System Architecture

This reference captures the reusable design that emerged while planning an AI Agent system for Autodesk Advance Steel. Keep project-specific geometry and transcripts elsewhere; this file is the class-level roadmap.

## Goal

Create an AI Agent that can safely assist with steel modeling and drawing production in Advance Steel:

1. understand structured engineering inputs
2. produce a modeling plan
3. control AutoCAD/Advance Steel through deterministic tools
4. verify the resulting model
5. support drawing/BOM workflows
6. eventually use an in-process C# plug-in for deep Advance Steel API operations

## Layered architecture

```text
User / Telegram / CLI
        ↓
Hermes Agent
  - conversation
  - planning
  - skill loading
  - safety checks
        ↓
Project data layer
  - project.yaml
  - grids.yaml
  - members.yaml
  - sections.yaml
  - operation logs
        ↓
Execution layer
  - Python pywin32 controller
  - Win32 recovery / UI helpers
  - C# Advance Steel plug-in
        ↓
Advance Steel / AutoCAD
        ↓
Verification / reporting
  - entity counts
  - handle maps
  - model_check.md
  - screenshots
  - exported drawings / BOMs
```

## Recommended phases

### Phase 0 — Safety boundaries

- define what the agent may modify
- always work on copies or backups for destructive actions
- require confirmation for ambiguous engineering inputs
- stop on unexpected prompts or dialogs
- write operation logs

### Phase 1 — Skill and SOP

Create/maintain a class-level Hermes skill (`advance-steel-agent`) with:

- safe operating rules
- data-driven modeling process
- AutoCAD/Advance Steel tool responsibilities
- known pitfalls
- references to project-specific notes

### Phase 2 — Data-driven modeling schema

Use YAML as the contract. Minimum fields:

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
  columns: []
```

Validation rules:

- all members need `id`, `section`, `material`, `start`, `end`
- coordinates are numeric 3D points
- no zero-length members
- units are explicit
- section/material names come from design docs or a confirmed database

### Phase 3 — Python control MVP

Python is best for orchestration and AutoCAD COM automation:

- `check_connection.py` — detect AutoCAD/Advance Steel and ModelSpace access
- `recover_esc.py` — send ESC to recover from command/modal states
- `draw_centerlines.py` — draw data-driven centerlines
- `verify_model.py` — count entities and write reports
- `group_by_section.py` — produce section grouping reports
- `highlight_group.py` — assist manual section assignment

MVP success criteria:

- create a 3-member sample from YAML
- write a handle map for centerlines
- verify object counts
- no irreversible action without backup/copy

### Phase 4 — Advance Steel member creation

Create members from centerlines using tested Advance Steel commands or the C# plug-in. The agent must verify resulting entity counts and not rely on command success alone.

Short-term: use known stable command sequences only after test-model verification.

Long-term: expose plug-in commands for deterministic operations:

```text
AICREATEMEMBERS project_members.json
AISETSECTION B001 RH488x300x11x18
AISETMATERIAL B001 CNS_SN490B
AIVERIFYMODEL
```

### Phase 5 — Section/material assignment

Short-term:

- generate section-group reports
- highlight/select one group at a time
- user confirms GUI assignment
- verify afterward

Long-term:

- C# in-process plug-in calls Advance Steel .NET APIs
- confirm internal profile database names before assignment
- write back verification results to JSON/logs

C# concept:

```csharp
StraightBeam beam = DatabaseManager.Open(beamId, OpenMode.kForWrite) as StraightBeam;
if (beam != null)
{
    beam.SetProfSectionName("Class#@§@#SectionSize");
    beam.UpdateModel();
    beam.Dispose();
}
```

### Phase 6 — Drawing/BOM workflow

After the modeling MVP is stable, add SOP/tooling for:

1. model check passed
2. numbering
3. assembly drawings
4. single-part drawings
5. BOM/material list
6. DWG/PDF export
7. final drawing checklist

## Risks and controls

| Risk | Control |
|---|---|
| AI guesses geometry | require structured YAML + confirmation |
| Commands modify real drawings | backup/copy before mutation |
| Modal dialogs block automation | ESC recovery + stop on unexpected state |
| GUI-only section selection | short-term manual grouping; long-term C# plug-in |
| External Python cannot access in-process APIs | use C# plug-in for Advance Steel .NET API |
| Model appears created but is wrong | always verify counts/handles/reports |

## First MVP file layout

```text
advance_steel_agent/
├── README.md
├── examples/
│   └── sample_project.yaml
└── tools/
    ├── as_common.py
    ├── check_connection.py
    ├── recover_esc.py
    ├── draw_centerlines.py
    └── verify_model.py
```

## Rule of thumb

Use Hermes for reasoning, planning, validation, and orchestrating deterministic tools. Use Python for safe external automation and reporting. Use C# in-process plug-ins for authoritative Advance Steel model mutation.
