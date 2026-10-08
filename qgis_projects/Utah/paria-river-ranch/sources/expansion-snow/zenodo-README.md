# Snow Cover Processing Workflow

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.20610474.svg)](https://doi.org/10.5281/zenodo.20610474)

This repository contains the processing workflow used to prepare monthly and long-term snow cover probability products from DLR Global SnowPack and ESA CCI snow cover data.

The workflow has three main parts:

1. processing DLR Global SnowPack daily snow cover data,
2. processing ESA CCI MODIS Terra daily snow cover data,
3. combining both products into a long-term monthly ESA CCI–DLR average snow cover product.

The final products are prepared as Byte GeoTIFFs and uploaded to `/gaia/global/snow/`.

## Repository contents

The repository includes the following notebooks:

```text
snowpack_dlr.ipynb
snowcover_esacci.ipynb
ensemble_esa_dlr_longterm.ipynb
```

### `snowpack_dlr.ipynb`

This notebook downloads and processes the DLR Global SnowPack daily snow cover extent data. It creates monthly snow probability composites from daily files and also prepares long-term monthly statistics.

### `snowcover_esacci.ipynb`

This notebook processes the ESA CCI MODIS Terra snow cover product. The ESA CCI data are daily snow cover products at 1 km spatial resolution. They are resampled to 500 m to match the DLR Global SnowPack product.

### `ensemble_esa_dlr_longterm.ipynb`

This notebook combines the long-term DLR and ESA CCI products into an ensemble average product. The ensemble uses equal weights north of 30°N. South of 30°N, the DLR product receives a 10 times smaller weight.

## Data sources

### DLR Global SnowPack

DLR Global SnowPack daily snow cover extent data were downloaded from:

https://download.geoservice.dlr.de/GSP/files/daily/

The workflow uses the historical `SCE/` data. Near-real-time data from `NRT_SCE/` can also be used when needed and available.

### ESA CCI Snow Cover

ESA CCI MODIS Terra snow cover data were downloaded from:

https://data.ceda.ac.uk/neodc/esacci/snow/data/scfg/MODIS/v4.0

This product is available as daily data at 1 km spatial resolution.

## DLR monthly processing

For the DLR product, daily snow-covered pixels are identified using the original source encoding:

```text
snow-covered pixels: values >= 64
valid snow-free land: bit 32
```

NoData, invalid, water and non-land pixels are excluded from the monthly denominator.

Monthly snow probability is calculated as:

```text
snow-covered valid days / valid daily land observations
```

The monthly DLR products are saved as Byte GeoTIFFs:

```text
0–100 = monthly snow probability in percent
255   = NoData
```

The products keep the original source grid and projection.

## ESA CCI monthly processing

The ESA CCI daily snow cover data are first resampled from 1 km to 500 m using cubic spline interpolation.

For the ESA CCI monthly products, the workflow calculates:

* mean monthly snow cover probability,
* monthly snow cover fraction based on valid snowy days, using a 10% snow threshold.

This follows the same general idea used for the DLR SnowPack monthly product.

## Long-term monthly statistics

For both DLR and ESA CCI products, long-term monthly statistics are calculated for each calendar month.

The available statistics are:

```text
p05
p50
p95
```

These products describe long-term snow cover conditions for each month from January to December.

## ESA CCI–DLR average ensemble product

The long-term DLR and ESA CCI products are merged into one ensemble average product.

The weighting is latitude-dependent:

```text
north of 30°N: equal weights for DLR and ESA CCI
south of 30°N: DLR receives a 10 times smaller weight
```

This reduces the influence of DLR Global SnowPack in lower-latitude areas.

The final ensemble products are also saved as Byte GeoTIFFs:

```text
0–100 = snow cover probability in percent
255   = NoData
```

## Output locations

The processed data and Monthly, long-term monthly and ensemble products are stored directly under:

```text
/gaia/global/snow
```

Daily DLR files are stored under:

```text
/gaia/global/snow/daily
```

## Zenodo archive

The Zenodo archive (https://doi.org/10.5281/zenodo.20610475) contains the long-term monthly ESA CCI–DLR average snow cover probability product.

Zenodo title:

```text
Long-term Monthly ESA CCI–DLR Average Snow Cover Probability, 2000–2025
```

The archive includes long-term monthly layers for each calendar month from January to December. The available statistics are:

```text
p05
p50
p95
```

The original daily DLR and ESA CCI input files are not included in the Zenodo archive.

## Software requirements

The workflow was prepared in Python notebooks and uses mainly:

```text
numpy
rasterio
xarray
rioxarray
pandas
netCDF4
concurrent.futures
```

The exact environment can be adapted depending on the server setup.

## Notes

The ESA CCI product is available from 2000 to 2023 in the downloaded source archive. The DLR Global SnowPack workflow was prepared for 2000 to 2025. For the ensemble product, the last two years use only the DLR-based long-term product because ESA CCI data are not available for those years.

## How to cite:

To cite these maps please use:

    @dataset{celik_t_2025_20610474,
        author       = {Celik, M.F. and Hengl, T.},
        title        = {{Long-term Monthly ESA CCI–DLR Average Snow Cover Probability, 2000–2025 at 500 m resolution}},
        year         = 2026,
        publisher    = {OpenGeoHub foundation},
        address      = {Doorwerth},
        version      = {v1},
        doi          = {10.5281/zenodo.20610474},
        url          = {https://doi.org/10.5281/zenodo.20610474}
    }

*Disclaimer*: Use at own risk. These are initial results with limited
accuracy and possible issues with quality of training points, location
errors and harmonization issues.

## Acknowledgments

This research was supported by multiple grants:

**[EarthMonitor.org](https://EarthMonitor.org/)** project has received
funding from the European Union’s Horizon Europe research an innovation
programme under grant agreement
**[No. 101059548](https://cordis.europa.eu/project/id/101059548)**.

**[AI4SoilHealth.eu](https://AI4SoilHealth.eu/)** project has received
funding from the European Union’s Horizon Europe research an innovation
programme under grant agreement
**[No. 101086179](https://cordis.europa.eu/project/id/101086179)**.
