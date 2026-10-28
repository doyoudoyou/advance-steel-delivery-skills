# AS2027 dimension point selection: DSM schema (read from factory AstorDetails.mdf)

Read-only: copy `C:\ProgramData\Autodesk\Advance Steel 2027\GBR\Steel\Data\AstorDetails.mdf` to scratch, attach to `(localdb)\MSSQLLocalDB` FOR ATTACH_REBUILD_LOG under a throwaway name, SELECT only, detach after.

Chain of tables:
`DetViewDimStrategyNew` (strategy, Items) -> `DetViewDimStrategyItems` (Order, Type, RequestLinear, GroupEqualDistances, BrokenRunningDimension, HideDimensionPoint) -> `DetViewDimRequestLinear` (Direction, ArrangeGlobally, ArrangeAbove, GroupRelatedDimensions, OneChainPerObjectInPoints1, AllowCombine, AutomaticallySeparate, Point1..Point15) -> `DetViewDimPointSelection` (one point rule).

Factory GBR counts: 93 strategies, 751 items, 486 linear requests, 492 point rules.

`DetViewDimPointSelection` columns = the classification axes of a dimension point:
- `Objects`: which model objects (by role/kind). Values seen with RunName prefixes: 14 Mp (main part), 4 AttPa, 15 AttPl, 19 AttBea, 11 Bo, 22 Ho, 44 Bo+Ho, 12 Mp beam-end processing, 18 Grid, 107 base plate role, 108 gusset role, 20506 fin plate role, 33 shear studs, 59 anchors, 1 column role, 134+ GA beams. Codes >100 are role-specific (model role).
- `PointType` (what point on the object): 0 All, 1 Extreme, 2 Contour, 3 features (holes/bolts/processing), 4 holes variant, 5 Mp points of attached parts, 8 single processing, 9 System line, 10 Centre, 11/12 bent beam inside/outside, 14 Colli(near), 15 template ref, 16 development, 19 BeamEndProc, 20 angle helper line, 24 camber. **+1000 = same type 'as reference'** (1001 Ref Extreme, 1009 Ref System, 1010 Ref Centre...).
- `PointGeometricRestrictions` (which of those points, view-relative position): 0 all, 1 Left, 2 Right, 4 Bottom, 5 BottomLeft, 6 BottomRight, 8 Top, 9 TopLeft, 10 TopRight, 11-16 combined/extreme variants (inferred from RunNames).
- `MpGeomRestriction`: same position codes but relative to the main part (e.g. 'Mp Left').
- `GeometricRestrictions` (object orientation filter vs view): 0 any, 1 orthogonal/linear, 2 diagonal, 3 TopView, 4 EndView, 5 SideEnd/system end, 13/14 diagonal/non-linear variants.
- `VisibilityStatus`: 0 any, 1 visible only, 2 (ref/system rules; meaning unconfirmed).
- `DepthPosition`: 0 any, 4 Rear, 7 Front.
- `ReferenceAxis`, `MPReferenceAxis`, `ParentRelativePositonRestriction`: almost always 0.

All value meanings above are inferred from factory RunNames (e.g. 'Mp - Contour, TopLeft' = Objects 14, PointType 2, PointGeomRestr 9); confirm in the DSM UI before writing rows.

Live DB read: server `(localdb)\AdvanceSteel2027`, Database = the full upper-case MDF path (`C:\PROGRAMDATA\AUTODESK\ADVANCE STEEL 2027\GBR\STEEL\DATA\ASTORDETAILS.MDF`); `Database=AstorDetails` fails login.

Roles: `DetObjQualifierSet` (= Objects code) -> `DetObjQualifierSetItem` (ObjQualifier, ModelRole). E.g. 1 Columns all = Column/Corner_Column/GableColumn; 10 EndPlate = Baseplate/Coverplate/Endplate; 64/76 'no EndPlates' exclude those; 107 Baseplate; 128/130 include Plate, Stiffener; 20506 Fin_Plate. Parts with Role '-' match none of the role-based rules.

Process -> style chain: DetailProcessDefinition.Step1 -> DetailProcessStep.StyleMap -> DetailStyleMapNew.Items -> DetailStyleMapItems (ObjQualifierSet -> DetailStyle) -> DetailStyle.Request1..10 -> DetViewRequest (Scale, ArrangeDir 0 main/1 top/2 bottom/3 left/4 right, inferred). A new style also needs DetailMasterTable and DetViewRequestCategories rows. No identity columns, FKs or triggers; keys are manual.

Model-side sidecar `<model>\Databases\revision_<sheet>.db` table `tObjDimPts(Handle, DimType, PtX/Y/Z)`: on Plum Tree T-1, DimType 10 = 1 pt per handle (fits Centre), 9 = 2 pts per beam (fits System line ends), 19 only on 1 handle (fits BeamEndProc), 14 = 40/handle. So DimType likely reuses the PointType code — inference, unverified.
