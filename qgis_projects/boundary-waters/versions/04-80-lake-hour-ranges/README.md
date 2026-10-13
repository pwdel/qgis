# The Canoe Traveller's Network

A black-and-white engraved teaching diagram: **80 lakes, 74 connections, 132 modeled crossing alternatives, two Clearwater loops and a Rose out-and-back option**. Recognizable lake footprints and recorded carry bends are deliberately distorted. Printed time ranges are based on geographic source geometry, not measurements of the drawing.

The expanded area runs from the Clearwater/Pike lakes west through Poplar, Winchell, Brule and the Long Island country, with Gunflint, Seagull and Saganaga to the north. Six lakes are context only; missing connections are not invented to make a continuous network.

## Open the saved projects

- **[journey-network.qgz](journey-network.qgz)** — editable diagram, local-CRS GeoPackage, saved styles, ten native print layouts. Equivalent [uncompressed project](journey-network.qgs).
- **[geographic-evidence.qgz](geographic-evidence.qgz)** — real lake outlines, measured base water paths, source/approximate carries, modeled shoreline extensions, candidate landings, sourced landmarks and hidden unverified terrain points in EPSG:26915.
- **[Journey chart PDF](output/pdf/journey-chart.pdf)** — one 36 × 24 inch sheet.
- **[Instructor PDF](output/pdf/journey-instructor.pdf)** — assumptions, three itineraries and a complete leg register (nine 17 × 11 inch sheets).
- **[Portable project ZIP](output/journey-network-project.zip)** — saved projects and their local dependencies.

Extract the entire ZIP, then open the QGZ. No virtual environment, running script or network connection is required. Tested with the installed QGIS 4.2.3 on macOS. Baskerville is used for the engraving-style lettering; another computer may need the font or a serif substitution. PDFs carry their font resources.

## Read the chart

Each lake has at most one short hour range: the **longest successfully modeled crossing between its included landings**. Other crossing alternatives remain in the instructor register. The selected endpoint pair and leg ID are attributes of the time-label layer. This is not an estimate for every possible trip across that lake. Lakes without modeled crossings have no time label.

Time ranges sit in the water footprint where they fit. Displaced labels have short leaders to their own lake or passage. Compact carry IDs and hours sit beside source-shaped links. Rod counts remain in the CSV and geographic layer, avoiding repeated text on the drawing. `S` is the Clearwater departure. Asterisks mark approximate geometry; dashed passages are water connections.

Eight sourced landmarks replace generic summit symbols: Clearwater, Rose, Winchell and Seagull cliffs, the Brule rockslide, and Rose, Johnson and Saganaga falls. Cliff/rockslide records describe published lake viewpoints; `(walk)` marks a land visit to a waterfall. A landmark leader associates the feature with its lake; it is not a surveyed sightline. [Landmark evidence](docs/LANDMARKS.md) includes specific vantage descriptions and coordinate uncertainty. None of these schematic anchors is a precise compass-bearing target.

Times include imperfect travel and a favorable-to-adverse wind envelope. They exclude rest, camp time, queues and weatherbound waits. Quarter-hour bounds are deliberately coarse; `0-0.25 h` means a brief nonzero passage. Geographic distances, raw hours, direction axes and individual allowances are in [data/leg-times.csv](data/leg-times.csv); [assumptions](data/assumptions.json) records the model used. Circuit totals sum unrounded leg values, then round outward.

**This is a schematic: measure no bearings or distances from its drawing.** Use the geographic companion for real positions. Generic terrain candidates remain hidden in the geographic companion and are not presented as visible landmarks. The diagrams can support route reasoning and recognition exercises; they do not replace compass geometry on an undistorted map.

## Source-shaped revision

Every added lake has explicit DNR feature IDs; duplicate names are disambiguated, including Caribou (Poplar) versus Caribou near Clearwater. DNR's `Bearskin` is labeled West Bearskin on the chart. Source selection, disconnected groups, omitted crossings and narrow-channel routing limits are documented in [the expansion notes](data-expansion-notes.md).

Lakes retain broad arms and orientation after simplification and unequal scaling. Display width follows `22 + 20 × sqrt(representative crossing hours)` in diagram units; context-only lake size uses an area-based fallback. Carry spacing is influenced by midpoint travel time, geographic ordering and legibility. The empty northern gap is compressed. **Neither distance nor time has a uniform ruler scale.**

## Data and editing

`data/diagram.gpkg` contains the actual QGIS diagram layers in an explicit local engineering CRS. `schematic-*.json` are internal drawing records, not GeoJSON or longitude/latitude data. `geographic-*.geojson` contains actual EPSG:26915 geometry. These coordinate spaces live in separate projects.

The ten layouts are editable in QGIS under Project → Layouts. Copies are in `layouts/`; styles are in `styles/`. Edit the time-weighted layout and label-placement rules in `scripts/schematic.py`, or edit the GeoPackage directly in QGIS. Rebuilding overwrites generated outputs, so preserve any manual edits first.

Timing assumptions are centralized in `scripts/timing.py`; `data/assumptions.json` is the generated snapshot, not the input configuration. To change speeds or handling, edit that script's `ASSUMPTIONS`, then rerun preparation and export. Indirect-travel allowances are assigned in `prepare.py`.

## Rebuild on the tested Mac

The launcher uses Python bundled with `/Applications/QGIS-final-4_2_3.app`. Override `QGIS_APP` for another installation. Saved projects do not require this runtime to remain at that path.

```sh
./scripts/qgis-python.sh scripts/prepare.py
./scripts/qgis-python.sh scripts/schematic.py
./scripts/qgis-python.sh scripts/build.py
python3 scripts/assemble.py  # pypdf is needed only for PDF assembly
python3 -m unittest discover -s tests
./scripts/qgis-python.sh scripts/validate.py
```

Preparation consumes bundled local evidence. Its copy-if-missing fallback only bootstraps the original working directory from the parent experiment. No online refresh runs automatically. The original terrain extraction is documented in the parent project; this rebuild reuses its derived points.

[Sources and limitations](docs/SOURCES.md) distinguish recorded trails, approximate lines, modeled shore extensions, hypothetical water paths and timing assumptions. [Validation](docs/validation.json) records actual arithmetic, geometry and project-portability checks.
