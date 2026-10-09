# Fire orders and seasonal outlook — checked October 9, 2026

The compact atlas copy is `sources/fire-orders/fire-orders.json`: four blocks per area, 167–175 body words total per sidebar, with source URLs. The date is a snapshot, not a prediction that fires will be allowed on future dates. Restrictions are issued by the land-management or legal authority; a responding fire department's service area does not establish that jurisdiction.

## Corrections that supersede earlier interpretations

**C12 in the existing camping evidence must not be read as proof of a current blanket Trust Lands campfire ban.** The [Trust Lands page](https://trustlands.utah.gov/trust-lands-and-you/) does show “OPEN CAMPFIRES PROHIBITED,” but the banner links to a [June 9, 2021 announcement](https://trustlands.utah.gov/wp-content/uploads/2021/06/Statewide-Stage-1.pdf), effective June 10, 2021. Its old general camping text also discusses fires. Neither establishes an October 2026 ban. The 2026 signed FFSL rescission below specifically includes Kane and Garfield state and unincorporated private lands. Keep checking parcel-specific conditions; this does not promise that any individual campsite permits fires. The prior snapshot was deliberately preserved.

Dixie still links regional order **04-2021-01**, but the fetched page explicitly ends July 17, 2026. It is not treated as currently effective. Likewise, old 2025 search results and third-party September 2026 Stage 1 summaries were not used to override current signed rescissions.

The official Utah registry contains a inconsistent historical record: **OBJECTID 117**, Paria Stage 2 UT-020-2026-05, reports September 28 rescission but its `Link_Rescind` downloads **Color Country UT-020-2026-09**, effective September 1. Saved as `blm-paria-stage2-rescission.pdf` to preserve the exact mistaken link; filename describes the referring record, not the PDF's real jurisdiction. Do not derive Paria's legal dates from that row. The correctly linked, directly read Paria Stage 1 rescission is unambiguous.

## Verified orders

| Authority / land | Evidence | Date and result |
|---|---|---|
| BLM Paria River District, Kane/Garfield BLM lands | [UT-020-2026-11](https://drive.google.com/file/d/1SuFoPojgHtzDsYshX1XzOWnK_LAJP7uD/view), `blm-paria-stage1-rescission.pdf` | Dated September 2; rescinds Stage 1 UT-020-2026-08 effective September 4, 2026 at 00:01. Standing prevention and other resource restrictions remain. |
| BLM Color Country District | [UT-020-2026-10](https://drive.google.com/file/d/1TH8NNVXXPLxJjPCUaCCFrfCkg6iG8kQl/view), `blm-color-country-rescission.pdf` | Dated September 2; rescinds UT-020-2026-09 and -07 effective September 4 at 00:01. Applies to its BLM lands in listed counties including Garfield. |
| Dixie National Forest | [Termination notice](https://www.fs.usda.gov/r04/dixie/alerts/dixie-national-forest-rescinds-stage-1-fire-restrictions), `dixie-rescission.pdf` | Signed August 31; terminates Stage 1 0407-26-12 effective September 2, 2026 at 00:01. Alert remains in live index. |
| Utah FFSL: state and unincorporated private lands in Beaver, Iron, Washington, Garfield and Kane | [Signed multi-area rescission package](https://drive.google.com/file/d/1lxHN-SO266CUo1aB2moMWFS1G74c3ClF/view), `ffsl-state-rescission.pdf` | Southwest page signed September 3; rescinds SWCLO2601–2605 September 4 at 00:01. Explicitly excludes private land inside incorporated towns/cities. The registry spells two order IDs SWCLOS; use PDF spelling. |
| Utah BLM lands, standing prevention | [UT914-25-001](https://www.blm.gov/sites/default/files/docs/2025-06/2025_UTSO_Fire%20Prevention%20Order.pdf), `blm-baseline.pdf` | Dated June 17, 2025; effective June 18 at 00:01 until rescinded. Prohibits explosives/devices and fireworks; not itself a general campfire ban. Live BLM index still lists it. |

The downloaded [BLM index](https://www.blm.gov/programs/fire/regional-info/utah/fire-restrictions), [Dixie alerts](https://www.fs.usda.gov/r04/dixie/alerts), and [Utah Fire Info restriction page](https://utah-fire-info-utahdnr.hub.arcgis.com/pages/ba47d998e6b04639bbf50954cf5aa8c7) contain no replacement seasonal campfire order for these riding areas on the check date. This is an index check, not a guarantee of no site-specific rule.

Utah's old `/active-fire-restriction-documents/` URL and `/pages/active-fire-restrictions` redirect or expose the home page, so the actual page item was retrieved by the official site's navigation ID `ba47d998e6b04639bbf50954cf5aa8c7`. Its data links web map `dc1ab69b0d48495d8da6534604d030d3`, whose current Fire_Restrictions service was queried with a southern-Utah envelope. The response is saved whole, including historical/superseded rows; those must not be displayed as current. It returned 49 records without transfer-limit truncation. The envelope includes extra jurisdictions for research and is not a cartographic restriction boundary.

## Jurisdiction and ownership

Existing `sources/expansion-camping/*-ownership.geojson` and ownership evidence were read without modification. They distinguish ownership and administration and do not grant permission.

- Paria River Ranch/canyon country: private ranch parcels, BLM Grand Staircase–Escalante/Paria Canyon wilderness context and state parcels. Use relevant BLM Paria River/monument contacts and parcel-specific rules. The geographical phrase “canyon country” is not BLM Canyon Country District. Paria Canyon's published permit rules independently prohibit campfires; seasonal rescission does not remove that rule.
- Mt Carmel/Bay Bill/Barracks: Kane County mosaic of BLM, state and private parcels. BLM [Barracks Kiosk](https://www.blm.gov/visit/barracks-kiosk) documents the private Barracks Ranch. BLM land uses Kanab/Paria River District authority; private/state parcels use applicable FFSL/local and owner conditions. No whole-area fire-department jurisdiction was inferred.
- Red Canyon/Losee/Casto/Thunder/Coyote Hollow/Toms Best: forest riding core is Dixie National Forest, Powell Ranger District; broader extent includes BLM, private and state parcels. The ownership source identifies Bankhead–Jones parcels as USFS-administered. Forest orders attach to National Forest System land, not the entire rectangular atlas extent.

## Current seasonal outlook verified

The direct [NIFC PDF](https://www.nifc.gov/nicc-files/predictive/outlooks/monthly_seasonal_outlook.pdf) downloaded successfully and its extracted first page reads **issued October 1, 2026**, **next issuance November 2, 2026**, covering **October 2026–January 2027**. Both PDF and extracted text are retained. The Great Basin discussion (PDF pages 10–11, one-based) specifies above-normal October potential only for the Sierra Front/Lahontan Basin; other areas and months are normal. Thus the three southern Utah atlas areas have **normal significant wildland fire potential** for this period. This regional forecast is not a daily danger rating, an individual campsite assessment, or legal permission to burn. No forecast monthly burn bans were invented.

## Preservation and limits

Raw official HTML, PDF, JSON, extraction text and retrieval headers are under `sources/fire-orders/`. A SHA-256 manifest records files. Public Drive PDFs were downloaded only from links in Utah's official registry. Direct Trust Lands HTML returned HTTP403; its page/banner destination were verified with the web tool and recorded separately. Initial un-escalated DNS failure was resolved by approved network access. No map restriction polygons were fabricated, no responding fire department was substituted for an issuing authority, and no prior sources were rewritten.
