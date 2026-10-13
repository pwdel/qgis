# Source register

## Minnesota DNR hydrography

Fresh public query acquired **2026-10-12 UTC** from [DNR hydrography FeatureServer layer 1](https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/water_dnr_hydrography/FeatureServer/1). The requested envelope is -90.42, 48.015, -89.97, 48.125 (longitude/latitude WGS84). The ID query returned 271 features; all requested IDs were fetched in batches. Preserve `sources/hydro-ids.json`, the batch responses, combined `hydrography.geojson` and `acquisition.json`. Original provider metadata is retained from the prior atlas in `hydrography-service.json`; its metadata date has not been relabeled as refreshed. Minnesota DNR attribution and applicable source terms remain in force. Small channels can be absent or disconnected in lake polygons.

## US Forest Service trails

Fresh complete envelope query acquired **2026-10-12 UTC**, 145 features, with no transfer-limit flag. [USFS National Forest System Trails layer](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0). Raw attributes and geometry: `sources/usfs-trails.json`; full recipe/time: `sources/acquisition.json`. The selected derivative preserves the current object IDs. Prior-atlas layer metadata remains available separately. USFS public GIS data are not field certification or guarantees of access/current conditions.

## Minnesota lidar

Reused `lidar-route-8m.tif` from the existing Boundary Waters atlas; its saved download response and service metadata accompany it. [MnTopo second-generation seamless lidar DEM](https://enterprise.gisdata.mn.gov/agsimg/rest/services/MnTopo/2nd_Generation_Seamless_Lidar_DEM/ImageServer). The source service reports 0.5 m native pixels; the existing raster is an **8 m bilinear resampling**, not new 0.5 m data. Original snapshot belongs to the atlas reviewed 2026-10-08; the exact retrieval timestamp is not established by the saved request. No fresh acquisition date is invented. Vertical datum/absolute accuracy are not established here. Missing or out-of-range cells are excluded. Bare-earth elevation omits tree canopy. Source terms and attribution are retained in `sources/lidar-service.json`.

## Published loop sketch and local observations

[Friends of the Boundary Waters: Pike and Pine Lake Loop](https://www.friends-bwca.org/route/pike-and-pine-lake-loop/) and its [GPX](https://www.friends-bwca.org/wp-content/uploads/ClearwaterPikePineLakes_4Day_Entry62.gpx), accessed **2026-10-12**. The GPX calls itself **Digitized in QGIS**, so it is treated as a published sketch, never a GPS survey. Original saved as `sources/published-loop.gpx`. Used to cross-check passage sectors, recover approximate carries absent from USFS geometry and anchor a hypothetical starting area. The publisher's prose is attributed to Dan Pauly's 2004 guide; website/GPX reuse terms were not separately established. Retention here is for this personal research experiment, not a claim of an open redistribution licence. Do not assume the entire project bundle is licensed for public redistribution.

[Clearwater Historic Lodge: canoe day trips](https://clearwaterhistoriclodge.com/gunflint-trail-activities/canoe-day-trips-2/), reviewed 2026-10-12, independently describes Clearwater–Caribou–Little Caribou–Pine connections. No names or heights from its Palisades description were assigned to derived peaks without matching coordinates.

[USFS BWCAW Trip Planning Guide](https://www.fs.usda.gov/sites/nfs/files/r09/superior/publication/USFS%20BWCAW%20Trip%20Planning%20Guide%202023.pdf) corroborates access to John through Little John and Pine through McFarland. [BWCAWild McFarland observations](https://bwcawild.com/BWCA-Lakes/Gunflint-District/McFarland-Lake/McFarland-Lake.html) show the river/bridge connection to Little John. These support transition classification, not a claim that the water connection is always passable.

## Magnetic field

[BGS WMM2025 calculator](https://geomag.bgs.ac.uk/data_service/models_compass/wmm_calc.html), jointly developed World Magnetic Model by BGS and NOAA/NCEI. Public model query for latitude 48.07, longitude -90.20, date 2026-10-12, altitude 0.5 km above the WGS84 ellipsoid; raw response, query URL and retrieval time saved in `sources/magnetic-model.json`. Declination -2.912 degrees east = 2.912 degrees west. Acknowledge BGS/NOAA; [BGS terms](https://www.bgs.ac.uk/legal-and-policy/terms-of-use/). This is a dated centre reference for the exercise.

## Derived work

`derived/` contains projected, attributed teaching geometry in EPSG:26915. New high-point IDs are neutral identifiers, not invented place names. Coordinate transformation uncertainty is distinct from survey/source uncertainty. Hachures, shore accents, clue polygons and route choices are generated teaching/cartographic work. Clue geometry is deliberately vague; this must not be confused with the geometry confidence of the hidden sources.
