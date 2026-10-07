# Paria River Ranch horse-riding atlas

Approved by the owner on 2026-10-07. First pass is a planning PDF; Avenza is a separate second pass.

## Design

Four 17 x 11 inch landscape sheets with 0.125 inch bleed: regional hauling context; ranch and nearby riding context; Mount Carmel/Bay Bill/Belly of the Dragon; Red Canyon/Losee/Casto/Coyote Hollow/Tom Best. Match the existing atlas's local sources, derived data, editable QGIS layouts, individual and combined PDFs, previews, project metadata and validation records. No private Minnesota locations are copied.

Use published geometry and explicit evidence for parking, roads, turnarounds, water, trails and terrain. Never infer trailer fit from a road line, current stock water from hydrography, horse permission from hiking access, or safe trail grade from a hillside slope. Unknown values remain unknown. Critical claims need a resolvable evidence record, date precision and limitations.

Peter's center, radius, dates, rig dimensions and final applications have not been supplied. The four geographic panels are provisional editorial extents, not a requested radius. "Red Mountain" is retained as an ambiguous user label; the selected cluster is Red Canyon/Thunder Mountain near Coyote Hollow, not a silently substituted confirmed place.

## Implementation plan

**Goal:** Publish a source-backed, portable four-sheet Utah equestrian planning atlas in the public qgis repository.

**Architecture:** Preserve public service responses and query manifests in sources; create presentation layers and terrain derivatives in derived; build QGIS layouts and PDFs from those local snapshots. Store critical claims separately from spatial geometry and validate their references before export.

**Tech stack:** Python standard library for requests, QGIS 3.22/PyQGIS, GDAL, NumPy, pypdf and Poppler in the existing GIS container. Work in a separate branch and isolated container directory.

1. [x] Acquire official trailheads, roads, trails, topo context, elevation mosaic, and lidar coverage. Store service metadata, queries, feature counts and hashes. Compare advertised counts with returned IDs; reject truncated responses.
2. [x] Create a local, versioned equestrian evidence profile using GeoJSON properties and source IDs. Critical water, turnaround, grade and exposure claims retain verification state and scope. Record explicit unknowns and conflicting/expired sources.
3. [x] Build native QGIS project and four layouts. Use EPSG:26912 for metric maps; preserve WGS84 GeoJSON. Include north, scales, readable legends, source links, known hazards and missing checks on every sheet. Terrain must disclose source resolution versus exported pixel size.
4. [x] Verify every layer after reopening and relocating the project; validate source hashes, geometry, evidence links, PDF dimensions and page counts. Render and inspect every final page; repair overlap or illegibility.
5. [ ] Publish the reviewed artifacts and documentation to qgis_projects/Utah/paria-river-ranch and add a repository index link. Verify remote commit and public artifact path.

## Additional terrain pages

Do not manufacture precise avoidance polygons. First inspect lidar coverage and source availability. Additional perspectives require an identified feature, native-resolution terrain and explicit explanation of what the model can and cannot support. If only a service mosaic is used in this pass, retain four sheets and document native lidar analysis as the next terrain task.
