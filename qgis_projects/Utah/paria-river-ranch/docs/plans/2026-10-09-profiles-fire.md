# Trail profiles and wildfire expansion implementation plan

Approved by the user October 9, 2026 after review of the six-page design.

**Goal:** Add a trail-profile and wildfire page to each detailed area, yielding 19 pages.
**Architecture:** Preserve the existing 13-page edition. Separate profile analysis, fire history data, and dated legal/outlook evidence; integrate six new editable QGIS layouts and an ordered PDF. Reuse existing page dimensions, typography and local source architecture.
**Tech stack:** QGIS, GDAL, Python, Matplotlib, pypdf, Poppler.

## Constraints
- X = miles traveled; Y = elevation relative to marked start in feet; ascent/descent totals separate.
- Disconnected routes and missing elevations are never bridged. Name map-clipped segments explicitly.
- Verified lidar and service DEMs are distinguished, including sampling and smoothing methods.
- Annual modeled burn probability is not an October probability; monthly incident counts are history, not forecasts.
- Restriction status requires dated orders and issuer; missing/revoked/expired status stays explicit.
- All public source URLs, retrieval dates, source snapshots and derivations remain reproducible.
- Preserve original and 13-page assets. Avenza remains second pass.

## Tasks
- [x] Profile analysis: inspect route inventory, sample elevation, calculate noise-aware ascent/descent, save route/sample data and page-ready SVGs. Test known ascent/descent and no-data gaps.
- [x] Fire data: collect complete local historical perimeters and incident records, source period and monthly counts; obtain annual burn-probability subsets when available with native units documented.
- [x] Fire authority: archive dated official restrictions and latest verifiable outlook, distinguish state/county/private/federal jurisdiction and restriction issuer from response agency.
- [x] Integration: scripts/build_profiles_fire_atlas.py reads prior expanded QGIS project; adds six layouts using new data, clones old layouts with updated page numbering, exports 19 individual pages and combined PDF, writes paria-river-ranch-riding-atlas.qgz.
- [x] Verification: validate 19 PDF pages, boxes, source links, missing text, QGIS relative paths and valid layers; inspect all six new pages at full resolution and a full-atlas contact sheet; verify unchanged old artifacts.
- [ ] Publication: update README, source/governance records and project metadata, commit only atlas changes, fetch and safely integrate public main, publish and verify remote hash.
