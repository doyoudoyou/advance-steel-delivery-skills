# Advance Steel Source Index

**Curated:** 2026-08-06  
**Scope:** public Autodesk documentation, same-version local Autodesk XML docs, official standards metadata, and selected community troubleshooting sources.

This file is a provenance index, not a copy of the source material. Re-fetch public pages when current behavior matters.

## Evidence Labels

- **A-current:** current official page or same-version locally installed Autodesk documentation.
- **A-versioned:** official Autodesk/standards source for a stated older version or edition.
- **C-community:** practitioner or support guidance that requires reproduction.
- **D-discovery:** useful lead only.

## Autodesk Current Documentation

### Advance Steel 2027 Help

- URL: https://help.autodesk.com/view/ADSTPR/2027/ENU
- Evidence: A-current
- Version: Advance Steel 2027
- Use for: current navigation, What's New, modeling, numbering, drawings, collaboration, Dynamo, FAQ, Developers, and installation.
- License note shown by Autodesk: except where otherwise noted, the Help content is licensed under CC BY-NC-SA 3.0.
- Stored here: only distilled routing rules and links, not copied chapters.

### FAQ: Customize a BOM on Drawing Template

- URL: https://help.autodesk.com/view/ADSTPR/2027/ENU?guid=GUID-AE98D7EA-0C09-49AF-ACFE-6A36E3E7FB20
- Evidence: A-current
- Version: Advance Steel 2027
- High-signal fact: an Advance Steel BOM template uses `ASTXBOMTEMPLATETEXT` objects grouped with AutoCAD group names; exploding the template removes its Advance Steel BOM-template behavior.
- Production implication: do not treat exploded lines/text as a native BOM template.

### Advance Steel Implementation Guide

- URL: https://help.autodesk.com/sfdcarticles/attachments/Advance_Steel_Implementation_guide.pdf
- Evidence: A-versioned
- Use for: implementation planning, deployment concepts, environment/setup vocabulary.
- Gate: confirm every UI path and database location against the target Advance Steel release.

### Advance Steel API Guide 2022

- URL: https://help.autodesk.com/view/ADSTPR/2022/ENU?guid=GUID-AF2072A9-3F8F-4DAC-B595-470A9E32BEE0
- Evidence: A-versioned
- Version: Advance Steel 2022
- Use for: conceptual API orientation only.
- Gate: do not claim a member exists in AS2025 or AS2027 until the matching local XML or same-version documentation confirms it.

## Same-Version Local Autodesk Documentation

Root:

```text
C:\Program Files\Autodesk\AutoCAD 2027\ADVS
```

Authoritative local files for installed AS2027 managed API member names:

- `ASMgd.xml`
- `ASObjectsMgd.xml`
- `ASCADLinkMgd.xml`
- `ASGeometryMgd.xml`
- `ASModelerMgd.xml`
- `ASProfilesMgd.xml`

Evidence: A-current for **member presence and documentation text** in this installation. XML presence alone does not prove runtime safety, transaction requirements, or production suitability. See `api-2027-local-reference.md`.

## Autodesk Community

### API Options for Numbering and Detail Drawing

- URL: https://forums.autodesk.com/t5/advance-steel-forum/advance-steel-api-options-for-numbering-and-detail-drawing/td-p/8216125
- Evidence: C-community
- Date/version context: 2018 discussion; product version must be inferred carefully.
- Use for: historical API limitation clues and terminology.
- Gate: never let this older thread override reproduced AS2027 in-process behavior.

### .NET API: Properties of Advance Steel Objects

- URL: https://forums.autodesk.com/t5/advance-steel-forum/net-api-how-to-get-properties-of-as-objects/td-p/8264717
- Evidence: C-community
- Date/version context: 2018 discussion.
- Use for: discovery of object/property access patterns.
- Gate: confirm namespaces, type names, ownership, open mode, and disposal against installed XML and a disposable runtime test.

### Out-of-Date Numbering

- URL: https://forums.autodesk.com/t5/advance-steel-forum/out-of-date-numbering/td-p/10234648
- Evidence: C-community
- Date/version context: 2021 discussion.
- Use for: symptom discovery and troubleshooting hypotheses.
- Gate: numbering conclusions require current model-state, equal-parts, prefix, and save/reopen evidence.

Do not store forum usernames, email addresses, signatures, or unrelated personal information.

## Specialist Technical Support

### GRAITEC: Numbering Options

- URL: https://graitec.com/uk/resources/technical-support/documentation/technical-faqs/faq-2086-what-are-the-different-numbering-options
- Evidence: C-community/support
- Use for: UI vocabulary and practitioner explanation of numbering options.
- Gate: verify in the target version and office setup.

### GRAITEC: Prototype Customization

- URL: https://graitec.com/uk/resources/technical-support/documentation/technical-faqs/faq-2489-how-can-a-prototype-be-customized-and-how
- Evidence: C-community/support
- Use for: prototype customization leads.
- Gate: validate on a copied prototype and generated sample drawing; do not edit production prototypes blindly.

## Standards Metadata

### CNS Online Service

- URL: https://www.cnsonline.com.tw?locale=zh_TW
- Evidence: A-current for public catalog metadata and edition/status lookup.
- Owner/operator: Taiwan BSMI/CNS service.
- Gate: obtain the licensed standard text or project-issued specification before using detailed clauses or values.

### BSMI Article on CNS 13812 SN Grades

- URL: https://www.bsmi.gov.tw/wSite/public/Data/f1622624920864.pdf
- Evidence: A-versioned
- The public BSMI article cites `CNS 13812:2014 建築結構用軋鋼料` and discusses SN400/SN490 grade marking, including SN490B.
- Gate: this does not prove the current CNS edition or every current numeric requirement. Re-check CNS Online and project documents.

## Adjacent Existing Skills

- `advance-steel-agent` — production architecture, model/drawing mutation and verification.
- `autocad-automation` — COM, File IPC, .NET and scripting execution patterns.
- `eircad-advance-steel` — practical video-derived workflow, evidence level D unless exact transcript is fetched.
- `steel-drawing-analysis-workflow` — visual and native drawing QA.

## Refresh Procedure

1. Re-fetch the exact URL.
2. Record access date and visible product version.
3. Compare the claim against installed same-version XML or a disposable test where applicable.
4. Mark dead or redirected URLs; do not silently substitute a search snippet.
5. Update this index only after the replacement source is verified.
