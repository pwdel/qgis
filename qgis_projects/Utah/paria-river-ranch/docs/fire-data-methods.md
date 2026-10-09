# Fire data methods and integration

Retrieved 2026-10-09. Reproduce with `python3 scripts/fetch_fire_data.py` in a runtime with requests and GDAL. This run used `savage-fen-qgis-build`, isolated under `/tmp/utah-firedata`.

## Occurrence and seasonality

Authoritative [USFS current-edition FPA FOD service](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrenceCurrentEdition_01/MapServer/0), seventh edition FPA_FOD_20260615, covers 1992–2024. Version-specific citation: [Short, spatial wildfire occurrence data, seventh edition](https://doi.org/10.2737/RDS-2013-0009.7). Full service and layer snapshots are in `sources/fire-data/` because this stable URL can later change editions.

Each query intersects the exact editorial map rectangle in EPSG:26912. Returned object IDs are compared with a separate count query, fetched in batches of 100 with all fields, and checked for exact ID equality and no transfer-limit flag. The ArcGIS server returns candidates against a projected envelope; some fall outside the exact UTM rectangle. All candidate features are preserved in source GeoJSON. Candidate geographic geometries are independently transformed into EPSG:26912 and filtered to intersect the exact rectangle. Geographic-check JSON records selected counts and excluded candidate IDs. Download completeness therefore applies to the candidate set; delivered analytical layers contain the exact selection. Zero records are valid results, not evidence of no historical fire.

Month comes from the discovery date, read in UTC to preserve the source calendar date. Counts combine all 33 years; they are counts of reported discoveries within each map, not burned acres, ignition rates, monthly burn probabilities, forecasts, or measures of reporting completeness. Missing discovery dates are counted separately. October's share divides October discoveries by discoveries with a known month. It is not the probability of a fire during an October visit. FPA FOD combines federal/state/local reports and is screened and deduplicated by the publisher; spatial, temporal, reporting and source-system biases remain. Points do not represent complete burned footprints.

Results: ranch 292 records (October 11); Mount Carmel 143 (October 6); Red Canyon 64 (October 0). Each monthly SVG is 900×240 and explicitly labels the period, sample size and interpretation. Chart bars sum to the known-month sample.

## Historical burned-area boundaries

[USFS MTBS all-year boundaries, layer 63](https://apps.fs.usda.gov/ArcX/rest/services/EDW/EDW_MTBS_01/MapServer/63). Queries use the same checked workflow and retain complete intersecting polygons, including portions beyond the map. The publisher maps documented large fires greater than 1,000 acres in the western US and greater than 500 acres in the eastern US, beginning in 1984. This is not a census of every small fire. Both wildfire and prescribed fire may occur in the source: use `fire_type` to distinguish them; never label all MTBS records as wildfire. These three extents return only `Wildfire`: ranch 2 (1998, 2020), Mount Carmel 0, Red Canyon 1 (2002).

The service-wide min/max query returned 1984–2026, saved in `mtbs-period.json`. This establishes available years, not completeness through 2026. Do not imply the current year is complete. An empty map means no qualifying intersecting perimeter returned by this service; it does not imply no fire history or future hazard. Historic boundaries are not current active incidents or closures.

## Annual burn likelihood

The endpoint was discovered through the [official WRC data viewer](https://experience.arcgis.com/experience/78e7e78bcef64dfc98cf13e2e0eae156), web map `43fc7ec110b0401c8218502512e43045`:
[USFS WRC BurnProbability ImageServer](https://imagery.geoplatform.gov/iipp/rest/services/Fire_Aviation/USFS_EDW_RMRS_WRC_BurnProbability/ImageServer).

This is the WRC 2024 second edition, using burn-probability landscape conditions at the end of 2020, FSim originally modeled at 270 m then upsampled to 30 m. A 30 m display pixel is not 30 m model precision. The service explicitly warns that pixel values were altered for web visualization and recommends original data for quantitative analysis. The original [Research Data Archive](https://doi.org/10.2737/RDS-2020-0016-2) Utah download is 6.39 GB; its catalog and metadata are preserved. The unaltered quantitative source was not downloaded, so numeric annual burn probability remains **unknown** in this deliverable.

Two TIFF products are retained per map: `annual-likelihood-visualization.tif` contains raw altered service values (do not interpret these numbers as probabilities), while `annual-likelihood-rendered.tif` uses the official `BurnProbability2024` PNG32 export and RGBA colors, translated into a GeoTIFF using the service response extent. Use the rendered version for maps. The complete official legend including labels and PNG swatches is `sources/fire-data/wrc-legend.json`; labels are source display classes, not independently verified numeric estimates. Export parameters and replies are preserved. Export requests use the exact EPSG:26912 bounds, approximately 30 m cells, and nearest-neighbor sampling; the service can adjust bounds slightly to preserve square output cells, and returned bounds are retained. No extra inference or monthly disaggregation is performed.

Recommended map title: **Modeled annual burn likelihood — WRC 2024 visualization**. Caption: **Annual model, end-2020 landscape; source display classes. Not an October forecast. Numeric local probability unverified.** Do not multiply annual likelihood by October occurrence share, and do not derive a trip-specific probability. Annual burn likelihood is distinct from historical perimeters and the monthly discovery histogram.

## `derived/fire-data/fire-summary.json` schema v1

Top level: `schema_version`, `retrieved_utc`, `occurrence_edition`, `sample_period` (inclusive years), `mtbs_period_evidence`, and `areas` keyed by `02-ranch`, `03-mount-carmel`, `04-red-canyon`.

Each area contains the exact `extent`, `occurrence_count`, `sample_period`, `observed_year_range` (actual earliest/latest observation), `monthly_counts` (12 integers, Jan–Dec), `unknown_month_count`, `october_count`, `october_share_of_known_months`, `perimeter_count`, `perimeter_type_counts`, `perimeter_years`, and project-relative `occurrences`, `perimeters`, `monthly_chart` paths.

`annual_burn_probability` contains `status: unknown_numeric_probability`, `source`, `edition`, `landscape_vintage`, `native_model_resolution_m`, `published_cell_m`, null `monthly_probability`/`october_probability`, explicit `limitation`, `visualization_available`, raw display-value range, `nodata`, CRS WKT, geotransform, dimensions and project-relative `raster`. On successful official RGB export it adds `rendered_raster` and `rendered_bands`; any unavailable export has an explicit error. A null/unknown probability must never become zero.
