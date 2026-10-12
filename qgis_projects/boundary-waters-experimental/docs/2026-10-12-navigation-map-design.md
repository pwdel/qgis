# Clearwater navigation teaching map — design

Date: 2026-10-12
Status: approved by the user and implemented. Delivery additionally includes an uncompressed .qgs project, seven editable layouts, local styles/data and a portable bundle.

## Approved intent

Create an experimental Boundary Waters directory in the main qgis repository. Produce a hypothetical canoe navigation exercise starting and ending around Clearwater Lake, spanning several lakes with two predesigned pathways. The map should resemble an eighteenth-century black-and-white ink sketch. Show named lake outlines and selected high points. Maintain portages as GIS evidence layers but conceal their exact routes and landings in the student map, replacing them with broad clues.

Deliver an editable QGIS project, printable student map, and separate instructor answer map. Keep all new assets within this experiment. The existing historical atlas remains the source of reusable data, with original provenance and dates retained.

## Visual design

Use black ink on white paper, restrained italic serif lake labels, lightly irregular pen strokes, sparse terrain hachures and small high-point symbols, a simple compass rose, neatline and modest title cartouche. No color, sepia paper, satellite imagery, bathymetry, fisheries panels or dense topographic background. Geographic positions and scale remain accurate beneath the period styling; do not randomly displace shorelines or decorate the map with invented mountains.

Student sheet: 17 × 11 inches landscape, generous pencil space and margin bearing worksheet. High-point IDs refer to instructor notes. Use hachures locally around selected terrain features, keeping shorelines and clue areas legible. A metric scale and unobtrusive edge grid/ticks support ruler work. Include a print-at-100% calibration line. Export additional detail sheets if full-extent features cannot remain legible at this paper size; retain an overview.

## Two pathway designs

A — inner loop: Clearwater → West Pike → Pine → Little Caribou → Caribou → Clearwater. The saved USFS snapshot includes the West Pike–Pine trail. Recheck complete trail topology and both shore connections before accepting route geometry.

B — eastern loop: Clearwater → West Pike → East Pike → John → Little John → McFarland → Pine → Little Caribou → Caribou → Clearwater. The Friends of the Boundary Waters published route corroborates the broad loop through East Pike and John; confirm the intermediate John-to-Pine transitions from source geometry during preparation. Do not infer a direct John–Pine carry.

These are hypothetical teaching itineraries, not time estimates or reservations. Both loops have separate instructor route layers and ordered lake lists. Keep route lines off the student base map. Supply the chosen lake sequence as an exercise card so students construct the passage with pencil. Distances will come from the final checked geometry, not copied itinerary estimates.

## Layer separation and clues

Visible student group: lake outlines, lake names, high points, terrain hachures, clue regions, starting area and navigation furniture.

Hidden instructor group: source portage polylines, source landing points, unresolved landing candidates, route A, route B, instructor reference bearings and terrain sightlines. Use separate map themes and explicitly locked layout layer sets so enabling the instructor group cannot leak exact carries into a student export.

Student clues are broad, irregular shoreline search areas covering roughly 300–700 m of shoreline, adjusted to local geography. Small lakes may require a broader proportion of the shore rather than a fixed width. Never render a buffered trail corridor, precise landing dot, trail-shaped polygon or route segment across land. Use short neutral clues linked to a named lake, broad shore sector, headland or nearby terrain feature. Clue IDs do not encode coordinates. Describe these regions in the key as intentionally generalized exercise clues, distinct from uncertainty in source evidence.

Instructor features retain source IDs, source URL, snapshot date, evidence class, coordinate provenance and field_verified=false. Where exact geometry is absent, retain a candidate point/region and a documented gap; never fabricate an authoritative portage line. Reported portage existence and surveyed trail geometry are separate claims.

## High points and navigation

Extract candidate prominences from the saved elevation raster, then inspect their position relative to lakes and terrain sightlines. Identify unnamed points by neutral IDs rather than invented geographic names. Clearwater Palisades is a candidate named feature supported by local outfitter descriptions; verify its actual position before labeling it.

Only describe visibility as terrain-model visibility unless independent evidence supports recognition from the water. Forest canopy is absent from the existing bare-earth model. Keep that limitation in the instructor key and a compact map note. Derived elevations must carry units and source/vertical-datum information where known.

Use NAD83 / UTM zone 15N consistently with the existing atlas and explicitly configure transformations from WGS84 source layers. Distinguish grid, true and magnetic north. Obtain location/date-specific magnetic declination from an authoritative model before printing a numeric value; record model and date. Compass bearings, distance plotting and position resection form the core exercise. An optional astrolabe activity may be documented separately after clarifying the intended instrument; the map exercise does not depend on it.

## Evidence reviewed

- Local `../boundary-waters/docs/portage-evidence.md`: USFS-backed candidates and unresolved Pine–Little Caribou / Little Caribou–Caribou geometry. Historical KML lines are generalized and sometimes cross land; do not reuse them as checked paddling routes.
- Local `../boundary-waters/sources/portage-usfs-query.json`: full saved query, including WEST PIKE-PINE, CLEARWATER-WEST PIKE and EAST PIKE-WEST PIKE trails. Select by stable attributes, not array position.
- Local DNR hydrography and 8 m resampled lidar: reuse where coverage supports the expanded extent; acquire documented additional coverage where absent.
- https://www.friends-bwca.org/route/pike-and-pine-lake-loop/ — reviewed 2026-10-12; published outer-loop narrative through Clearwater, both Pike lakes, John, Pine, Little Caribou and Caribou. Its heading statistics conflict with some narrative distances; do not copy aggregate distances or portage counts.
- https://clearwaterhistoriclodge.com/gunflint-trail-activities/canoe-day-trips-2/ — reviewed 2026-10-12; local descriptions corroborate Clearwater–Caribou–Little Caribou–Pine connections and describe the Clearwater Palisades.

## Acceptance checks

1. Both itineraries close at Clearwater; each transition has documented evidence, and every unresolved geometry is explicitly identified.
2. Paddling segments stay within mapped water except separately classified, supported portages. Preserve islands and narrow connections.
3. Student map theme and exported PDF contain no exact portage paths, landings, hidden instructor labels or answer routes. Inspect both layer configuration and rendered pages.
4. Every shown high point has source-backed coordinates and an evidence note; no unverified all-weather or canopy visibility claims.
5. QGIS reopens with local relative assets; all required layers and layouts render. Record actual runtime and any unresolved transformation issues.
6. Printed scale calibration, north references, lake-label legibility, black-and-white appearance and clue widths pass visual review at final print size.
7. Instructor PDF clearly distinguishes recorded trails, approximate candidates, hypothetical water routes and teaching clue areas. Include a compact note that exact carries are deliberately omitted from the student exercise.

## Scope

This first version is a teaching-map experiment with two route choices. Campsite booking, trip duration, field verification, celestial-navigation tables and a general map-making framework are outside this build. The design is ready for review; implementation follows approval of this written specification.
