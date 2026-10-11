# Utah riding maps on iPhone

Export date: October 11, 2026. Research remains dated October 7-9, 2026; exporting does not refresh water, road, snow or fire information. Existing map extents are unchanged. These are planning maps, not verified multi-day itineraries.

## Choose the right download

| App/use | Files | What they contain |
| --- | --- | --- |
| Avenza or another geospatial PDF reader | `output/mobile/geopdf/{area}-five-maps.pdf` | Five geographic sheets per area: access, terrain, October snow, camping, historical fire. Each page is a separate map; insets remain reference only. |
| Full atlas | `output/mobile/geopdf/utah-riding-geospatial-atlas.pdf` | All 19 pages: 16 main maps georeferenced, three trail-profile pages deliberately not georeferenced. Prefer the five-map bundles for navigation imports. |
| QField on iPhone | `output/mobile/qfield/{area}-qfield.zip` | Self-contained QGIS project, local data, selectable themes and offline references. No cloud subscription required for this manual workflow. |
| Gaia GPS | `output/mobile/gaia/{area}-trails-and-points.gpx` | Separate mapped trail components and planning waypoints, with evidence/limitations in descriptions. |
| Gaia custom maps | `output/mobile/gaia/*.tilejson.json` | Fifteen custom map definitions using publicly hosted XYZ tiles. Import individually, then download needed coverage in Gaia Premium. |
| Gaia custom-map preparation | `output/mobile/gaia/{area}-custom-map-sources.zip` | Five georeferenced, styled map-panel TIFFs plus their PDF legends. Requires publishing through a supported custom-tile workflow before use in Gaia. Not a direct Gaia ZIP/TIFF import. |

Area names: `ranch`, `mount-carmel`, `red-canyon`. Individual geospatial PDFs are also supplied in `output/mobile/geopdf-individual-sheets.zip`.

## QField iPhone import

1. Download an area's `-qfield.zip` to Files on the iPhone (or AirDrop it).
2. In QField, choose **Open local files**, then **+**, and import the compressed project. Select the ZIP. Open the area's `.qgz` project after extraction.
3. Open the map-theme selector to switch between access, terrain, snow months, camping, fire history, annual fire context and trail profile attributes. The default is Access. Snow has twelve separate month themes; annual fire likelihood is not a monthly forecast.
4. Tap map features to inspect original source attributes. Profile-route features include modeled ascent/descent, geometry provenance and gaps. All evidence vectors are read-only; this is a reference package, not a synchronized field-editing project.
5. The `reference` folder contains the profile page, five map sheets with legends, source notes and evidence. Use Files/PDF viewer for those documents. Web citations require connectivity; the packaged maps and notes do not.
6. Before departure, open each needed area in airplane mode, switch themes, inspect features and verify GPS location against a known point. Device import, font substitution, performance and on-location GPS behavior have not been certified in this build environment.

