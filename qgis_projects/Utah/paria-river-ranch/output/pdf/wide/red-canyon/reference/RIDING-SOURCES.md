# Riding edition: profiles and wildfire source key

Research snapshot: **October 9, 2026**. The 19-page PDF adds six sheets to the earlier atlas. Earlier access, terrain, snow and camping pages retain their original research dates; their evidence remains in [SOURCES.md](SOURCES.md) and [EXPANSION-SOURCES.md](EXPANSION-SOURCES.md). This key is the clickable source target on every riding-edition page.

## P01 — Modeled route elevation profiles

Trail geometry comes from the archived [Utah SGID trails](../sources/state-trails.geojson) and [USFS trails](../sources/usfs-trails.geojson). State `HorseAllowed=Yes` is published mapping, not current permission. Conflicting hiking-only classifications remain visible. Profiles retain original feature identifiers and disconnected components.

USGS 3DEP service DEMs supply terrain elevations: approximately15m output cells in the ranch area,10m at Mount Carmel and13.75m at Red Canyon. These are service mosaics whose pixel-level native provenance is unresolved; they are **not represented as complete verified 1m lidar coverage**. The earlier verified Thunder Mountain1m crop covers only part of the area and is not silently mixed into route profiles. Requests and source TIFFs remain archived in `sources/`.

The Y axis shows feet above/below a marked start. Total ascent and descent are separately derived after documented sampling and noise treatment. Profiles do not survey the trail tread or resolve narrow benches, overhangs, exact cliff edges, erosion, footing or horse safety. A route clipped at a map boundary is a section, not a complete ride. Disconnected components cannot be added to fabricate an itinerary.

See [profile methods](profile-methods.md), [profile data](../derived/profiles/) and [source inventory](../sources/profiles/) for route completeness, component directions, elevation samples and analysis details.

## F01 — Historical large-fire footprints

