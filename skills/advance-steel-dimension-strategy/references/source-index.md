# Dimension Strategy Source Index

**Curated:** 2026-08-06  
**Scope:** Advance Steel automatic/manual dimension strategy, DSM hierarchy, dimension points, update behavior, dimension styles, and practical troubleshooting.

This is a source map and distilled evidence record. It does not archive complete articles or video transcripts.

## Evidence Labels

- **A-current:** current Autodesk Help or Support matching AS2025/AS2026.
- **A-versioned:** official Autodesk material for an older stated release.
- **B-legacy:** older GRAITEC product guide describing the stable DSM hierarchy; verify controls in the current release.
- **C-practitioner:** Autodesk Community, EIRCAD, or current GRAITEC practice; reproduce before production.

## A-current Autodesk Sources

### Setting up Automatic Dimensions

- URL: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-up-Automatic-Dimensions-in-Advance-Steel-drawings.html
- Updated: 2025-08-05
- Key evidence: Autodesk directs users to two official DSM automatic-dimension webinars and the Dimension Request Help topic. It recommends learning model objects and object presentation/labeling rules before dimension customization.

### Dimension Request

- URL: https://help.autodesk.com/cloudhelp/2026/ENU/AdvSteel-Drawings/files/GUID-09FC505F-B067-4EE9-9DA2-A881DDF08699.htm
- Version: 2026
- Key evidence: one dimension request defines the dimensioned objects in a chain; definitions can be shared; modifying one affects all drawing styles that use it.

### Customized Dimension Styles

- URL: https://help.autodesk.com/view/ADSTPR/2025/ENU?guid=GUID-57D845BE-3C2E-44E2-AC03-3BDBB5E78489
- Version: 2025
- Key evidence: prototype stores named dimension styles; Management Tools defaults link Advance Steel dimension types to prototype styles; detailing uses those prototype styles. Linear, arc, radial, angle and slope dimensions have separate defaults.

### Manual Dimensions

- URL: https://help.autodesk.com/cloudhelp/2025/ENU/AdvSteel-Drawings/files/GUID-D462912E-5259-476F-9EC8-B27A361B7A0E.htm
- Version: 2025
- Key evidence: use Advance Steel parametric dimensions rather than AutoCAD linear dimensions. AS dimensions follow scale, detail movement, clipping and model updates. Preferred/smart points are linked to model geometry.

### Hole Pattern Point Behavior

- URL: https://help.autodesk.com/cloudhelp/2025/ENU/AdvSteel-Drawings/files/GUID-8F9D78A0-083C-4CE9-9136-4B01E3ABB5A8.htm
- Version: 2025
- Supported updateable selections: all holes; first; last; first and last; supported endpoints with a reference point.
- Unsupported: arbitrary subsets of intermediate holes. Update can remove those points or leave a stale invalid point, depending on defaults.

### Dimension Chain Representation

- URL: https://help.autodesk.com/cloudhelp/2025/ENU/AdvSteel-Drawings/files/GUID-9A4AFCEA-0425-461B-8E65-8505AA4C7A39.htm
- Version: 2025
- Key settings: presentation, group equal distances, broken dimension line, and hide first/last/none.

### Dimension Arrangement

- URL: https://help.autodesk.com/cloudhelp/2023/ESP/AdvSteel-Drawings/files/GUID-97C690AD-E9F3-4294-AD4A-6EE10F0FC01E.htm
- Version: 2023, official/versioned
- Key evidence: G/L controls global versus local overlap avoidance; T/B controls side; A/S controls combined versus one chain per detected item; automatic separation can split features and attached objects.

### Attached Parts

- URL: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Advance-Steel-How-to-customize-an-assembly-drawing-style-to-dimension-the-attached-parts.html
- Updated: 2026-03-30
- Key evidence from Autodesk indexing: add a new chain under the view, choose the type and a definition matching the case; attached-part definitions are identified by `AttPa` in the description.

### Excluding Drilled Holes

