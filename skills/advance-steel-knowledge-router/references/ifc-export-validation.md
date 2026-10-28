# IFC export validation

Require an independent IFC parser with EXPRESS/schema validation and geometry creation before accepting a custom STEP writer. Successful C# compilation and lexical substring tests do not validate IFC.

Check 22-character IFC GUIDs, real literals with decimal/exponent, complete IfcTriangulatedFaceSet arguments including optional PnIndex, non-null RelativePlacement, and exact spatial entity argument ordering. Roundtrip Unicode marks, RGB and dimensions, and compare computed volume using explicit units on clearly labeled synthetic fixtures.

Do not equate getBrepInfo contour vertices with proven tessellation of curved native surfaces or holes. Closed manifold validation only proves mesh topology, not correspondence to the native solid. Preserve a hard export block until a native geometry adapter is validated with real AS objects and volume/extents/feature evidence. Never silently substitute bounding boxes or drop holes.

Treat custom property-set names as plugin-owned, not Autodesk mappings. Do not claim IFC MVD compliance merely by placing a view name in the STEP header. Separate synthetic writer validation from real selected-native-model export acceptance.
