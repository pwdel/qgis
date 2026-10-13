# Eighty-lake geographic evidence expansion

The expanded teaching network contains **80 uniquely identified named lakes, 74 transitions, and 132 modeled paddle legs**. All 22 original lake identities and all 23 original transition records are retained. The three original itineraries retain their exact low/high timing totals.

## Source acquisition and identity

Public Minnesota DNR hydrography and USFS national forest trail services were downloaded on 2026-10-12. `sources/expanded-acquisition.json` records every complete query URL, raw response filename, and retrieval timestamp. The raw batches and combined source datasets retain EPSG:4326 source geometry. Outputs use EPSG:26915.

The expansion query envelope was -90.95,47.85,-90.28,48.20; complete intersecting features were retained. It returned 627 named-basin hydrography features (including features called Unnamed) and 497 trail features. Only the 58 specifically selected additional lake identities in `sources/expanded-selection.json` are used. The saved output lake footprint extends from approximately **91.05657°W,47.91862°N to 90.04635°W,48.29733°N**, including the full Saganaga polygon extending beyond the query rectangle.

Selection uses DNR object IDs, not name matching. `Caribou (Poplar)` (DNR basin 16024000) is separate from the original Caribou near Clearwater (16014100). Original Moose remains unchanged. Canadian halves are joined only when explicitly selected as parts of the same lake. Saganaga uses the full named Saganaga polygon, avoiding double counting its overlapping Minnesota-only feature. Moon is the eastern Moon basin 16011700, not the western same-named lake. Seagull uses DNR's Sea Gull polygon (object ID 262234). DNR's spelling Pillsbery is retained; the USFS source calls it Pillsbury on some trail records.

## Connection evidence

`sources/expanded-portages.json` is a reviewed manifest of 51 additional USFS portages. Each trail name agrees with the corresponding lake pair (allowing official abbreviations/spelling variants), consists of one complete source path, and has both endpoints within 30 metres of the assigned DNR lake polygons. Endpoint proximity verifies a named source trail; proximity by itself does not create a connection. Each new connection has a stable compact `A01`–`A51` ID in the manifest and records its source object ID and trail name. Original transitions `a` through `w` remain exact.

The unsnapped USFS lines remain in `geographic-connections.geojson`. `geographic-modeled-connections.geojson` separately includes the small modeled shoreline extensions, and each transition records its extension length. Length-derived rods are calculated estimates, never represented as official portage counts. Timing retains the existing paddle/carry assumptions.

**Context-only lakes:** Daniels, Gunflint, Brule, Morgan, Seagull, Saganaga. They have real geographic polygons but no accepted transition in this selected evidence network. Disconnected groups also remain separate. A missing edge does not imply that no real route exists. River reaches, lake narrows and incompletely matched portages were not invented to connect the graph.

## Paddle paths and coverage limits

All emitted paddle geometries pass the existing water-containment check against the lake polygon buffered by two metres. Lake paths are hypothetical teaching examples, not recorded tracks or navigation instructions. Existing lake pairs are evaluated fully. For added lakes with more than four landings, a star plus adjacent landing pairs limits the number of examples; this omits three East Bearskin combinations.

Five additional landing pairs could not be routed by the existing 25-metre water grid: Alder (East Bearskin landing to Canoe landing), Skipper (Poplar to Little Rush landings), two Allen combinations involving the Pillsbery landing, and Snipe's hypothetical turn point to Missing Link landing. These are omitted rather than replaced with lines crossing land. Their failure may reflect narrow water features and raster resolution, and is not evidence of real-world impassability. `network.json` records each failed and intentionally omitted pair in `coverage`.

The network schema preserves `lakes`, `connections`, `legs`, and `routes`. An optional `coverage` object adds selection criteria, context-only lake names and omitted/failed pairs. Geographic lake features also include `connection_count` and `context_only` properties. The regenerated CSV and assumption file preserve the established timing schema.

## Verification performed

- Exactly 80 distinct lake names, with 58 additional explicit source selections.
- Original 23 connection dictionaries compared equal to the saved Git HEAD version.
- All three original itinerary low/high totals compared exactly equal to Git HEAD.
- Valid lake geometries and water-valid emitted paddle legs.
- Complete source manifest and retrieval metadata saved with the artifact.
