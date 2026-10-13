# Boundary Waters Journey Network Implementation Plan

> **For agentic workers:** Use executing-plans inline, task by task. User approved implementation in the existing project directory.

**Goal:** Deliver a portable editable QGIS journey network and verified monochrome chart with source-backed connections and modeled travel times.

**Architecture:** Keep real EPSG:26915 geographic evidence separate from an explicitly local schematic coordinate system. Build the timing table from geographic legs, then render schematic data with native QGIS layers and layouts. Reuse the existing experiment's evidence and proven native QGIS runtime.

**Tech stack:** Installed QGIS 4.2.3 / Python, Shapely, GDAL, standard-library CSV/JSON, native PDF export, Poppler and PDFKit verification.

## Global constraints

- Black ink on white; distorted puddles, straight carry links, approximate geographic ordering.
- Real local `.qgz` and `.qgs` files with relative paths and no online dependencies.
- Double carries: two loaded traversals, one return, one handling allowance.
- Times are modeled ranges, including indirect paddling and adverse travelable wind; weatherbound waits excluded.
- Existing geographic project remains intact. Work on existing feature branch in the user-requested project directory.

## Task 1: Evidence and timing

Files: journey-network/scripts/{timing,prepare}.py, tests/test_timing.py, sources/, data/.

- [x] Test independently calculable cases: 1 km double carry includes three traversals; 4 km paddle receives detour allowance; displayed bounds enclose exact times; invalid distances rejected.
- [x] Implement pure `paddle(distance_km, detour_low, detour_high)`, `carry(distance_km)` and `rounded(low, high)` functions returning hour pairs.
- [x] Reuse local hydrography and USFS evidence; measure and inspect additional named trail endpoints. Include verified northwestern branches and southern lake connections.
- [x] Generate lake polygons, landing pairs and water-contained paths for connection pairs; retain approximate and incomplete source classifications.
- [x] Export JSON/CSV leg records, assumptions, circuit sequences and totals. Check connectivity and every water path against source polygons.

Run: `python3 -m unittest discover -s qgis_projects/boundary-waters-experimental/journey-network/tests`.
Expected: timing tests pass.

## Task 2: Editable cartography

Files: scripts/build.py, data/schematic-*.geojson, styles/, layouts/, journey-network.qg{z,s}, geographic-evidence.qgz, output/pdf/.

- [x] Build approximately ordered lake nodes with size classes, horizontal hatching, engraved landmark symbols, name/endpoint/time labels and carry links.
- [x] Use a local engineering CRS for schematic layers, EPSG:26915 for separate geographic project.
- [x] Add native editable chart and timing-key layouts; save styles and templates.
- [x] Save project formats, export PDFs, render previews and inspect all pages. Correct collisions before final verification.

Run the existing `scripts/qgis-python.sh` launcher with the new scripts. Expected: valid layers, saved projects, successful PDF export.

## Task 3: Delivery verification

Files: scripts/validate.py, docs/validation.json, README.md, docs/SOURCES.md, output/journey-network-project.zip.

- [x] Reopen both formats; validate layers, native layouts and timing provenance. Verify all chart connections exist in the evidence graph.
- [x] Copy bundle to a temporary directory, reopen and re-export offline; assert no data source references outside the copy.
- [x] Render final PDFs with Poppler and Apple PDFKit. Inspect every page.
- [x] Package all local dependencies, document assumptions and source gaps, record validation and commit only task files.

Expected: no broken layers or external absolute paths; all arithmetic, geometry and portability checks pass.

Completed: 17 lakes, 18 connections, 33 crossing pairs; 6 unit checks and 492 native/geometry/portability checks passed. Four PDF pages rendered and inspected; Apple PDFKit opened all four pages.
