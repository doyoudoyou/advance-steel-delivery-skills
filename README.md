# Advance Steel Delivery Skills

Agent skills for Autodesk Advance Steel / AutoCAD shop-drawing work: frame replacement, native plotting, drawing-number organisation and complete delivery packaging, plus related dimensioning, mark recovery and API research guidance.

They were written for [Hermes Agent](https://hermes-agent.nousresearch.com/docs), but each skill is a plain `SKILL.md` (YAML front matter + Markdown) with optional `references/` and `templates/`. Other agent frameworks that read the same format can use them too.

Most of the content is in Traditional Chinese (Taiwan). Some references are in English.

## Skills

| Skill | Purpose |
|---|---|
| `advance-steel-frame-and-delivery` | Replace drawing frames, set drawing numbers and file names, run native PDF output, classify parts as ModelSpace 1:1 DWGs, and package and verify the full delivery (fixed project folder layout, hash checks, ZIP read-back, cleanup rules). |
| `advance-steel-agent` | Architecture and guardrails for controlled Advance Steel agents (execution layer, pitfalls and runbook, specialist drawing agents). |
| `advance-steel-dimension-strategy` | Designing automatic dimensions: DSM/drawing styles, point selection, chain patterns, post-generation native dimensions. |
| `advance-steel-knowledge-router` | Where to look in AS manuals, the 2027 .NET API and standards, and how to judge the evidence. |
| `advance-steel-native-mark-recovery` | Restoring native Single Part Mark / Assembly Number after downgrade or upgrade. |
| `box-column-shop-drawing-annotation` | Annotation principles and native workflow for BOX column shop drawings. |
| `step-model-portfolio-rendering` | Rendering STEP models for a website portfolio. |

## Install (Hermes)

Copy the skill folders into your skills directory, for example:

```bash
git clone https://github.com/doyoudoyou/advance-steel-delivery-skills
cp -r advance-steel-delivery-skills/skills/* ~/.hermes/skills/autocad-automation/
```

On Windows the default location is `%LOCALAPPDATA%\hermes\skills\autocad-automation\`.

## Notes and limitations

- **Anonymised.** Project names, client names, machine names and local paths were replaced with placeholders (`範例案A`–`E`, `範例案T`, `case-T`, `<USER_HOME>`, `<WORKSPACE>`, `<owner>`). Referenced scripts and tools (e.g. `AdvanceSteelTools`, `as-agent`, project `05_交付紀錄/scripts`) are **not** included in this repository. Treat them as descriptions of a working setup, not something you can run directly.
- Written for Advance Steel 2025–2027 on Windows. Version-specific facts are marked where known.
- The skills tell an agent to work on copies, verify with native reopen and plotting, and never overwrite source files or delete without approval. Read them before you let an agent change production drawings.
- Not affiliated with or endorsed by Autodesk. Advance Steel and AutoCAD are trademarks of Autodesk, Inc.

## License

[MIT](LICENSE)