- URL: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-configure-the-dimension-style-to-avoid-dimensioning-the-holes-drilled-in-steel-parts-in-Advance-Steel.html
- Updated: 2025-09-05
- Key evidence: remove the dimension requests responsible for holes from the detail-style configuration. This supports minimal-chain design rather than broad point suppression.

## Official Training

### Customizing Automatic Dimensions, Part 2

- URL: https://www.youtube.com/watch?v=ta-d8OQfCmg
- Publisher: Autodesk Building Solutions
- Published: 2017-07-12
- Evidence: A-versioned
- Video description states that the workflow starts from the desired result and builds a view dimension request through arrangement, point filtering and point requests.
- Transcript status on 2026-08-06: disabled. Do not quote content beyond public metadata/description.

## B-legacy Structural Reference

### Advance Steel Drawing Style Manager Guide 8.1

- URL: https://download.graitec.com/public/Common/Downloads/Documentation/AS-DSM_guide-8.1-EN.pdf
- Relevant pages: 34–41 and 61–76
- Stable concepts extracted:
  - a strategy combines chains;
  - a request defines direction, point selection and position;
  - reference points are conditional anchors;
  - features and contour points differ;
  - G/L, T/B and A/S define arrangement;
  - point rules filter model object, geometry type, position and visibility;
  - copied/shared sub-styles create blast-radius risk; deep copy isolates them.
- Gate: terminology and hierarchy are useful; confirm current UI and country-build definitions in AS2025/AS2027.

## C-practitioner Sources

### EIRCAD: Edit Dimension Strategy

- URL: https://www.youtube.com/watch?v=YFi4d1cqpFY
- Published: 2021-01-05
- Use for: tracing a visible section-view dimension back to the responsible chain/request and copying a definition before editing.
- Gate: reproduce on the target version; this is practical training, not Autodesk documentation.

### GRAITEC Guide to Advance Steel Dimensions

- URL: https://graitec.com/uk/blog/a-guide-to-advance-steel-dimensions
- Published: 2018-04-06
- Use for: manual parametric angle, arc and radial pick sequences; curved CHS may appear faceted and require the 3-point workflow.

### GRAITEC Recommended Practices

- URL: https://graitec.com/uk/resources/technical-support/documentation/advance-steel-technical-articles/recommended-practices-autodesk-advance-steel
- Use for: modeling direction, system-line placement, model roles and planning drawing output.
- Important hypothesis: system-line position influences assembly dimensioning. Treat this as a modeling/datum warning, then verify project conventions.

### Autodesk Community: Setting Up Automatic Dimensions

- URL: https://forums.autodesk.com/t5/advance-steel-forum/setting-up-automatic-dimensions/td-p/8331763
- Use for: observed cleanup burden, system-line dimensions, update instability, and a diagnostic tactic of temporarily labeling each chain to identify which rule created it.
- Evidence: C-practitioner only.

### Autodesk Community: Invalid/Red Manual Points

- URL: https://forums.autodesk.com/t5/advance-steel-forum/dimension-line-parametric-dimensions-red-circle/td-p/8416817
- Use for: red/non-preferred point means update risk; defaults can retain or erase invalid points, but retention does not make them smart.

### Autodesk Community: Plan View Dimensioning

- URL: https://forums.autodesk.com/t5/advance-steel-forum/dimensioning-a-steel-plan-view/td-p/10720513
- Use for: GA dimensions to grids/beams can be automated through view dimension systems, with AS parametric tools as fallback.

### Autodesk Community: Drawing/Layout API Limits

- URL: https://forums.autodesk.com/t5/advance-steel-forum/advance-steel-api-access-layout-elements/td-p/12547358
- Use for: limitation clue. Community replies state detail/layout API access is limited and DSM is the intended control surface.
- Gate: do not state this as a complete current API contract; verify AS2025/AS2027 behavior before concluding no automation path exists.

## Source Conflict Rules

1. Current Autodesk Help/Support wins for documented AS2025/AS2026 behavior.
2. The legacy DSM guide explains hierarchy but cannot establish current control names by itself.
3. Community evidence can identify a failure signature but cannot define acceptance.
4. User-verified native drawing evidence overrides generic examples for the user's production workflow.
