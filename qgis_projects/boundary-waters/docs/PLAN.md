# Boundary Waters Atlas Implementation Plan

**Goal:** Build the approved six-page canoe atlas and editable QGIS project.
**Architecture:** Preserve original source snapshots; normalize local vector layers and terrain into a portable project; compose and export six layouts; validate data and rendered pages.
**Tech stack:** QGIS 3.22, GDAL, NumPy, Matplotlib, Python, Poppler and pypdf in the existing GIS container.

## Global constraints
Six pages, 17 x 11 inches landscape. No invented bathymetry or species locations. Stocking is dated evidence, absence is unknown. Historical KML and contemporary source datasets must be visually differentiated. Experimental terrain is bare earth, true aspect, with explicit camera position. QGIS layers use relative local paths.

- [x] Acquire route, bathymetry, hydrography, fisheries and mapped portage snapshots. Check API errors, pagination and duplicate IDs; retain query URLs and counts.
- [x] Normalize route and portage features in EPSG:26915. Design overview and four overlapping sheets around measured route extents. Preserve KML geometry and source text.
- [x] Download lidar DEM subsets, record source service and native vs output pixel size, validate finite elevations and coverage. Ray-cast canoe-eye silhouettes and mark viewpoint/landing on maps.
- [x] Build offline QGIS layers and six editable layouts. Export merged PDF and page previews with legends, scale, north, references, survey limitations and fisheries table.
- [x] Reopen project and PDF. Assert six 1224 x 792 point pages, valid layers and relative source paths, route preservation and evidence references. Render all pages and inspect typography, overlaps, margin insets, route continuity and depth visibility.
- [x] Write README, source register and validation record; add repo index entry. Review git diff and commit only atlas files.
