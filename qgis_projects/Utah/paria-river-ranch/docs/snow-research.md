# Snow data acquired for the expanded Utah riding atlas

## Deliverables and integration

All paths below are relative to this project. `sources/expansion-snow/snow-climatology.json` contains nine NOAA stations, coordinates, elevations in metres/feet, twelve monthly snowfall normals, twelve snow-depth day frequencies, twelve midmonth daily probabilities, per-variable years and flags, and original download URLs. `snow-stations.geojson` is ready for QGIS point mapping (WGS84). All original monthly/daily CSVs are archived. `scripts/expansion_snow.py` rebuilds JSON/GeoJSON from them and checks nine stations × twelve months and probability bounds. `manifest.json` records hashes.

`sources/expansion-snow/snowcover-ensemble-p50-01.tif` through `-12.tif` provide exploratory spatial context for all three map areas. WGS84 regional clip: west −112.95, east −111.4, south 36.75, north 38.0. All are 372 × 300, 1/240° cells, percent values 0–100, NoData 255. Preserve those cells; no additional smoothing or elevation interpolation. `gridded-snow-metadata.json` contains the exact semantics, limitations, license, source links, monthly min/max and retrieval method.

Use the raster map title **Typical monthly snow cover — satellite ensemble (%)**. Label its legend **Exploratory p50 ensemble; not snow depth or a forecast**. Use a regional station locator/table when station points lie outside an individual riding map: do not move stations onto the route or assign their values to an entire area. Terrain elevation can explain context but must not be colored as invented snow probability.

## NOAA definitions and completeness

Sources: [monthly CSV documentation](https://www.ncei.noaa.gov/data/normals-monthly/1991-2020/doc/Normals_MLY_Documentation_1991-2020.pdf), [daily CSV documentation](https://www.ncei.noaa.gov/data/normals-daily/1991-2020/doc/Normals_DLY_Documentation_1991-2020.pdf), [flags/readme](https://www.ncei.noaa.gov/data/normals-monthly/1991-2020/doc/Readme_By-Variable_By-Station_Normals_Files.txt). These documents are archived beside the data.

* `MLY-SNOW-NORMAL`: normal monthly new snowfall, inches. Snowfall is not standing depth.
* `MLY-SNWD-AVGNDS-GE001WI`: mean number of days in a month with snow depth at least one inch. Our derived monthly station day frequency is 100 × that number / average calendar month length during 1991–2020. February uses 28 + 8/30 days. NOAA rounded the original day normals to tenths, so display derived frequency to one decimal, not three.
* `DLY-SNWD-PCTALL-GE001WI` on each month's 15th: NOAA historical percent probability using a centered 29-day window and smoothing. This is NOT the chance of encountering snow at any time in a 29-day stay. Preserve this separately from the monthly frequency.
* Period is the 1991–2020 normals product; actual valid contributing years differ by station, month and variable. S means standard, at least 24 years; P means provisional, at least 10 years with gaps unfilled. R and E definitions are included in JSON. Missing is null, never zero. Flag X is a nonzero value rounded to zero.

October checks from original CSVs:

| Station | Elevation ft | New snow in | Depth ≥1 in: days | Derived day % |
|---|---:|---:|---:|---:|
| Kanab | 4,900 | 0.2 | 0.0 | 0.0 |
| Alton | 7,098 | 2.0 | 0.6 | 1.9 |
| Bryce Canyon NP HQ | 7,890 | 3.0 | 1.1 | 3.5 |
| Kodachrome Basin | 5,805 | 0.2 | 0.0 | 0.0 |
| Escalante | 5,810 | 0.1 | 0.0 | 0.0 |
| Panguitch | 6,647 | 0.2 | missing | missing |

Page and Lees Ferry add low-elevation context. Lees Ferry has no depth normals; Bryce airport has neither snowfall nor depth normals. Keep Bryce airport only if showing missing-data coverage; never silently replace it with the higher Bryce NP station. Rounded zero is not a guarantee of no snow. Stations describe their particular exposure and observation site, not route segments. Snow days are dependent because snow persists; do not multiply independent-day probabilities into a trip probability.

## Spatial raster provenance and limits

[Çelik and Hengl / OpenGeoHub dataset](https://doi.org/10.5281/zenodo.20610475), published 9 June 2026, CC BY 4.0. All twelve p50 layers were acquired with GDAL HTTP range reads, avoiding full global downloads. Citation must credit the derived dataset plus [DLR Global SnowPack](https://download.geoservice.dlr.de/GSP/files/daily/) and [ESA CCI MODIS snow](https://data.ceda.ac.uk/neodc/esacci/snow/data/scfg/MODIS/v4.0). Archived Zenodo API response supplies checksums/file URLs; archived [source notebooks and README](https://codeberg.org/openlandmap/snow_cover) supply processing evidence.

At Utah latitude the code averages the two sources' long-term monthly medians equally where both are valid; where only one is valid it uses that source. The product is not a median of combined annual data or a pooled observed-day probability. DLR computes snow-covered days / valid land-observation days; invalid/water observations are excluded. ESA source resolution is 1 km, resampled to the nominal 500 m output. The published period is 2000–2025, but the source README and notebook identify ESA inputs through 2023; DLR runs through 2025.

The publisher describes ESA snow-day frequency with a 10% snow-cover threshold. Its notebook computes both mean daily fractional cover and thresholded snow-day frequency but does not include the subsequent ESA long-term quantile step. Therefore the exact ESA variant cannot be independently reproduced from the archived code. Avoid a stronger “percentage of calendar days” claim for the combined map. This is a real published raster, but initial and not locally validated. The README acknowledges limited accuracy and harmonization/location issues. Per-pixel valid-year counts are not provided. Values include small nonzero summer areas, which should not be presented as verified lingering summer snow. A zero median can coexist with occasional snowy years. There is no physical depth threshold and no inference of trail safety.

All raster checks passed: native WGS84 bounds align, 372 × 300 pixels each, NoData=255, all valid values bounded 0–100. October regional range is 0–26. Native GDAL emitted a missing proj.db lookup warning, but there was no reprojection; outputs retain the correct WGS84 coordinate definition, exact source grid spacing and requested geographic extent. Integrators may explicitly set EPSG:4326 when loading if needed.

## Alternatives reviewed

[NOAA/NSIDC SNODAS](https://www.drought.gov/data-maps-tools/snodas-gridded-snow-depth-us) supplies modeled daily 1 km snow depth since October 2003. Full national daily downloads were not acquired. [DEVISE](https://devise.uwyo.edu/devise-documentation/SNODAS.html) exposes derived SNODAS products, but its `snowcover` metric means days with depth greater than 15 inches (38 cm), not generic snow on ground; it cannot substitute for a one-inch snow-day map. Monthly mean/max depth is not a frequency. Station normals remain the stronger directly defined depth-frequency evidence.

## ENSO footnote for atlas

El Niño and La Niña can shift broad seasonal precipitation patterns, but Utah impacts are inconsistent and neither phase reliably predicts October snow on an individual route. These historical layers combine ENSO phases and are not forecasts. See the [NOAA Utah State Climate Summary](https://statesummaries.ncics.org/chapter/ut/) and [NWS ENSO guidance](https://www.weather.gov/twc/enso). Do not apply unsupported El Niño/La Niña multipliers to either station or raster values.
