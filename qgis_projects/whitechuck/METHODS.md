# Methods and limitations

## Coordinates and original model
The point subset uses NAD83(CORS96) / UTM zone 10N, meters, with NAVD88 elevations using GEOID18, meters, as declared by NOAA and the file header. GPX/GeoJSON routes use longitude/latitude. Pins are approximate references, not survey controls.

The original one-meter surface averages only class-2 ground returns per cell. Empty cells use the nearest occupied cell only within two meters; larger gaps remain nodata. Slope uses finite differences; hillshade uses azimuth 315 degrees and altitude 45 degrees. The original hillshade substitutes median elevation at nodata during shading; do not interpret shading at missing-data boundaries as measured geometry.

## The notch and the gaps
The low saddle is near 18.75 m along the analytical line. The original ground-only profile is blank around 24.17–27.94 m: a different feature. A small box around those blank samples, expanded one meter each way, contains 332 unclassified and 5 ground-classified returns. Filtering and the two-meter fill cutoff leave cells empty; bilinear profile sampling expands the gap.

Split raw-point height bands remain in a narrower 0.3 m-wide strip. Abrupt geometry or multiple sampled surfaces can produce bands, but this analysis does not prove the cause of each separation or the classifier's original decision. No aircraft-motion fault is inferred.

## Local rock experiment
Based on firsthand observation of bare rock at the notch, treat class 1 (unclassified) and class 2 (ground) as rock candidates locally and exclude class 7 noise. Original classifications are unchanged. Use median elevation per 0.5 m cell in a 55 × 82 m crop. Linear interpolation fills remaining cells only where an actual return is within one meter.

95,573 returns are included; 99.817% of cells contain direct measurements. Central-line descent over five horizontal meters before the trough is about 4.52 m. Profiles shifted east/west by up to one meter give 4.50–5.21 m. A ten-meter look-back includes additional approach terrain and gives 7.20–9.03 m. These are window-dependent terrain differences, not surveyed vertical cliff heights.

The deliberately fitted cue requires a 3 m descent from the preceding 10 m and a 3 m rise within the following 15 m. It flags distances 11.25–21.5 m on this line. It has no out-of-sample validation or established false-positive rate. Exact results: `sources/notch-model/model-results.json`.

## Wider ridge
Include classes 1 and 2, excluding labeled noise, in a 290 × 240 m crop. Compute one-meter medians and linearly fill empty cells only within 1.5 m of a return. Included: 1,667,884 returns; more than 99.99% of cells have measurements. The wider crop may contain snow or vegetation; the notch's rock assumption is not independently established everywhere.

Orange highlights GPX portions north of UTM northing 5340735 within the crop, an illustrative match to the reported approach, not surveyed scree boundaries. The GPX is draped on modeled elevations and lifted 1.5–2 m for display; these are not GPS altitude measurements. Static route lines are foreground overlays for readability, including where terrain would otherwise occlude them.

## Reading the visuals
3D scenes have equal physical axis scales, with no vertical exaggeration. Static ridge surfaces display every third raster cell; the GeoTIFF and interactive scene use one-meter cells. Profile diagrams use different horizontal/vertical screen scales for readability.

Grid spacing is not positional accuracy. One-height-per-cell models cannot fully represent vertical faces or overhangs; use raw points to inspect those features. These experiments support annotation of this example, not climbing-difficulty ratings, equipment selection, or route-safety certification.
