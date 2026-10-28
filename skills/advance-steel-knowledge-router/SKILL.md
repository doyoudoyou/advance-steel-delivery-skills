---
name: advance-steel-knowledge-router
description: Use when researching Advance Steel manuals and APIs.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [advance-steel, manuals, api, documentation, forums, standards]
    related_skills: [advance-steel-agent, autocad-automation, eircad-advance-steel, grounded-citations]
---

# Advance Steel Knowledge Router

## Overview

Use this skill to answer questions from Advance Steel manuals, API documentation, standards metadata, technical books, Autodesk Community, or specialist technical articles. It is a **research and evidence router**, not a CAD mutation skill.

Always separate:

1. **documented fact** — current Autodesk Help, installed Autodesk XML docs, or official standards metadata;
2. **observed behavior** — reproduced on a named Advance Steel version and disposable work copy;
3. **community suggestion** — forum, reseller FAQ, video, or personal workflow that still needs validation.

For any action that modifies DWG, load `advance-steel-agent` or `autocad-automation` after research is complete. Their production safety rules remain authoritative.

## When to Use

Load this skill when the user asks to:

- find or explain Advance Steel commands, workflows, FAQ, drawing behavior, numbering, BOM, prototype, or setup documentation;
- identify Advance Steel .NET API assemblies, namespaces, types, methods, or version availability;
- compare official documentation with Autodesk Community, GRAITEC, EIRCAD, or another practitioner source;
- determine whether a rule belongs to Autodesk software behavior, a project standard, or an engineering code;
- turn an Advance Steel manual, API document, or technical reference into a grounded SOP or reusable skill update.

Do not use this skill as structural design approval, connection-capacity verification, or permission to modify a live DWG.

## Evidence Hierarchy

| Level | Source | Permitted claim |
|---|---|---|
| A | Current-version Autodesk Help; installed same-version Autodesk XML API docs; current official standards metadata | State as documented, with version and source |
| B | Older Autodesk Help/API guide or Autodesk implementation material | Use as versioned conceptual guidance; re-check current version |
| C | Autodesk Community, Autodesk University class material, GRAITEC technical FAQ | Treat as practitioner guidance; reproduce before production |
| D | General forums, blogs, videos, cached summaries | Discovery only; never sole authority for engineering or mutation |

If sources conflict, prefer the highest level that matches the user's exact Advance Steel version. Report the conflict instead of blending the claims.

## Mandatory Workflow

### 1. Define the question and version

Record:

- target Advance Steel version;
- object or workflow being investigated;
- whether the answer is read-only research, troubleshooting, or a proposed mutation;
- whether project specifications or licensed standards control the decision.

**Completion:** the answer cannot silently mix AS2025, AS2027, or older forum behavior.

### 2. Load only the relevant reference

- General manuals and source authority: `references/source-index.md`
- AS2027 .NET API names and fingerprints: `references/api-2027-local-reference.md`
- CNS/engineering-code and copyright boundaries: `references/standards-boundaries.md`

Do not load every reference by default.

### 3. Verify current facts

- For software behavior, inspect the matching Autodesk Help version.
- For API availability, verify the type/member in the installed version's XML documentation before proposing code.
- XML presence proves the member is documented, not that a specific runtime call sequence is safe.
- For forums or technical articles, capture author/date/version when visible and identify the claim as community evidence.

**Completion:** every external claim has a URL or exact local file path; unsupported claims are labeled unverified.

### 4. Apply the version gate

- A public AS2022 API page may explain an architecture, but it does not prove availability or behavior in AS2025/AS2027.
- A member found in AS2027 XML must not be projected backward into AS2025 without checking AS2025 docs or runtime.
- A forum limitation from an older release must not override newer same-version XML docs or reproduced production evidence.

**Completion:** each API recommendation states the version evidence supporting it.

### 5. Route action separately

If the user wants implementation:

1. load the matching operational skill;
2. use a copied model and complete sidecar workset;
3. create the smallest disposable test;
4. verify persistence, native object identity, and output artifacts;
5. promote only reproduced behavior into an operational skill.

Never turn a forum recipe directly into production CAD execution.

## Manual and Workflow Research

Start with Advance Steel's current Help navigation for:

- What's New
- Get Started and 3D Modeling
- Numbering
- Create and Manage Drawings
- Collaboration and Dynamo
- FAQs
- Developers
- Installation

Treat BOM templates, drawing styles, prototypes, numbering, and Document Manager as separate subsystems. A fix in one does not prove the others are correct.

For output questions, require a generated sample drawing or native Document Manager result; a style name or UI setting alone is not verification.

## API Research

