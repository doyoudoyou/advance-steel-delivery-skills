# Experimental native folded-plate analytic-hole adapter

AS2027 pinned IFCPlugin FoldedPlateConverterCoordinationView.BuildRepresentation uses BodyContext enum value 1 (kDetailed), then PropertiesUtils.ConvertModelerToIfcBrep. That path bakes polygonal drill holes. The studied method has no tessellation-precision argument.

An isolated proof can rebuild only the in-memory folded product representation using native kNC bodies (unperforated for the verified simple-hole fixture), then call native FeatureConverter.BuildIfcFeatures with source GetFeatures(false), identity parent transform for the WCS-based folded product, false mirror flag, representation, null swept solid. Link the resulting openings with AddToIFCRelVoid. Require all features to be ConnectionHolePlate simple kHole entries and their arranger-count sum to equal NumberOfHoles; refuse other cuts or unresolved source semantics. Keep this behind an experimental compile flag and exact working-copy guard until broader validation.

Register EVERY newly converted BRep through EarlyBindingInstanceModel.Add(P21Instance). Merely appending new BReps to an already-registered product representation can serialize an empty item list because those new entities lack registered STEP IDs. This failure must be rejected before publication; do not bypass the color/geometry guard.

Validate analytic IfcCircleProfileDef, opening-host count, absence of baked inner loops on the host, effective closed geometry after boolean subtraction, source metadata/RGB, and axis/penetration alignment. Use explicit fine IfcOpenShell mesher settings when comparing analytic circle volumes; viewer tessellation is not the analytic IFC definition. Distinguish alignment to earlier exported body loops from independently measured native source coordinates.

The native feature converter may add a 0.001 mm radial clearance and extend cutter depth beyond thickness. Report it; do not call the resulting 14.002 mm diameter exactly 14 mm. A successful simple-hole sample does not certify slots, mirrored plates, partial holes, cuts or bend-intersecting holes. Standard V8 must remain unchanged until explicit integration and acceptance.