[Monitoring Trends in Burn Severity](https://www.mtbs.gov/) is an interagency USGS/USFS program with records beginning1984. Its western-US inventory generally targets fires of at least1,000 acres, including wildfires and prescribed fires. A map without a perimeter does not establish absence of historical fire. Boundaries represent mapped burned extent rather than an inventory of all small incidents or present closures.

The exact service, query parameters, source fields, feature IDs, count checks and downloaded snapshots are archived in [fire-data sources](../sources/fire-data/). The map differentiates fire types and labels footprint year/name where present. Geographic counts refer to the exact detailed-sheet rectangle, including intersecting footprints that extend outside it. [MTBS coverage and methods](https://www.mtbs.gov/faq/fire-mapping).

## F02 — Monthly historical fire activity

The [USFS FPA FOD current-edition service](https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrenceCurrentEdition_01/MapServer) provides the seventh edition,1992–2024. Monthly charts count reported incidents by **discovery month** within each exact detailed-sheet rectangle. They do not count the number of days burning, the month of all burned acreage, or the probability a rider will encounter fire. Discovery points are approximate; a dot is not a surveyed ignition location.

October is highlighted without turning its fraction of historical records into trip odds. Record reporting and location quality vary. Zero records are not zero risk. Preserve source FOD identifiers, all downloaded candidates, exact spatial-selection results, unknown dates and the record period. See [fire-data methods](fire-data-methods.md) and [computed summaries](../derived/fire-data/fire-summary.json).

## F03 — Annual modeled fire likelihood

[Wildfire Risk to Communities](https://wildfirerisk.org/understand-risk/) describes annual burn likelihood derived from many simulated fire seasons. Its annual model does not forecast October weather or current daily danger. WRC2024 uses a landscape updated through2020; published30m visualization cells do not create30m independent native model precision.

The available [official ImageServer](https://imagery.geoplatform.gov/iipp/rest/services/Fire_Aviation/USFS_EDW_RMRS_WRC_BurnProbability/ImageServer) states that its values were altered for visualization. The inset therefore preserves the official rendering and is labeled **relative annual likelihood**. No conversion of those display values into a numerical annual or October probability is asserted. Original service metadata, legend and raster requests are archived. The underlying numerical Utah archive was not substituted with guessed percentages.

## F04 — October2026 seasonal outlook

The [NIFC National Significant Wildland Fire Potential Outlook](https://www.nifc.gov/nicc-files/predictive/outlooks/monthly_seasonal_outlook.pdf), directly retrieved and checked, was issued **October1,2026**, covering October2026–January2027; next issue scheduled November2. Its Great Basin discussion places southern Utah in normal significant fire potential during this period. Normal is relative to seasonal expectations, not an absence of fire, a daily weather forecast or campfire permission.

The [archived PDF](../sources/fire-orders/nifc-monthly-seasonal-outlook.pdf) preserves the actual edition used. Do not rely on the live URL retaining this edition. Seasonal outlook categories cannot be translated into a local percentage without an appropriate calibrated model.

## F05 — Governing authorities, restrictions and rescissions

The [dated restriction register](../sources/fire-orders/fire-orders.json), [research notes](fire-orders-research.md) and [archived evidence](../sources/fire-orders/) preserve signed orders and source conflicts. Utah FFSL is the Utah Division of Forestry, Fire and State Lands. Federal land managers issue federal-land restrictions; state, county, municipal and landowner requirements can apply to other parcels. A responding fire department's service area is not automatically a restriction or ownership boundary.

- **Ranch / Mount Carmel:** BLM Paria River District Stage1 order UT-020-2026-08 was rescinded effective September4 by UT-020-2026-11. Utah lifted Stage1 restrictions on Kane County state/unincorporated-private lands September4. Paria Canyon wilderness has a separate standing campfire prohibition. Private property requires its owner's conditions.
- **Red Canyon:** Dixie National Forest terminated Stage1 order0407-26-12 effective September2. Garfield County state/unincorporated-private and BLM Color Country Stage1 restrictions ended September4. Other resource closures, campground requirements and owner conditions still apply.
- Checked indexes listed no replacement seasonal restriction for these riding areas as of the research date. This is a dated search result, not a promise of unrestricted burning. Future monthly restrictions are unknown; they change by order and conditions rather than a fixed calendar.

Official recheck sources: [BLM Utah](https://www.blm.gov/programs/fire/regional-info/utah/fire-restrictions), [Dixie alerts](https://www.fs.usda.gov/r04/dixie/alerts), [Utah Fire Info](https://utah-fire-info-utahdnr.hub.arcgis.com/pages/ba47d998e6b04639bbf50954cf5aa8c7), [Trust Lands](https://trustlands.utah.gov/trust-lands-and-you/). Signed rescissions are linked in the register, including the original official-index Google Drive document links. These are evidence links, not private uploads.

### Correction to earlier C12 interpretation

The Trust Lands website's open-campfire banner points to a June2021 notice. That banner does **not** establish an October2026 blanket ban. This correction supersedes that interpretation in the earlier C12 camping evidence; the original snapshot is preserved for audit. The signed2026 state rescission and parcel-specific conditions must be checked instead.

An additional Utah registry row labeled Paria Stage2 has inconsistent date/link information: its PDF belongs to Color Country. That row was not used to date Paria's Stage1 rescission. A Forest Service regional order still linked from alerts also states an expiry of July17,2026; being linked does not make an expired order current.

## Reproduction and release checks

Run `scripts/trail_profiles.py`, `scripts/fetch_fire_data.py` and then `scripts/build_profiles_fire_atlas.py` in the documented GIS environment. Fire-order legal interpretation is a dated reviewed snapshot and must be researched anew before updating its status. Layout-ready sidebar text is preserved in `derived/riding/layout-data.json`.

Run `scripts/test_trail_profiles.py` and `scripts/validate_riding_atlas.py`; inspect rendered PDFs as recorded in [visual review](riding-visual-review.md). [Validation](riding-validation.json) and [manifest](riding-manifest.json) record preservation, output and portability checks. The first and expanded editions are retained. The PDF is not yet Avenza-georeferenced or field-certified.
