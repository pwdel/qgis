# Horse terrain, snow and camping atlas expansion

Approved in the conversation on October 8, 2026, including the horse-and-rider interpretation of grade, surrounding slope and exposure. Original four-page edition remains available.

## Design and implementation plan

Goal: retain the regional overview and three access sheets, add three terrain sheets and three snow sheets, then add camping maps where the evidence warrants them. Use the original landscape format, editable QGIS layouts, individual PDFs and a combined expanded PDF.

Architecture: separate downloaded evidence from modeled terrain and presentation. The existing local EPSG:26912 terrain and trail layers support reproducible terrain screening. Independent source research supplies snow observations/climatology and camping boundaries. A new expansion builder loads the existing QGIS project and adds layouts; it does not overwrite the original project or PDF.

Global constraints: no invented horse-safe slope thresholds, cliff edges, trail-tread grades, permissions or snow probabilities. Missing data remain unknown. Snow climatology is not a forecast. Percent grade = 100*tan(angle). Geometry buffers indicate search context, not safety clearance.

- [x] Terrain: derive percent slopes and local relief from each area's source DEM; retain source resolution. Map steep ground within a declared trail corridor and show detailed cutouts. Illustrate 30/45/60/90 percent with corresponding angles. Trail longitudinal grade, sidehill exposure and local height must not be conflated. Use terrain-cell slopes and neighborhood relief where trail-tread measurements are unavailable.
- [x] Snow: obtain NOAA station snowfall normals and historical snow-depth probabilities; investigate accessible spatial snow data. Require actual numerator/denominator or documented probability definition. Use October prominently and compare all months, preserve elevations, dates, missingness and source scale. If a reliable grid cannot be obtained, map measured station probabilities with explicitly unresolved intervening terrain rather than fabricate a smooth cloud.
- [x] Camping: obtain official ownership data and current rule sources. Map documented patchwork where available; separate ownership from permission, designated stock camps from dispersed camping, and expired orders from current rules.
- [x] Presentation: build editable expansion QGIS layouts, labeled terrain cutouts, slope illustration, monthly snow charts, evidence footers and expanded PDF. Retain original sheet URLs and create a separate expanded edition.
- [x] Verification: test grade conversions, nodata handling and analytical slope behavior on synthetic terrain; verify source references, raster CRS, finite extents, relocated QGIS layers, PDF page boxes, page counts and searchable text. Render and inspect all new pages. Check hashes and publish approved expansion to public qgis main; verify remote paths.

Implementation and pre-publication verification completed:13 sheets;873 automated checks;4 analytical terrain tests;all13 finalPDF pages visually inspected. Publication is recorded by the Git commit containing this plan.
