# Portage evidence and approach viewpoints

These are **map-derived candidates, not field-verified landing locations**. The original 2008 KML is a generalized historical route, not a surveyed track: several lake-crossing segments cut through shore or islands. Candidate insets must retain that qualification.

## Primary data

- USFS National Forest System Trails, [service](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0): the complete bounding-box query returned 104 features with no exceeded-transfer-limit flag. Request URL/parameters, retrieval time, layer metadata, service metadata and full unmodified response are preserved in `sources/portage-usfs-*.json`. `portages.geojson` contains the ten distinct USFS trail features relevant to mapped travel; original attributes are retained. No invented connecting trails are added.
- Minnesota DNR hydrography: `sources/hydrography.geojson`, acquired separately with its associated metadata, supplies named approach-lake shorelines.
- Independent USGS NHD [waterbody layer](https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/12): 121 features, complete raw response and request saved as `sources/portage-nhd-*.json`. This independently corroborates the large Hungry Jack endpoint/shore gap.
- User-provided `sources/2008-boundary-waters.kml`: ordered coordinates establish travel direction. Route dates/day labels have not been reinterpreted.

## Ordered approach candidates

| ID | Historical line | Approach | Evidence |
|---|---|---|---|
| P01 | Day 1 | Hungry Jack → Moss | Low confidence: USFS endpoint 383 m from shoreline |
| P02 | Day 1 | Moss → Duncan | USFS endpoint, DNR shoreline; 75 m view |
| P03 | Day 1 | Duncan → Rose | USFS endpoint, DNR shoreline |
| P04 | Day 2 | Rose → Rove | USFS endpoint, DNR shoreline |
| P05 | Day 2 | Watap → Mountain | USFS endpoint, DNR shoreline |
| P06 | Day 3 | Mountain → Clearwater | USFS endpoint, DNR shoreline |
| P07 | Day 3 | Clearwater → West Pike | USFS endpoint, DNR shoreline |
| P08 | Day 3 | West Pike → East Pike | USFS endpoint, DNR shoreline |
| P09 | Fourth Day | East Pike → Pine via West Pike junction | USFS endpoint and connected trails; direction from KML |
| P10 | Fourth Day | Pine → Little Caribou | Low confidence: historical line/shoreline only; trail unresolved |
| P11 | Fourth Day | Little Caribou → Caribou | Low confidence: historical line/shoreline only; trail unresolved |
| P12 | Fourth Day | Caribou → Clearwater | USFS endpoint, DNR shoreline |

Day 1 goes through Moss, not West Bearskin. Rove–Watap is a connected-water transition and receives no invented portage. Last Day is a Clearwater paddle to the exit, with no mapped portage. P09 follows the incoming East Pike shoreline: USFS East Pike–West Pike and West Pike–Pine trails meet near West Pike shore, while the historical line turns south there. A separate West Pike water approach is not depicted for that return traversal.

P01 deserves additional checking before navigation use: the USFS Hungry Jack–Moss line ends roughly 383 m inland from the DNR Hungry Jack shoreline (NHD independently gives about 387 m). The candidate is the nearest named-lake shoreline point, not a claim that the actual carry begins there. P10/P11 preserve route/shoreline crossings only; the complete queried USFS trail dataset did not provide these carries. Do not display those as verified trailheads or add synthetic authoritative trails.

## Derivation and checks

`sources/portage-derive.py` reproduces the derived files with Python and Shapely. It uses a local longitude/latitude metric approximation (74,400 m/longitude degree, 111,200 m/latitude degree), appropriate for viewpoint and offset estimates, not survey measurements. For trail-backed candidates, the incoming trail endpoint is snapped to the nearest boundary of the named approach lake; raw endpoint coordinates and snap distance remain in each feature. Normal offsets are approximately 3–18 m.

Viewpoints prefer a point along the incoming KML about 400 m before the landing, provided it lies in the named lake and the entire straight sightline lies in water within a 2 m shoreline tolerance. When that fails, a fan search chooses a water point near the incoming direction. P02 is shortened to 75 m because a longer unobstructed water sightline was not found. All 12 resulting viewpoints pass point-in-lake and buffered water-sightline checks. These checks establish mapped water coverage only, not actual visibility through vegetation or terrain.

Fields include `confidence`, `field_verified=false`, `evidence_method`, raw endpoint, snap distance, `view_lon`, `view_lat`, `view_distance_m`, `view_bearing_deg` (clockwise from north, toward the candidate), `view_method`, and explicit water checks. All coordinates are WGS84 longitude/latitude. Baseline confidence is medium, never high, because no landing has been field verified.
