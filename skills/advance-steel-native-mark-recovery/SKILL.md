---
name: advance-steel-native-mark-recovery
description: Use when working on Advance Steel downgrade/upgrade workflows where restored marks must become native Advance Steel 2025 Single Part Mark and Assembly Number, not merely displayed text or User Attributes. Covers verification mindset, COM/plugin cautions, and acceptance criteria.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [advance-steel, autocad, marks, downgrade, as2025, steel-detailing]
    related_skills: [autocad-automation, advance-steel-agent]
---

# Advance Steel Native Mark Recovery

## Overview

Use this skill when the user is restoring Advance Steel marks after downgrade/upgrade, import/export, or data migration. The user's hard requirement is that restored values must become native Advance Steel 2025 properties:

- **Single Part Mark** / part mark
- **Assembly Number** / assembly mark

It is not sufficient to show the mark in labels, store it in User Attributes, attach XData only, or keep an external mapping file. Those can be intermediate aids, but final acceptance requires Advance Steel itself to recognize the marks as native numbering fields.

## When to Use

Use when the user mentions:

- Advance Steel 2025 mark recovery
- 降版/升版後 mark 不見、編號恢復、構件編號
- Single Part Mark, Assembly Number, part mark, assembly mark
- AS objects, BOM, numbering, drawings, labels
- User Attributes vs native marks

## Core Principle

Always distinguish three levels:

| Level | Meaning | Acceptable final result? |
|---|---|---:|
| Display-only | Text label, annotation, block attribute, exported table | No |
| Auxiliary storage | User Attributes, XData, external CSV/JSON mapping | No, intermediate only |
| Native Advance Steel mark | AS2025 numbering fields used by BOM/drawings/object properties | Yes |

## Recommended Workflow

1. **Inventory source marks**
   - Determine where old marks exist: drawings, BOM exports, labels, object handles, GUIDs, CSV, DWG attributes.
   - Preserve mapping keys: handle/object ID/GUID/profile/length/location/assembly relation.

2. **Identify target AS objects**
   - Match objects conservatively using stable IDs if available.
   - If IDs changed, use multi-factor matching: section, length, endpoints/grid, material, assembly relation, quantity.
   - Report ambiguous matches instead of writing uncertain marks.

3. **Write through a native-capable path**
   Possible paths depend on installed APIs and Advance Steel exposure:
   - Official Advance Steel .NET/C# API/plugin if available.
   - COM automation only if it exposes the actual mark/numbering properties.
   - Manual/import workflow if native API write access is blocked.

4. **Do not stop at User Attributes**
   User Attributes may be used to stage the old mark, but a second step must transfer into native AS fields.

5. **Renumbering caution**
   - Advance Steel numbering may overwrite manual marks if not configured/locked correctly.
   - After writing marks, run a verification pass after save/reopen and after any numbering update.

## Acceptance Criteria

Use `templates/native-mark-acceptance-checklist.md` as the reusable evidence checklist for an implemented recovery run.

A solution is only successful if all of these pass:

- [ ] Selecting the AS object in Advance Steel shows the restored value in the native part/assembly mark field.
- [ ] BOM / structured list reads the restored mark from native AS data.
- [ ] Drawing labels generated from AS tokens show the restored mark without custom text hacks.
- [ ] Save, close, reopen preserves the mark.
- [ ] A numbering/update operation does not unexpectedly destroy the restored values, or the required locking/configuration is documented.
- [ ] Ambiguous/unmatched objects are reported separately.

## Output Format for Recovery Plans

When proposing or implementing a recovery workflow, return:

```markdown
## 目標
## 可用來源資料
## 物件匹配方法
## 寫入 native mark 的方法
## 驗證步驟
## 風險/限制
## 需要使用者確認的 Advance Steel 畫面或 API 能力
```

## Common Pitfalls

1. **Calling User Attributes a fix.** The user explicitly does not accept this as final.
2. **Assuming COM exposes all AS properties.** Verify property availability before promising automation.
3. **Ignoring assemblies.** Single part and assembly marks are different data; do not conflate them.
4. **Letting AS renumber overwrite restored marks.** Always include post-renumber verification.
5. **Overwriting uncertain matches.** Ambiguity must be surfaced, not guessed.

## Verification Checklist

- [ ] Native AS field write path identified
- [ ] User Attributes treated only as staging if used
- [ ] Single part and assembly numbers handled separately
- [ ] Save/reopen/BOM/drawing-label verification included
- [ ] Ambiguous matches isolated for manual review
