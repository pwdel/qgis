# Delivery verification — 12 October 2026

- Six timing unit checks passed, including an independently calculated 1 km double carry, detour allowance, invalid distances, outward rounding and changed input assumptions.
- 492 native project, geometry and arithmetic checks passed: both saved schematic formats, geographic companion, explicit local engineering CRS, real UTM evidence, local relative dependencies, raw itinerary sums, lake containment and modeled shoreline extensions.
- Relocated the project and local data to a temporary directory and successfully reopened and re-exported the chart without network access.
- Inspected the 17 × 11 inch chart and all three instructor pages rendered by Poppler. Corrected Clearwater callout and hill/carry collisions; all 17 lakes, 18 passage labels and 33 crossing-pair labels are present. The shared West Pike landing is labeled explicitly.
- Apple PDFKit opened and rendered the final chart (one page) and instructor key (three pages). PDFs were assembled with complete document structures using pypdf.
- A separate read-only reviewer verified route continuity and timing sums. Corrected assumptions handling, standalone local CRS storage, bundled-input rebuilding and separate modeled shore-extension geometry. Printed assumptions now use the same configuration snapshot as the tables.

This verifies the saved files and modeled geometry, not present trail conditions, canopy visibility, or actual journey duration. Desktop QGIS was not manually inspected in this turn; native offscreen QGIS 4.2.3 performed reopen and export checks.
