# Native IFC volume and hole fidelity

Do not treat AtomicElement.Volume or summed kNC ModelerBody.Volume as net finished-part volume without checking body context. Read-only AS2027 measurements show kNC/normal can omit drill subtraction and beam notches; kExactDetailing may include beam notches but still omit plate holes. kDetailed/kMaxDetailed can include holes with different polygonal approximations. Record context and compare equivalent finished geometry rather than selecting the context nearest the IFC result.

Compare source hole Diameter, Depth, arranger count and placement against IFC geometry. Gross volume minus count*pi*r^2*depth is only a conditional reference until full-depth, non-overlap and placement/intersection are verified. Keep that assumption visible in evidence.

Do not count IfcOpeningElement as drilled-hole count. Beam notches may be openings, while folded-plate drilled holes may be baked into FacetedBrep inner loops. Classify host/profile and inspect baked boundaries as well.

Check both nominal circumdiameter and minimum polygon aperture. Observed folded-plate nominal 14 mm circles became eight-sided loops with circumradius 7.001 mm and minimum aperture about 12.936 mm. A plausible bounding circle, legal schema and preserved IFC-to-IFC fingerprint do not establish circular-hole fidelity. Plain plate holes may remain analytic IfcCircleProfileDef with exporter epsilon added to radius.

For mesh volume checks, require closed consistently oriented topology, use SI geometry output explicitly, translate coordinates near the origin to reduce cancellation, and match source ASId to exact IFC GlobalId. Preserve raw failed comparisons; do not widen tolerance after seeing results. A provisional development threshold is not engineering approval.
