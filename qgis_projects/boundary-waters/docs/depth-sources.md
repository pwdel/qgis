# Minnesota DNR historical lake depth scans

Downloaded 2026-10-08 UTC from Minnesota DNR LakeFinder. `sources/depth-manifest.json` records index pages, direct PDF URLs, lake IDs, local originals, and file sizes. DNR maps retain their original copyright. The LakeFinder page links the DNR General Data and Software License Agreement for commercial use.

Twelve route lakes have scanned depth maps. Watap (16013800) lists no bathymetric map; downloaded legend files are not lake-specific maps. No depth coverage is claimed for Watap.

`derived/depth-panels.json` identifies 12 cropped depth inset images. The source scans were rendered at 300 dpi, exterior white margins trimmed, and hand-selected rectangles extracted. Mountain and Clearwater were rotated 90 degrees counterclockwise so map text reads upright. Source contour lines, values, and scan imperfections were preserved. Original whole sheets remain in `sources/depth-scans/`; whole-sheet raster copies remain in `derived/depth-scans/`.

These are independent historical reference panels, **not georeferenced rasters**. Do not load them as positioned overlays or infer coordinates from their pixel dimensions. Cropping removes some original scales and titles; panel size is not a navigation scale. Caption each with its lake name, “Historic MN DNR depth scan; depths in feet” and make originals available for full labels and metadata. Contour intervals vary; use the per-lake manifest only where explicitly identified, otherwise refer to original contour labels. Depth soundings and shoreline surveys can be many decades old.

Rove shows the Canadian boundary and does not imply complete Canadian bathymetric coverage. Rose continues beyond the left edge of the source sheet; the crop preserves that source limitation. Caribou has a heavy vertical artifact present in the original scan. West/East Pike and some long lake panels cannot have every small number legible at four-inch printed width; full PDFs retain the original detail.

Reproduction: run `scripts/depth-download.py` with network access; run `scripts/depth-render.py` and `scripts/depth-panels.py` with a Python environment containing Pillow and `pdftoppm` on PATH. The bundled Codex dependency Python supplies Pillow. `derived/depth-panels/contact-sheet.jpg` is a visual QA index.

## Selection and identity review

Every selected original title was visually checked against its lake-specific DNR index. Hungry Jack C0279 is genuinely Hungry Jack (printed 16-227), but its combined contour/substrate hatching obscures depth lines. The final inset uses cleaner B0532, fieldwork 1986, drawn 1987. East Pike B0412 explicitly identifies East Pike 16-42, with 1971 fieldwork; its broad 40-foot basin and northeast-pointing north arrow account for the sparse central contours and differing orientation. `sources/depth-selected-metadata.json` records exact source URLs, title captions, survey years, and dates. Unknown survey dates remain null rather than being inferred from the 1993 copyright stamp. Rose survey is CCC 1935 (drawing date1954); Hungry Jack1986; Rove/Mountain/West Pike/Caribou/Little Caribou1939; East Pike1971; Pine1957. Moss, Duncan, and Clearwater dates are not explicit on the selected sheet.
