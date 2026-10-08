# Source register

Retrieved October 8, 2026 UTC. All GIS features are local snapshots. Source data retain their original attribution and terms.

| Evidence | Publisher and source | Local record |
| --- | --- | --- |
| Historical route and observations | User-supplied [2008 Boundary Waters Trip KML](https://drive.google.com/file/d/1h9r2ATOb1APQxzhwQTQ-nx44N68GY1yb/view) | `sources/2008-boundary-waters.kml` |
| Shoreline polygons | [Minnesota DNR Hydrography](https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/water_dnr_hydrography/FeatureServer/1) | `sources/hydrography.geojson`; metadata, ID inventory and exact requests |
| Digital lake-depth contours | [Minnesota DNR Lake Bathymetry](https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/water_lake_bathymetry/MapServer/0) | `sources/depth-contours.geojson`; metadata, IDs and requests |
| Historical lake-depth scans | [DNR LakeFinder](https://www.dnr.state.mn.us/lakefind/index.html) | `sources/depth-manifest.json`, `sources/depth-selected-metadata.json`, original PDFs and index HTML |
| Fish surveys and stocking | [DNR LakeFinder](https://www.dnr.state.mn.us/lakefind/index.html) | `sources/fisheries.json` links each lake report, API and stocking page; original responses in `sources/fisheries-raw/` |
| Lidar-derived elevation | [MnGeo second-generation lidar](https://mn.gov/mngeo/gis-data-and-maps/info-by-topic/elevation/lidar/lidar-gen2.jsp), [image service](https://enterprise.gisdata.mn.gov/agsimg/rest/services/MnTopo/2nd_Generation_Seamless_Lidar_DEM/ImageServer) | `sources/lidar-service.json`, `sources/lidar-route-request.json`, 8m output TIFF |
| Mapped portage trails | [USFS National Forest System Trails](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0) | `sources/portage-usfs-*`; complete query, source metadata and selected trail geometry |
| Independent shoreline cross-check | [USGS hydrography](https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer) | `sources/portage-nhd-*`; supports P01 mismatch investigation |
| Wilderness boundary | [Minnesota DNR BWCA](https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/bdry_boundary_waters_canoe_area/FeatureServer/2) | `sources/wilderness.geojson`; service and request snapshots |

The statewide lidar catalog describes 2021–2024 collection; the seamless service description states 2021–2023. Exact route-tile acquisition dates were not resolved. We identify the service snapshot and distinguish its native 0.5m grid from the atlas’s 8m resampling; no per-pixel flight date or accuracy claim is made.

LakeFinder notes that not every lake has been surveyed or depth sounded, and that recent survey publication can lag. It retains copyright on its lake maps and links its General Data and Software License Agreement, particularly for commercial reuse. Original copyright text is retained in the attached full scans; cropped reference panels do not replace the originals.

No source supplies field verification of the derived landing candidates. No lake-reference coordinate is presented as an actual fisheries sampling station. No relationship between stocking and the exact locations of the historical bass observations is inferred.