When same-version XML omits a constructor or default, inspect installed PE metadata and managed IL statically with dnfile/dncil instead of executing Autodesk assemblies outside the CAD host. Metadata parameter names can identify overload intent; follow the actual constructor call chain to confirm constants passed to native entry points. Keep raw signature/call-chain evidence and distinguish static availability/defaults from native behavior. In AS2027, parameterless DocumentAccess calls the default StartTransaction overload, which passes bReadOnly=false; explicit DocumentAccess(doc, bReadOnly) forwards the boolean. Do not assume a helper called 'read scope' uses read-only native access, or that aborting a write-capable read context leaves the Undo stack untouched; the latter requires a separate native test.

The installed XML covers only a fraction of the public types (e.g. no `StraightBeam`/`Beam` entries), so an empty XML grep is not evidence of absence. For constructor/method signatures, list types and members with a small throwaway .NET 10 console tool using `System.Reflection.MetadataLoadContext` (PathAssemblyResolver over `ADVS\*.dll`, the AutoCAD root `*.dll` and the runtime directory) or `System.Reflection.Metadata`; it reads metadata only and never executes Autodesk code. Build it under Hermes scratch, give native `dotnet` `C:/...` paths (MSYS `/c/...` paths are resolved as `C:\c\...`), and set `ImplicitUsings` enable. The AS managed DLLs (`AS*Mgd.dll`, joint DLLs) live in `AutoCAD 2027\ADVS`, not the AutoCAD root; Windows PowerShell reflection cannot load these .NET 10 assemblies, so use the metadata tool. Build it once and invoke `bin/Release/net10.0/<tool>.exe` directly in loops — repeated `dotnet run` per DLL rebuilds each time and can exceed the terminal timeout. Use `ProfileName.Name` (not `ToString()`, which returns the type name) for the section string, e.g. `HEA nach DIN#@§@#HEA100`. Headless test launch that reaches NETLOAD: `acad.exe <dwg> /language en-US /product ADVS /p <<ADVS>> /b <script.scr>` (shortcut args come from the Start Menu .lnk; script sets FILEDIA 0, NETLOAD, commands, QUIT). Diagnose silent write failure before debugging geometry: if `WriteToDb()` returns an ObjectId with `IsNull()==true`, empty `Handle` and 0 model-space entities without an exception, check `DocumentManager.GetAllDocuments().Count` and `GetCurrentDocument()` — commands run from a `/b` script right after NETLOAD see 0 AS documents, so creation is silently dropped. Fix: arm an `Application.Idle` handler and run the create command only after AS is idle (~20 s) and `GetCurrentDocument()!=null`. Always treat a null `WriteToDb()` ObjectId as failure. Full recipe: `autocad-automation` `references/live-link-publication-boundary.md`. Observed AS2027 signatures: `StraightBeam(string profName, Point3d p1, Point3d p2, Vector3d z)` + `FilerObject.WriteToDb()`; `ProfilesManager.GetProfTypeAsDefault(string className)`; `DocumentAccess(Document, bool bReadOnly[, bool propagate])` with `Commit()`/`DiscardAllChanges()`.

Joint/connection-component research (Tekla `Component`/`Deconstruct Component` equivalents): AS2027 `ASObjectsMgd` exposes `ConstructionTypes.IJoint` (InputObjects, CreatedObjects, Load/Save, UpdateDrivenConstruction), `IRule` (JointId, CreateObjects, GetRulePages), `RuleParameterSet`, `RuleApplicability*`, and `UserDefinedConnection`(`CreateTemplate`)/`UserDefinedConnectionInstance`(`CreateFrom`, Drivens). IJoint/IRule are joint-authoring interfaces; a public "insert factory joint by name + input objects" call was not found in metadata, and Dynamo-for-AS has no joint nodes. The model-side joint objects to read are `PassiveConstructionObject` (Drivers, Drivens, Rule, ParameterSet, AutoUpdate, Update) and `UserAutoConstructionObject` (InputObjects, CreatedObjects, GetConnectionPages, PrimaryJointName, Begin/Updated/UpdateFailed events); filter `GetModelObjectIds` results by these types. Treat reading existing joints as the first probe and native-command insertion as the candidate write path; both are runtime-unverified. Tekla's practice to mirror: attribute names differ from dialog labels, so discover them by having the user place one factory joint manually in a disposable DWG and change 2 parameters to recognizable values (e.g. plate thickness 12, a bolt alignment option), then search the read-back parameter table for those marker values. Write the read probe as reflection over public parameterless getters only (no setters, Update or UpdateDrivenConstruction), skip the known AS-crashing getters (CompoundClassName/CompoundTypeName/NumberOfConnectedHoles), wrap each getter in try/catch, and append each step to a trace file so a native crash can be located to one member.

