#!/bin/sh
set -eu
QGIS_APP=${QGIS_APP:-/Applications/QGIS-final-4_2_3.app}
export PYTHONHOME="$QGIS_APP/Contents"
export PYTHONPATH="$QGIS_APP/Contents/Resources/python3.12:$QGIS_APP/Contents/Resources/python3.12/lib-dynload:$QGIS_APP/Contents/Resources/python3.12/site-packages:$QGIS_APP/Contents/Resources/qgis/python"
export QGIS_PREFIX_PATH="$QGIS_APP/Contents/Resources/qgis"
export PROJ_DATA="$QGIS_APP/Contents/Resources/qgis/proj"
export QT_PLUGIN_PATH="$QGIS_APP/Contents/PlugIns"
export QT_QPA_PLATFORM=offscreen
exec "$QGIS_APP/Contents/MacOS/python3.12" "$@"
