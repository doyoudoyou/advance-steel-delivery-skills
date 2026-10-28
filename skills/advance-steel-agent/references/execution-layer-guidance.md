## Execution layer guidance

### AdvanceSteelBridge HTTP 中介層 (verified 2026-07)
Hermes should not drive Advance Steel DLLs directly. Historical source bridge: `<USER_HOME>/Documents\AdvanceSteelTools\tools\AdvanceSteelBridge\` (`Bridge.cs`, `smoke_test.py`, README), not a local deployment. The expected local bridge is `<USER_HOME>/Documents/AdvanceSteelTools/tools/AdvanceSteelBridge/`; `tools/`, `Bridge.cs` and `smoke_test.py` are missing. Before NETLOAD or smoke tests, run the `autocad-automation` local preflight and verify the selected bridge source, DLL, SDK, copied DWG and runtime; fail closed on missing resources. The following API contract and live results describe historical source evidence, not a running local endpoint. It exposes `http://127.0.0.1:8765` with `GET /health`, `POST /commands`, `GET /commands/{id}`, and `GET /model/objects`.

Supported typed commands: `ping`, `create_beam`, `create_column` (default role `Column`), `create_plate`, `query_object` / `query_by_handle`, `delete_object`, `numbering`, `list_model_objects`.

**Validation (fail-closed):**
- create ops require `unit:"mm"`
- coordinates must be complete `[x,y,z]`
- plate thickness must be `> 0`
- max 1 create item per command
- profile must exist in AS2027 AstorProfiles via ODBC (`(localdb)\AdvanceSteel2027` → `ProfileMasterTable` → section table `SectionName`/`StandardName`); do **not** trust `ProfilesManager.GetProfileType()`
- `delete_object` requires prior `query_object` one-time `query_token` (5 min, bound to document+handle+UniqueId) **and** `confirm:true`
- `numbering` requires `confirm:true` (defaults: SP unique false / MP unique true, methods 2, starts 1000/1, reuse on)
- audit log: `%LOCALAPPDATA%\HermesAdvanceSteel\bridge-audit.jsonl`

**Python / MCP access:**
- client: `from as_bridge import AdvanceSteelBridgeClient`
- MCP tool: `bridge` on `as-worker-mcp` (`health`, `create_beam/column/plate`, `query_object`, `delete_object`, `numbering`, `list_objects`)

Load path: raw `TcpListener` loopback; main-thread queue via `Application.Idle` + `PostMessage(WM_NULL)`; model writes use `LockDocument` + `DocumentAccess` + `Commit`. Build with .NET 10 against AutoCAD 2027/ADVS managed DLLs **and** `ADVS\System.Data.Odbc.dll` (`Private=false`). Load via no-space `/b` SCR (`C:/ASDump/`). Unsigned DLL security prompt must be clicked by the user (Load Once/Always Load)—automation must not click it. `/health` may take 60–90s after AS launch. Live smoke: `python tools/AdvanceSteelBridge/smoke_test.py --apply` on a `test`/`copy` DWG. Verified validation+cleanup on `C:\ASDump\bridge_validation_test.dwg`.

### MCP File IPC (preferred)
Use Hermes `autocad-mcp` MCP server with File IPC backend for background AutoCAD/Advance Steel control — no focus steal, full tool support (entity CRUD, layers, blocks, dimensions, zoom, undo, PDF plot, LISP execution). Reference: `autocad-automation` skill.

### Python / pywin32 layer

Good for:

- checking AutoCAD connection
- listing visible AutoCAD/Advance Steel windows
- drawing AutoCAD centerlines via COM
- running carefully tested commands
- writing verification reports
- simple highlight/selection helpers

Avoid:

- relying on natural-language prompts inside AutoCAD
- sending long unverified command chains to real project drawings
- using external Python to directly load Advance Steel .NET modeler DLLs for in-process-only APIs

### Isolated .NET probe builds

Use `dotnet build <project.csproj> -c Release --artifacts-path <short-absolute-root>` for SDKs supporting artifacts output. This keeps each referenced project's intermediates separate. Do not pass one shared global `BaseIntermediateOutputPath` to a multi-project build: different target frameworks can overwrite the same `project.assets.json` and produce `NETSDK1005`. Record exact binary hashes after copying to the run evidence directory; compiler success does not establish native activation or persistence.

### C# plug-in layer

Use an AutoCAD/Advance Steel **in-process C# plug-in** for reliable access to Advance Steel .NET APIs, especially for:

- setting profile section names
- setting materials
- reading/modifying Advance Steel model objects
- numbering automation
- drawing/BOM automation

Pattern for section assignment:

```csharp
StraightBeam beam = DatabaseManager.Open(beamId, OpenMode.kForWrite) as StraightBeam;
if (beam != null)
{
    beam.SetProfSectionName("Class#@§@#SectionSize");
    beam.UpdateModel();
    beam.Dispose();
}
```

Do not assume the internal section string. Confirm the Advance Steel profile database class and section size naming first.

