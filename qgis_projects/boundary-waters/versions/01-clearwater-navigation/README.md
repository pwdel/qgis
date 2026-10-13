# Clearwater & the Eastern Lakes — navigation teaching experiment

A black-and-white chart in the manner of an eighteenth-century ink draught: named lake outlines, engraved shoreline accents, hill hachures, twelve terrain-derived high points and broad passage clues. Two hypothetical canoe circuits begin and end at Clearwater Lake.

## Open the real project

**[Open clearwater-navigation.qgz](clearwater-navigation.qgz)** in QGIS. An equivalent uncompressed **[clearwater-navigation.qgs](clearwater-navigation.qgs)** is included for inspection and editing. Keep this directory intact: data, compass artwork, saved styles and seven editable layouts use local relative paths. No virtual environment, container, network connection or script execution is needed to open the saved project.

Built and reopened with **QGIS 4.2.3 on macOS arm64**. Baskerville is the intended font and is installed on the tested Mac. On other systems, install an appropriately licensed matching font or select a local serif font and check label/layout fit. The PDFs contain their own font resources.

- **[Student chart PDF](output/pdf/clearwater-student.pdf)** — three sheets: overview, western detail, eastern detail.
- **[Instructor key PDF](output/pdf/clearwater-instructor.pdf)** — four sheets: circuit A overview, circuit B overview, western A detail, eastern B detail.
- **[Portable project bundle](output/clearwater-navigation-project.zip)** — project, data, styles, layouts, documentation, scripts and PDFs.

Print landscape, **17 × 11 inches**, at **100% / actual size**. The 50 mm calibration line must measure 50 mm. Use the linked scale bar on each sheet; the detail sheets have different scales.

## Layers and layouts

The saved project opens with **STUDENT** layers visible. **INSTRUCTOR** and **REFERENCE** groups are hidden. Use the map-theme menu to switch between student, both circuits, circuit A and circuit B. The print layouts explicitly lock their own layer sets and styles: turning instructor layers on in the canvas does not add answers to the student PDFs.

Student layers show shorelines, lake names, hachures, high points, a departure symbol and dotted clue regions. Exact trail segments, approximate passage sketches, candidate landings, water routes and terrain sightlines remain available in the instructor group. The reference group contains the original elevation raster. An optional neighbouring-water layer is off by default.

All seven sheets are native editable QGIS layouts under **Project → Layouts**. Separate `.qpt` templates live in `layouts/`, and `.qml` styles plus the vector compass are in `styles/`. Templates belong with this project and its matching layer IDs; the saved project layouts are the primary editing surface.

## Predesigned choices

**A — Inner circuit:** Clearwater → West Pike → Pine → Little Caribou → Caribou → Clearwater. About **30.5 km of hypothetical paddling**, excluding carries.

**B — Eastern circuit:** Clearwater → West Pike → East Pike → John → Little John → McFarland → Pine → Little Caribou → Caribou → Clearwater. About **48.7 km of hypothetical paddling**, excluding carries and the short river transition.

These are geometric exercise choices, not trip-duration estimates. Water legs were constructed between evidence-backed or explicitly approximate shoreline candidates, avoiding mapped land and islands with a 2 m GIS tolerance. They are not field-recorded tracks. Exact carry geometry is deliberately absent from the student edition.

## Evidence distinctions

Clue areas intentionally generalize a shore sector; their size is a teaching choice, not a statistical confidence interval. Matching lower-case letters indicate the same passage exercise; b / c marks a shared shore area. They do not depict the path across land.

The USFS record supports seven selected trail segments. **Clearwater–West Pike is incomplete in that record:** its saved segment ends about 579 m from West Pike's mapped shore. The published digitized route supplies an approximate continuation, separately styled and classified. **Pine–Little Caribou and Little Caribou–Caribou** have published route and local outfitter support, but no corresponding geometry in the complete USFS query. Their lines are explicitly approximate published sketches. **Little John–McFarland** is a short river connection, not an invented portage; the water polygons leave a small gap. John–Little John retains the recorded carry as the planned transition rather than assuming the channel is passable.

Twelve high points come from the saved 8 m resampled Minnesota lidar raster. Labels round elevations to 5 m, without claiming 5 m accuracy. Eleven have a sampled bare-earth sightline from a hypothetical water leg; all remain unverified for canopy obstruction and recognition in the field. Hachures indicate terrain slope and do not mark trails. See [instructor notes](docs/instructor-notes.md) and [geometry checks](docs/geometry-validation.json).

## Compass and coordinates

The chart uses **NAD83 / UTM zone 15N (EPSG:26915)**, metres, grid-north up. Source GeoJSON and GPX are longitude/latitude WGS84. Preparation explicitly uses the available **Inverse of NAD83 to WGS84 (1) + UTM zone 15N** operation, nominal transformation accuracy 4 m; this is not a claim of source positional accuracy. The project saves the matching operation without fallback. All loaded output layers already use the project CRS.

At the reference point **48.07° N, 90.20° W**, grid convergence is approximately **2.1° east of true north**. BGS WMM2025 gives declination **2.912° west** for **2026-10-12**, using 0.5 km ellipsoidal altitude as a model input. Thus, near the chart centre, add **2.1°** to a grid bearing for true bearing or **5.0°** for magnetic bearing, reducing modulo 360°. These are centre approximations, not corrections for every place/date. The north rose indicates true north. [Saved model response](sources/magnetic-model.json).

## Sources, terms and reproducibility

[Source register](docs/SOURCES.md) records acquisition dates, official endpoints, published-route references, licensing notes and the limits of each layer. [Validation report](docs/validation.json) records actual saved-project checks. [File hashes](docs/manifest-sha256.json) identify the delivered inputs and outputs.

To rebuild on the tested Mac (the saved project does not require this):

```sh
./scripts/qgis-python.sh scripts/prepare.py
./scripts/qgis-python.sh scripts/build_project.py
python3 scripts/assemble_pdfs.py  # requires pypdf
./scripts/qgis-python.sh tests/validate_project.py
```

`qgis-python.sh` uses the Python and libraries bundled inside the installed QGIS app, not a virtual environment. Override `QGIS_APP` if the app path changes. `scripts/fetch_sources.py` is an explicit online refresh step; do not run it during ordinary opening or validation. A refresh can change the evidence and requires rechecking the routes.
