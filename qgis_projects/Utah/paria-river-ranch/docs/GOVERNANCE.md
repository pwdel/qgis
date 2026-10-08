# Equestrian evidence profile 1.0

This is a project-specific profile, not an OGC water-safety standard. Geometry uses [GeoJSON RFC 7946](https://www.rfc-editor.org/rfc/rfc7946.html), longitude then latitude in WGS84. Its `properties` object can carry our domain attributes. QGIS stores presentation layers in a GeoPackage. The [OGC GeoPackage metadata extension](https://www.geopackage.org/spec140/#extension_metadata) can attach standards-based metadata documents; it does not itself certify water, access, or safety. This release uses explicit source IDs and a portable JSON evidence register, and makes no ISO metadata conformance claim.

## Pattern retained from Elm/outdoor-rules

Separate place, location reference, parking, entry, access route, activity authorization, stay conditions, governing authority, source medium and evidence. Separate observations from derived interpretations. A map line is not a right of passage. Source acquisition, publication, retrieval and processing dates are distinct. Unknown dates stay null; no confidence score is invented. A new download does not make an old observation current. The public profile adds horse travel and horse-trailer planning; private location records are not copied.

## Types and criticality

`feature_type`: Ranch, Trailhead, Campground, WaterFacility, CanyonReference, Landmark, RoadReference.

`water_status`: AdvertisedPotable, SeasonalStockOnly, SurfaceWaterUnverified, NoSupplyDocumented, Unknown. These describe evidence, not availability today. A potable-water statement does not establish permission for bulk tank filling, hose connections, flow, or a trailer turnaround.

`trailer_status`: Unknown, HistoricalStagingLead, FacilityAdvertisesRigs, HighClearanceSourceFlag. None means vehicle-specific approval. Supporting attributes retain total rig length, width, height, ground clearance, loaded mass, measured entrance width, curve radius, turnaround dimensions, grade percent, surface, bridge/weight restrictions, source and observation date. Missing measurements are null, not zero. Road classes preserve the source's CARTOCODE; code 16 is an explicit high-clearance/4WD warning, not a towing recommendation.

`horse_status`: PublishedYes, PublishedRestricted, Unknown, Conflicting. State `HorseAllowed=Yes` is published mapping, not a current manager confirmation. Blank USFS fields are unknown. A hiker-only category is shown as a conflict/limit rather than silently overridden by a commercial ranch's route list. No route is recommended simply because it is drawn.

`verification_status`: PublisherStatement, HistoricalReport, DerivedModel, Unknown, Conflict. No record in this release is field-verified.

`criticality`: Critical or Context. Water supply/access, trailer turning/clearance, steepness, cliff exposure, flooding and permissions that determine access are Critical. Critical claims must reference a source ID, identify the exact supported assertion, give date precision, spatial scope and limitations, and have a recheck instruction. Unsourced unknowns may be recorded only as unknowns, with an explicit missing-evidence reason.

## Evidence record

Every record in `sources/evidence.json` has an ID, title, publisher, URL, source medium, authority type, retrieval date, publication/observation dates (nullable), retrieval status, supported claim and limitations. GeoJSON features reference those IDs and separate coordinate evidence from operational evidence. `sources/manifest.json` records downloaded-file SHA-256 values; service request files preserve query parameters and counts. Failed original-document retrieval is disclosed; a search-index excerpt is not represented as an archived source PDF.

## Promotion and expiry

1. Import geometry as context; preserve publisher IDs and source attributes.
2. Extract a scoped claim. Do not promote the publisher's general statement into a current inspection.
3. Require direct manager/owner confirmation for a positive trip-critical supply or trailer-fit decision; record who, role, date, exact rig and location. An agent may not invent or make that confirmation.
4. Recheck water, snow/mud, closures and road conditions immediately before the trip and at departure. A report is historical as soon as conditions may have changed. This profile does not claim a universal number of days for validity.
5. Conflicts remain visible. Historic Tom Best order 0407-21-19 ended May 15, 2026 by its terms; its existence neither proves a current closure nor proves unrestricted camping.
6. Keep superseded evidence with its original dates. Resolve only with an identified replacement, reviewer and scope. A seasonal hydrant and a no-water trail description refer to different facilities and must not be flattened into one status.

## Terrain rules

Model slopes in degrees using horizontal and vertical metres; if reporting grade, `grade_percent = 100 * tan(slope_degrees)`. A 30-degree slope is about 58 percent, not 30 percent. Map classes 15/30/45 degrees are visualization bins, not safe riding thresholds. Cell slope describes terrain around a route; it is not measured trail tread grade or road longitudinal grade. Narrow benches, vertical faces, overhangs, erosion, unstable footing and exact cliff edges may be absent or smoothed. Do not produce an `Avoid` polygon without feature-specific evidence and review.

All service DEM output sizes are explicitly distinguished from native resolution. Native one-meter crop provenance retains its project identifier; do not assume the year in its product name is its flight date. Site-area lidar coverage is a discovery result, not evidence that every displayed pixel is from that survey.

## Release checks

Reject dangling evidence IDs, invalid geometry, missing source files, incomplete feature downloads, invalid raster CRS, nonfinite map extents and broken relative paths. Require four searchable, rendered, visually inspected PDF sheets, exact page/trim dimensions and a relocated QGIS reopen. First-pass PDFs have not been tested in Avenza and are not advertised as Avenza-ready.


## Expanded edition / profile 1.1

The expanded edition adds T01/S01-S03 and C01-C14 registries and separate QGIS/PDF outputs. Terrain, snow and access claims remain Critical; context cannot be promoted to verified safety or permission. Original source snapshots and the original four-sheet PDF are preserved.

- Terrain units: percent grade, with illustrated equivalent angles. Color breaks 30/45/60/90/150% are display classes, not horse-safety thresholds. The 150m corridor uses every mapped state-trail line, including paths with unknown or conflicting horse use. The review marker algorithm samples trail raster cells, requires a complete valid 100m neighborhood, excludes a 1000m map-edge margin, and selects three large nearby-lower-ground values at least1500m apart. Values are rounded to5m. This is a selected screening sample, not an exhaustive cliff inventory. Absolute cliff-face height, edge clearance and trail-tread grade remain unmeasured.
- Snow variables stay separate: new snowfall in inches; NOAA historical station depth>=1inch probability; satellite p50 ensemble percent. The latter is exploratory because ESA processing is partly unreproduced and local accuracy/counts are not supplied. It cannot be described as calibrated daily or trip probability. Low or zero median does not imply no snow/ice. Small summer patches may be artifacts. ENSO phases receive no invented numeric multiplier.
- Camping ownership categories must all appear in legends. Posted-source and posted-corral orders cannot be generalized to all mapped water or corrals. Expired rules remain historical even when still linked by an agency. A known water source does not establish legal camping nearby.
- Expansion validation requires13 combined sheets and13 individual PDFs, searchable text, print boxes, citation links, original-artifact hash preservation, valid relocated QGIS layers and visual inspection of every page. This release is not Avenza-georeferenced or field-tested.
