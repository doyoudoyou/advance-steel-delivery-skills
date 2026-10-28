# Standards, Specifications, and Copyright Boundaries

## Core Separation

Keep these authorities separate:

1. **Advance Steel documentation** — explains software commands, data, drawing generation, and APIs.
2. **Engineering standard/code** — defines material, design, fabrication, welding, inspection, or acceptance requirements.
3. **Project specification and approved drawings** — adopt editions and impose project-specific requirements.
4. **Shop/office standard** — controls detailing conventions and production workflow where the contract permits.

No Advance Steel setting proves engineering compliance.

## CNS and SN490B

Public official evidence located on 2026-08-06:

- CNS Online Service: https://www.cnsonline.com.tw?locale=zh_TW
- BSMI public article: https://www.bsmi.gov.tw/wSite/public/Data/f1622624920864.pdf

The BSMI article cites `CNS 13812:2014 建築結構用軋鋼料` and discusses SN400/SN490 grades, including SN490B. This is useful evidence that SN490B is associated with CNS 13812 in that cited edition.

It is **not** authority to:

- assume 2014 is the current edition;
- reuse every numeric table as a current requirement;
- infer a project's adopted edition;
- replace mill certificates, approved material submittals, or the engineer's specifications.

For the user's case-T S1-04 work, `CNS SN490B` is a known project material designation. Any mechanical property, chemistry, toughness, thickness limit, inspection, or substitution decision must still be checked against the project-issued specification and licensed/current CNS text.

## Standard Intake Record

Before turning a standard or technical book into reusable knowledge, record:

```yaml
source_title: <exact title>
issuer_or_author: <organization/person>
edition_or_date: <exact edition>
access_basis: public | user-supplied licensed copy | metadata only
project_adoption: <document and clause, or unknown>
permitted_use: metadata | short paraphrase | internal summary
excluded_content: <copyrighted tables/figures/chapters not stored>
reviewer: <engineer/detailing authority if required>
```

If `edition_or_date`, `access_basis`, or `project_adoption` is unknown, do not turn numeric requirements into a production rule.

## Copyright-Safe Distillation

Allowed by default:

- public title, issuer, edition/status metadata;
- short paraphrases of necessary concepts;
- formulas or requirements only when their use is authorized and properly cited;
- a source map telling the agent where to verify;
- user-authored project rules and acceptance checks.

Blocked by default:

- copying a paid CNS/AISC/EN/AWS/JIS standard into a skill;
- reproducing substantial chapters, figures, tables, or answer keys from a technical book;
- building a full-text substitute from OCR;
- stripping watermarks, access controls, or licensing notices;
- distributing a user-supplied licensed document outside the approved local scope.

## Engineering Safety Gate

A standards-derived answer must state:

- the exact standard and edition;
- whether the project adopts it;
- the applicable material/product/thickness/configuration;
- whether the answer is documentation, detailing guidance, or engineering design;
- what requires engineer approval or certified test evidence.

Never infer connection capacity, weld adequacy, member strength, or code compliance from Advance Steel geometry alone.

## Skill Promotion Rule

Promote only one of these into an operational skill:

- a project rule explicitly supplied/approved by the user;
- a stable software workflow reproduced on a disposable model;
- a standards requirement with confirmed edition, authorized source access, and clear project adoption.

Keep unresolved or metadata-only findings in this research skill.

## Fastener Catalog Research

- Check each CNS/JIS product standard on the issuer's current listing; a historical government specification or supplier cross-reference does not establish current status. Keep publication/revision dates separate from confirmation dates.
- Distinguish product accuracy grades A/B from mechanical strength grades, Japanese JSS torshear standards from JIS high-strength hex standards, and a supplier's available lengths from the complete standard range. Preserve full-thread markings when extracting catalog text; plain DOM text can lose color-coded meaning.
- Inspect bolt components and length-calculation relations by actual database schema, not table names alone. Washer records can reside in `SetNutsBolts`; automatic grip-length rules can reside in `ScrewNew`. Do not use a JIS text match in section-profile relations as evidence that JIS bolt sets exist.
- For read-only SQL LocalDB inventory, resolve catalog names through `sys.databases` joined by `database_id`; `sys.master_files.name` is a logical file name, not the name to pass to `ChangeDatabase`. Avoid assigning PowerShell `$Matches`, which `-match` automatically overwrites. Preserve exact-target SELECT output and distinguish inventory verification from native CAD acceptance.

## Verification Checklist

- [ ] Issuer, edition/date, and source URL/path recorded
- [ ] Access basis is explicit
- [ ] Current status checked on the issuer's service
- [ ] Project adoption confirmed or labeled unknown
- [ ] No substantial copyrighted text stored
- [ ] Numeric requirements trace to an authorized source
- [ ] Engineering decisions routed for qualified approval
