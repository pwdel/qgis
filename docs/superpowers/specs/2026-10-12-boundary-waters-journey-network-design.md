# Boundary Waters journey network

Design approved in conversation on 12 October 2026. Written specification for review before implementation.

## Purpose and scope

Create a black-and-white, eighteenth-century-inspired schematic for teaching route choice, elapsed-time estimation, landmark recognition and travel uncertainty. The supplied 1817 image guides the chains of small hatched lakes, italic lettering and engraved hills. This is a modern hypothetical teaching chart, not a reproduction or a claim about historical travel records.

Expand the existing nine-lake Clearwater experiment into the surrounding eastern Boundary Waters. Aim for 15–20 connected lakes, extending toward the Mountain and Rose lake country as published connections permit. Include only source-supported connections; a smaller verified network takes precedence over an invented connection. Preserve the two existing Clearwater circuits and add connected branches or another circuit where supported. Distinguish portages from river transitions.

Save the new work under `qgis_projects/boundary-waters-experimental/journey-network/`. The existing geographic chart remains the companion for distance and compass work.

## Visual design

- Landscape 17 × 11 inch overview, with additional detail sheets only if labels cannot remain legible at actual print size.
- Black strokes on white paper, irregular puddle outlines, horizontal lake hatching, restrained shoreline echoes, serif italic lake names and engraved hill symbols.
- Three broad lake-size classes derived from geographic surface area; exaggerate small lakes for legibility. Preserve approximate north/south/east/west relationships while moving and shrinking symbols to clarify the network.
- Label distinct connection points on each lake with stable identifiers. Associate each paddle-time range with a particular pair of connection points, not the lake as a whole.
- Draw portages as straight schematic links. Label each with rods and a range of hours. Clearly distinguish short river links with a different line pattern.
- Use subtle numbered circuit identifiers and a compact itinerary key. Preserve an uncluttered main network.
- Omit coordinate grids, a geographic scale bar and any rose suggesting that accurate bearings can be measured from the diagram. Include “Connections & travelling hours — not to scale.”
- Add supported nearby high points with rounded elevations and shore-relative descriptions. Separate named landmarks from unnamed terrain-derived summits. Do not imply that a schematic hill position gives a usable bearing.

## Geographic evidence and schematic geometry

Maintain two independent representations: source-backed geographic geometry for measurements and deliberately displaced schematic geometry for display. Never calculate travel distance from the diagram. Keep diagram coordinates explicitly identified as local schematic units; do not publish them as real geographic positions.

Reuse the saved DNR lakes, USFS trail records, published digitized route and lidar where they cover the expanded network. Acquire additional public source data when needed and record URLs, retrieval dates and source limitations. A published digitized route is not a recorded journey. Partial trail geometry must remain flagged as partial rather than silently treated as a complete carry.

Each connection requires evidence of connectivity. Its length may be an official published rod count, a complete mapped trail measurement, or an explicitly approximate source-backed estimate, in that order of preference. Missing evidence produces an omitted connection or a labeled unknown estimate, never a fabricated precise number.

Keep local geographic evidence in a companion QGIS project or clearly separate geographic view, so schematic and actual geometry cannot accidentally overlay as if they shared a real-world position.

## Travel-time model

All times are planning scenarios for an ordinary recreational tandem canoe team, not predictions or observed historical durations. Publish the assumptions with the timing table. Round displayed ranges outward to quarter hours, with a minimum displayed interval of a quarter hour for a nonzero leg. Keep the underlying unrounded calculations in the data.

### Paddling

Construct a feasible water-only path between the particular connecting points, accounting for mapped shorelines and islands. Use this geographic path as the base distance. Model indirect travel with a documented per-leg allowance: initially 15–35 percent additional distance, selecting larger allowances for complex shorelines or multiple bays. These percentages are teaching assumptions, not reconstructed evidence of a past traveler’s mistakes.

Use initial moving-speed scenarios of 4.0 km/h with favorable conditions and 2.0 km/h with adverse but still travelable conditions. These are adjustable model assumptions and must be checked against relevant canoe-planning references during implementation; cite any resulting revisions. Divide the shorter modeled distance by the faster speed for the lower bound and the longer modeled distance by the slower speed for the upper bound. Exclude rest, camp time and prolonged weather delays from the leg range.

Where direction changes wind exposure, describe the direction and exposure in the timing table. Do not assume that all headwinds remain travelable or that tailwinds always improve progress. The printed key states that windbound conditions mean waiting outside the displayed range. Avoid adding a numerical wind correction to a speed model that already includes adverse conditions.

### Portaging

Baseline: double carry, comprising two loaded traversals and one unloaded return. Use actual carry length rather than schematic line length. Convert rods at 5.0292 metres per rod; distinguish sourced rod counts from counts calculated from mapped or approximate lengths.

Initial walking scenarios are 2–3 km/h loaded and 3–4 km/h unloaded, plus 10–20 minutes total handling per carry link. Compute the lower bound as two loaded traversals at the faster loaded speed plus one return at the faster unloaded speed plus lower handling time; use slower speeds and higher handling for the upper bound. These are explicit, editable assumptions to check against planning references, not universal walking speeds. Note difficult terrain and source uncertainty separately. Waiting, group queues and extended rests are excluded.

### Itineraries and audit table

Provide predesigned Clearwater circuit choices assembled from stable leg IDs. Each row records mode, lake/connection endpoints, direction, geographic distance, length provenance, evidence quality, indirect-travel allowance, speed assumptions, handling allowance, low/high hours and source references. Sum unrounded leg times for itinerary totals before outward rounding. Label totals as modeled moving-and-handling time, excluding overnight stops and weather delays.

## Saved deliverables

1. A real editable `.qgz` schematic project and equivalent `.qgs`, with native layers, saved styles and editable print layouts.
2. Local schematic data and local geographic evidence, with a geographic companion project when separate views are needed.
3. A printable PDF chart and a compact instructor timing/itinerary key; exported preview images for visual inspection.
4. A leg-by-leg CSV timing table and machine-readable assumptions.
5. Source register, concise opening/rebuilding instructions and validation results.
6. A portable ZIP containing the projects, required local data, styles, layouts and documentation. Opening the delivered project must not require a virtual environment, a running script or a network service.

Use relative paths throughout. Keep the source image as a stylistic reference, not an uncredited background layer or invented map geometry.

## Verification and acceptance

- Every displayed connection resolves to an evidence record and its correct transport mode.
- Every paddle range resolves to a specific pair of shore connections and a geographic water path; modeled extra travel is separately identified.
- Carry calculations include two loaded traversals, one return and one handling allowance. Check rod conversions, rounded labels and itinerary sums independently.
- Existing known partial or approximate carry records remain visibly classified in the instructor data.
- Geographic distances and diagram coordinates never mix in calculations; diagram distortion cannot change a travel-time result.
- Reopen both project formats and a relocated portable copy. All required layers and layouts must load from local files.
- Export and inspect every PDF page at actual print size, checking label collisions, readable time ranges, monochrome rendering and the distinction between paddle, carry and river symbols.
- Report the final verified extent, included lake count, source gaps and model assumptions rather than claiming a field-validated navigation instrument.

## Workflow status

- Project context explored and design direction approved in conversation.
- Written specification prepared for the required review.
- Implementation planning, data expansion, project creation and output validation follow written-spec approval.
