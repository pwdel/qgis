# Clearwater Navigation Map Implementation Plan

> For agentic workers: use executing-plans to implement this plan inline, with verification at each deliverable.

**Goal:** Save an editable, portable QGIS project and black-and-white student/instructor PDF maps in this directory.

**Architecture:** Prepare local vector evidence and terrain-derived drawing layers, then build native QGIS styles and layouts. Student layers are explicit allowlists; instructor layers retain portage evidence and both hypothetical itineraries. All outputs and dependencies remain on disk in this project.

**Tech stack:** Installed QGIS 4.2.3, its Python 3.12/GDAL/PROJ, Shapely, SciPy, NumPy; PDF render checks.

## Global constraints

- Black ink on white; eighteenth-century-inspired hachures and lettering.
- Exact portages/landings and route answers excluded from student exports.
- Both hypothetical loops start/end at Clearwater. Unknown trail geometry stays unknown.
- Local relative assets, real .qgz and .qgs outputs, native editable layouts, no virtual-environment-only delivery.
- Main qgis checkout and new experimental directory are the user-selected destination.

## Deliverable 1 — evidence and geometry

- [x] Create `scripts/qgis-python.sh` to run the installed QGIS Python with its packaged paths.
- [x] Write `tests/validate_project.py`: assert project files, two route choices, nonempty clue/high-point layers, valid relative assets and hidden answer layers. Run before authoring to establish missing-output failure.
- [x] Save public source responses, retrieval recipes and source metadata under `sources/`.
- [x] Implement `scripts/prepare.py` to produce projected GeoJSON layers, water-only paddle geometry, portage evidence, generalized clue regions and terrain high points/hachures under `derived/`.
- [x] Check transition topology, shore mismatches, route closure, sampled terrain coverage and missing geometries; save `docs/geometry-validation.json`.

## Deliverable 2 — editable cartography and print outputs

- [x] Implement `scripts/build_project.py` using native QgsVectorLayer renderers, QgsPrintLayout maps/labels/scale bars/legends and locked map-layer lists.
- [x] Save `clearwater-navigation.qgz` and `clearwater-navigation.qgs`; save style files and layouts under `styles/` and `layouts/`.
- [x] Export student and instructor PDFs to `output/pdf/`, overview previews to `previews/`.
- [x] Reopen both project formats and export again from the saved project, checking source paths and hidden layers.

## Deliverable 3 — review and handoff

- [x] Render final PDFs independently and inspect page images, lake labels, scale, high points and generalized clues. Repair any overlapping or missing content.
- [x] Run `scripts/qgis-python.sh tests/validate_project.py`; save measured runtime and assertions in `docs/validation.json`.
- [x] Save `README.md`, source manifest and instructor evidence notes. Link main README to the experiment.
- [x] Provide the saved QGIS project and queue a PDF preview in Codex; report artifacts and evidence limitations. Desktop QGIS UI inspection was unavailable because the Mac was locked; native saved-project and relocation checks ran successfully.
