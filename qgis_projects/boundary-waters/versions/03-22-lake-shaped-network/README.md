# The Canoe Traveller's Network

A black-and-white journey diagram inspired by early engraved canoe-country maps: **22 lakes, 23 connections, 42 lake-crossing pairs, two Clearwater loops and a Rose out-and-back option**. Simplified real lake footprints and source-shaped carry bends are deliberately distorted. Crossing duration influences lake size; carry duration guides spacing, constrained by geographic ordering and legibility. The chart shows rounded ranges of hours, calculated from real-world evidence beneath the drawing.

## Open the saved projects

- **[journey-network.qgz](journey-network.qgz)** — editable diagram, local-CRS GeoPackage, saved styles, five native print layouts. Equivalent [uncompressed project](journey-network.qgs).
- **[geographic-evidence.qgz](geographic-evidence.qgz)** — real lake outlines, measured base water paths, source/approximate carries, modeled shoreline extensions, candidate landings and high-ground positions in EPSG:26915.
- **[Journey chart PDF](output/pdf/journey-chart.pdf)** — one 24 × 12 inch panoramic sheet.
- **[Instructor PDF](output/pdf/journey-instructor.pdf)** — assumptions, three itineraries and a complete leg register (four 17 × 11 inch sheets).
- **[Portable project ZIP](output/journey-network-project.zip)** — saved projects and their local dependencies.

Extract the entire ZIP, then open the QGZ. No virtual environment, running script or network connection is required. Tested with the installed QGIS 4.2.3 on macOS. Baskerville is used for the engraving-style lettering; another computer may need the font or a serif substitution. PDFs carry their font resources.

## Read the chart

Each connecting passage has a letter. Beneath a lake, `a-j` gives a paddling range between those passages. `S` is the hypothetical Clearwater start/finish; `T` is an imagined water turnaround on a terminal lake. `b-c same landing` identifies the shared modeled West Pike landing, not a missing paddle leg.

Curved carry labels show derived rods (~) and double-carry hours: two loaded walks, an unloaded return and one handling allowance. Asterisks flag approximate carry geometry. Dashed links are water connections rather than portages. All rod counts are derived from geometry, not official published counts.

Times include imperfect travel and a favorable-to-adverse wind envelope. They exclude rest, camp time, queues and weatherbound waits. Quarter-hour bounds are deliberately coarse; `0-0.25 h` means a brief nonzero passage. Geographic distances, raw hours, direction axes and individual allowances are in [data/leg-times.csv](data/leg-times.csv); [assumptions](data/assumptions.json) records the model used. Circuit totals sum unrounded leg values, then round outward.

**This is a schematic: measure no bearings or distances from its drawing.** Use the geographic companion for real positions. High-ground IDs are terrain candidates, not field-verified visible landmarks. The diagrams can support route reasoning and recognition exercises; they do not replace compass geometry on an undistorted map.

## Wider, source-shaped revision

Added Duncan and West Bearskin to the west, and Fan, Vaseux and Moose to the northeast. DNR calls West Bearskin simply `Bearskin` in the source data and leg register. The chart uses the familiar West Bearskin name.

Each lake retains its principal arms and broad orientation after shoreline simplification and unequal horizontal/vertical scaling. Display width follows `18 + 18 × sqrt(representative crossing hours)` in diagram units, where representative hours is the midpoint of the longest modeled crossing between the included points. This is not a full-lake end-to-end travel survey.

Carry spacing targets `7 + 18 × sqrt(midpoint carry hours)` before corrections for trail bends. A layout optimization balances those targets against approximate geographic order and label room. Source bends are mapped between the distorted shores; small portions falling inside the diagram lakes are clipped. Thus longer journeys receive more space, but **neither geographic distance nor time has a uniform ruler scale**. Printed hour ranges remain the quantitative reference.

## Data and editing

`data/diagram.gpkg` contains the actual QGIS diagram layers in an explicit local engineering CRS. `schematic-*.json` are internal drawing records, not GeoJSON or longitude/latitude data. `geographic-*.geojson` contains actual EPSG:26915 geometry. These coordinate spaces live in separate projects.

The five layouts are editable in QGIS under Project → Layouts. Copies are in `layouts/`; styles are in `styles/`. Edit the time-weighted layout and label-placement rules in `scripts/schematic.py`, or edit the GeoPackage directly in QGIS. Rebuilding overwrites generated outputs, so preserve any manual edits first.

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