Official instructions: [QField storage and iOS ZIP import](https://docs.qfield.org/how-to/project-setup/storage/). Manual packages use relative paths and local GeoTIFF/GeoPackage/GeoJSON data. Import the ZIP, not the standalone `.qgz` without its `data` folder. Some shared vector data extends beyond the initial view; raster coverage remains limited to the researched area.

## Gaia iPhone import

Import each area's GPX using Gaia's file-import workflow. The GPX contains WGS84 coordinates, one track per disconnected mapped component and planning waypoints. No estimated elevations are inserted into track geometry. Some tracks are clipped at the sheet edge; they are not complete loops or recorded rides. Any elevation analysis Gaia calculates may differ from the companion atlas's documented smoothing and DEM method.

Each waypoint description retains water/trailer uncertainty and source IDs. Keep the matching `-evidence.json` and atlas as full references; the way an app displays descriptions can vary. A water-related trail name does not establish a water source. Current horse permission remains unverified where stated, including conflicting published attributes. These exports do not enable turn-by-turn routing or prove a route is passable.

For the supplied custom maps, use `gaia/*.tilejson.json`: there are five per area (access, terrain, October snow, camping and historical fire). Import a definition through Gaia's custom-map workflow, or use its `tiles` URL in **Custom map layers > Explore Layer Library > Add Custom Map Source** on gaiagps.com, set zoom 8-13, preview and save, then sync the iPhone. [Official Gaia custom source instructions](https://help.gaiagps.com/hc/en-us/articles/115003639068-Adding-a-TMS-Map-Source).

The XYZ tiles are public, static files in this repository. Their zoom range is deliberately limited to the source map detail; zooming does not reveal finer surveyed data. They are complete styled map views, not transparent overlays or individual QGIS feature layers. Use the PDF legends to interpret each view. The fire view shows history; the annual model and monthly counts remain in the companion atlas. There are no tiles outside the researched coverage. Download before travel; GitHub availability and rate limits make it unsuitable as a live safety service.

Gaia does not use our QGIS project or GeoPDF as a directly imported layered map. For custom cartography, upload a supplied GeoTIFF through [Gaia's documented Mapbox Studio workflow](https://help.gaiagps.com/hc/en-us/articles/115003639948-Import-Maps-and-Data-with-Mapbox-Studio), publish the map, and connect its tile URL/TileJSON to Gaia. The supplied TIFFs are flat styled map panels, with coordinate bounds embedded; legend and safety interpretation remain in `legends-and-evidence.pdf`. They preserve the established map view, not unlimited detail. The repository also supplies ready TileJSON definitions and XYZ tiles, so Mapbox is optional. No costs or service subscriptions have been incurred. On-device custom-layer import has not been certified.

[Gaia membership guidance](https://help.gaiagps.com/hc/en-us/articles/115003524547-Membership-Options-Free-Premium-and-Premium-with-Outside): Premium is needed for offline map downloads. Complete the custom-layer download and test in airplane mode before relying on it. GPX import alone does not download a basemap.

## Geospatial PDF and QGIS

`paria-river-ranch-geopdf.qgz` retains the full editable atlas and explicitly selects each largest map as its layout reference map. The standalone project still needs the original atlas folder's datasets. The mobile ZIPs are the self-contained alternatives.

The exports use ISO 32000 geospatial `/VP` and `/Measure` dictionaries with EPSG:26912 and geographic control points. Each PDF's viewport is restricted to its actual main-map rectangle. This prevents a PDF reader from treating charts, legends and terrain cutouts as GPS map coverage. QGIS 3.22's ordinary georeference export extrapolates across the full page; `package_mobile.py` corrects the viewport and control points after export. Reproduce with the scripts rather than assuming a manual export has the same restricted viewport.

The three profile pages are charts, so they intentionally have no geospatial viewport. Colors and labels are fixed in the PDFs, not selectable thematic layers. Avenza import requires a paid tier under its current custom-import policy; file-level validation is not an Avenza device certification.

## Interpretation retained from the atlas

- Terrain colors measure terrain-cell slopes near mapped trails, not surveyed tread grade, cliff edges, footing or horse-safe thresholds.
- Snow maps are exploratory historical satellite context. Their colors are not calibrated probabilities of snow during a future October trip. Consult station notes and elevation differences in the companion pages.
- Historical fire dots and footprints, annual modeled likelihood, monthly historical counts and dated restrictions are separate concepts. Exported files do not provide live fire warnings or refreshed restrictions.
- Ownership does not alone establish camping permission. Water and trailer markers retain source-specific qualifications; do not infer usable water or turnaround dimensions from a symbol.

## Rebuild and validation

In the existing QGIS 3.22/GDAL environment, run `scripts/export_mobile.py`, `scripts/build_gaia_tiles.py`, `scripts/package_mobile.py`, then `scripts/validate_mobile.py`. The builder reads only the prior research snapshots. Validation checks geospatial corners and bounds, relocated package dependencies/themes, GPX geometry, TIFF coverage and archive integrity. Results are recorded in `mobile-validation.json`; downloadable file hashes are in `mobile-manifest.json`.
