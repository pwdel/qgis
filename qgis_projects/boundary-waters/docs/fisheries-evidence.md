# Fisheries evidence

The machine-readable source is `sources/fisheries.json`; raw DNR JSON and HTML snapshots are in `sources/fisheries-raw/`. Each row identifies a Minnesota DNR lake ID, the latest returned Standard Survey with positive fish catches, survey date, all caught species, the DNR game-fish subset, maximum depth in feet, and the current stocking report. The script `sources/fisheries-build.py` rebuilds the summary from snapshots.

These are lake-wide observations, not sampled coordinates or fishing hotspots. Metadata points are lake reference points and must not be styled as survey stations. No sub-lake sampling locations are supplied. A species missing from a particular survey is not necessarily absent from the lake.

Many lakes have newer targeted temperature/oxygen surveys without fish catches. Their dates are not substituted for fish survey dates. Fish-catch evidence is particularly old on Rose (1987), Rove and Watap (1991), Little Caribou (1996), Caribou (2000), and East Pike (2002). The atlas must retain those dates.

Stocking records are a distinct evidence type. The current DNR report explicitly covers the last ten years. Hungry Jack reports walleye fingerlings in 2017, 2019, 2022, 2023 and 2025. Pine reports lake trout yearlings in 2016, 2019 and 2022. The other eleven reports state no stocking data over the last ten years. That is not evidence of never being stocked. For example, Rose's 1987 survey narrative refers to 1984 lake trout stocking, outside the current stocking-report window.

The route-lake candidate set includes Moss and Little Caribou pending the atlas route geometry interpretation. Caribou is DNR 16014100, not the other Cook County lakes with that name. Pine is DNR 16004100.

Official entry points:
- https://www.dnr.state.mn.us/lakefind/index.html
- https://maps.dnr.state.mn.us/cgi-bin/lakefinder/search.cgi?context=desktop&county=16&name=
- Survey API: https://maps.dnr.state.mn.us/cgi-bin/lakefinder/detail.cgi?type=lake_survey&id=16023000 (replace lake ID).
- Public survey and stocking report URLs are retained on every JSON row.

Files were retrieved 2026-10-08 UTC. Records are current downloads of historical surveys, not reconstructed conditions in 2008.
