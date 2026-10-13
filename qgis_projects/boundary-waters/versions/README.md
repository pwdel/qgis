# Boundary Waters map versions

Five saved stages of the navigation-teaching experiment. Each directory is a self-contained snapshot with an editable QGIS project, local data, source evidence, print layouts, PDFs, previews and a downloadable project ZIP.

**Start with [Version 5: 80 lakes with daylight pies](05-80-lake-daylight-pies/README.md).** Its paired symbols represent shorter and longer estimates within a fixed 15-hour period: white is zero, half black is 7½ hours, and full black is 15 hours.

| Version | Design | Editable project | Printable map | Complete download |
| --- | --- | --- | --- | --- |
| [1 — Clearwater navigation](01-clearwater-navigation/README.md) | Geographic teaching map; hidden portage evidence and vague student clues | [QGIS](01-clearwater-navigation/clearwater-navigation.qgz) | [Student PDF](01-clearwater-navigation/output/pdf/clearwater-student.pdf) · [Instructor PDF](01-clearwater-navigation/output/pdf/clearwater-instructor.pdf) | [ZIP](01-clearwater-navigation/output/clearwater-navigation-project.zip) |
| [2 — 17-lake network](02-17-lake-network/README.md) | Early schematic network with travel-time ranges | [QGIS](02-17-lake-network/journey-network.qgz) | [Chart](02-17-lake-network/output/pdf/journey-chart.pdf) · [Instructor](02-17-lake-network/output/pdf/journey-instructor.pdf) | [ZIP](02-17-lake-network/output/journey-network-project.zip) |
| [3 — 22-lake shaped network](03-22-lake-shaped-network/README.md) | Distorted real lake footprints and source-shaped carries | [QGIS](03-22-lake-shaped-network/journey-network.qgz) | [Chart](03-22-lake-shaped-network/output/pdf/journey-chart.pdf) · [Instructor](03-22-lake-shaped-network/output/pdf/journey-instructor.pdf) | [ZIP](03-22-lake-shaped-network/output/journey-network-project.zip) |
| [4 — 80-lake hour ranges](04-80-lake-hour-ranges/README.md) | Wider region, compact decimal ranges, label leaders and sourced landmarks | [QGIS](04-80-lake-hour-ranges/journey-network.qgz) | [Chart](04-80-lake-hour-ranges/output/pdf/journey-chart.pdf) · [Instructor](04-80-lake-hour-ranges/output/pdf/journey-instructor.pdf) | [ZIP](04-80-lake-hour-ranges/output/journey-network-project.zip) |
| [5 — 80-lake daylight pies](05-80-lake-daylight-pies/README.md) | Paired black-and-white 15-hour pie symbols replace decimal ranges on the chart | [QGIS](05-80-lake-daylight-pies/journey-network.qgz) | [Chart](05-80-lake-daylight-pies/output/pdf/journey-chart.pdf) · [Instructor](05-80-lake-daylight-pies/output/pdf/journey-instructor.pdf) | [ZIP](05-80-lake-daylight-pies/output/journey-network-project.zip) |

Download and extract a complete ZIP before opening its QGZ, or clone this repository and open the QGZ within the chosen version. Downloading only a QGZ omits its data dependencies. Each ZIP retains its original internal folder name; extract different versions into separate folders.

Versions 2–5 also include `geographic-evidence.qgz`, which keeps real positions separate from the deliberately distorted drawing. Historical snapshots retain their original methods and limitations; consult the README and source register within each version. The latest two have 80 lakes, 74 supported connections, five documented lake-view features and three walking waterfall stops. Six lakes remain context-only. The 15-hour unit is a teaching assumption, not a seasonal daylight forecast.

The [original 2008 canoe-route atlas](../README.md) remains in the parent directory. The [working experiment](../../boundary-waters-experimental/README.md) remains available separately.

## Snapshot provenance

Each version's `VERSION.md` identifies its exact source commit. [snapshots.json](snapshots.json) records SHA-256 hashes for all 499 preserved files. [Publication validation](publication-validation.json) records native QGIS reopening, local data-path checks and test exports after copying the projects into these directories. Snapshot contents were not rebuilt or substituted during publication.
