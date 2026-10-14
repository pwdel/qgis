# Expanded maps to share

Three ZIP downloads, each with five individual GeoPDF maps, separate GeoJSON layers, source notes, and the original atlas/profile reference pages:

- [Paria River Ranch](https://raw.githubusercontent.com/pwdel/qgis/main/qgis_projects/Utah/paria-river-ranch/output/pdf/wide/ranch-share.zip)
- [Mount Carmel](https://raw.githubusercontent.com/pwdel/qgis/main/qgis_projects/Utah/paria-river-ranch/output/pdf/wide/mount-carmel-share.zip)
- [Red Canyon](https://raw.githubusercontent.com/pwdel/qgis/main/qgis_projects/Utah/paria-river-ranch/output/pdf/wide/red-canyon-share.zip)

Unzip in Files. Import the individual `*-wide.pdf` maps into a compatible GeoPDF app. Each PDF is a single styled map: access, terrain, October snow, camping/ownership, or wildfire history. GeoJSON files are separate vector datasets and do not reproduce the raster imagery or PDF styling. Actual iPhone import and live GPS operation remain untested.

The same centers are retained. Width AND height increased 1.5 times, for 2.25 times the original area. Ranch width is 49.5 km; Mount Carmel 24 km; Red Canyon 33 km. The new QGIS project is `paria-river-ranch-wide.qgz`; retain the repository's relative source/derived directories when opening it.

Official USGS topo and elevation imagery, SGID trails/roads, Utah ownership, FPA FOD incidents and MTBS perimeters were downloaded for the expanded extent on October 14, 2026. Request parameters, IDs and complete-count evidence are saved under `sources/wide/`. The regional satellite snow raster already covers the new extents. Expanded terrain screening uses service elevation sampled at approximately 15 m (ranch), 10 m (Mount Carmel), and 10 m (Red Canyon). It is not full-extent native lidar, surveyed cliff height, or trail grade. The separate native 1 m Thunder Mountain overlay remains a small original crop.

The source GeoPackage CRS was restored for project layers with missing CRS declarations before exporting longitude/latitude GeoJSON. All clipped feature geometry is checked for validity. Attributes preserve the original source fields and add `atlas_source`, `atlas_input`, and limitations. Source geometry repair counts and layer inventories are in `wide-manifest.json`.

The companion atlas and profile sheets retain their original extents and research dates. Their fire counts and charts must not be treated as counts for the wider maps. Water remains unverified for the actual trip; ownership does not grant camping permission; road classes do not establish trailer clearance. Snow context is exploratory, and fire history is not a forecast. Check current restrictions with the governing land manager before travel. See [governance](GOVERNANCE.md) and [riding sources](RIDING-SOURCES.md).

Rebuild in the project's QGIS 3.22/GDAL environment: `scripts/fetch_wide.py`, `scripts/export_wide.py`, then `scripts/validate_wide.py`. The exporter sets an ISO 32000 geospatial viewport only on the actual map frame. Independent GDAL checks compare PDF neatlines to the requested UTM extents, rather than relying only on the PDF metadata writer.