For AS2027, inspect these installed XML files first:

- `ASMgd.xml`
- `ASObjectsMgd.xml`
- `ASCADLinkMgd.xml`
- `ASGeometryMgd.xml`
- `ASModelerMgd.xml`
- `ASProfilesMgd.xml`

Use XML member names to confirm spelling and assembly ownership. Then verify runtime requirements with a minimal in-process C# command on a disposable copied DWG. Do not load Advance Steel managed assemblies into external Python and assume in-process APIs will behave correctly.

For native-body research, name the exact `BodyContext.eBodyContext` and keep geometry observations separate from analytic system-line assumptions. Compare actual face/vertex data and volume across supported contexts; `kExactDetailing` or `kMaxDetailed` is not, by its name alone, a certified smooth-surface or tessellation-error contract. A numerical diagnostic that reproduces successfully can be saved as a read-only recipe, but do not promote it into mutation approval or a curved-cut verifier before that result has been exercised. See the body-context evidence notes in `references/api-2027-local-reference.md`.

API research output should include:

```markdown
**Version:** AS2027
**Assembly/XML:** ASObjectsMgd.dll / ASObjectsMgd.xml
**Member:** Autodesk.AdvanceSteel.CADAccess.DatabaseManager.ExportToACIS(...)
**Documentation evidence:** present in installed XML
**Runtime evidence:** tested / not tested
**Mutation risk:** read-only / model write / derived-document write
**Next test:** smallest disposable verification
```

## Standards and Technical Books

Advance Steel documentation explains software behavior; it does not certify structural design or code compliance.

For CNS, AISC, EN, JIS, AWS, or project specifications:

- store only public metadata, short paraphrases, and citations unless the user supplies a licensed source;
- verify edition, amendment, material grade, thickness range, and project adoption before using a numeric requirement;
- treat the engineer's project specifications and approved contract documents as project authority;
- do not convert a paid standard or copyrighted book into a substitute full-text archive.

## Community and Forum Handling

Community sources are useful for symptoms, workarounds, UI paths, and version clues. They are not automatically current or complete.

For each community finding, record:

```yaml
claim: <short paraphrase>
source_url: <exact URL>
source_type: Autodesk Community | GRAITEC | AU | video | forum
product_version: <stated or unknown>
evidence_level: C | D
reproduced_on: <version or not tested>
production_status: blocked | test-only | verified
```

Never preserve usernames, email addresses, access tokens, or unrelated personal information in the skill.

## Output Format

```markdown
## 結論
<answer first>

## 證據等級
- A: <current official/local evidence>
- B/C: <older or community evidence>

## 版本適用性
- Confirmed: <versions>
- Unverified: <versions>

## 可執行下一步
1. <smallest safe check>
2. <verification result required>

## Sources
- <title> — <URL or exact local Autodesk XML path>
```

## Common Pitfalls

- Distinguish catalog `StandardName` (display) from `SectionName` (lookup key), and distinguish `ProfileMasterTable.TypeName`, `TypeNameText` and `TableName`. Preserve the source literal and query it with parameters; verify any candidate key separately in the current host. In AS2027, `ProfilesManager.GetProfileType(new ProfileName(...))` can return a non-null generic `ProfileType` with `Type=Dummy` for an invalid token, so non-null/InternalName/RunName is not section-validity evidence. Record native Type plus concrete wrapper type and reject Dummy where a valid profile is required. Use only SELECT on already-attached catalogs for a read-only audit; legacy helpers with FOR ATTACH fallback are not read-only. A discovered invalid fixture does not authorize changing its structural profile or prove an Undo/Redo root cause.

1. **把論壇答案當API契約。** Verify the member in same-version XML and reproduce it.
2. **把XML存在當runtime成功。** XML confirms documentation, not locking, transaction, document registration, or persistence behavior.
3. **混用版本。** Always label AS2022/AS2025/AS2027 evidence separately.
4. **把軟體文件當工程規範。** Software capability is not structural compliance.
5. **大量複製手冊或標準。** Store distilled rules, provenance, and links instead.
6. **覆蓋既有production skill。** Research findings remain here until reproduced and deliberately promoted.
7. **只看指令成功。** For drawings and numbering, verify native objects, save/reopen persistence, and output artifacts.

## Verification Checklist

- [ ] Exact Advance Steel version stated
- [ ] Every claim classified as documented, observed, or community
- [ ] Current official or same-version local evidence checked first
- [ ] Older and forum sources carry explicit version caveats
- [ ] Licensed-standard text was not copied without authorization
- [ ] No credentials or personal forum data stored
- [ ] Mutation requests routed to an operational skill and disposable work copy
- [ ] Final answer includes source paths/URLs and a smallest safe verification step
