"""Create finite XYZ map tiles and Gaia TileJSON definitions for public hosting."""
from pathlib import Path
import json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/mobile/gaia';TILES=OUT/'tiles';TILES.mkdir(exist_ok=True)
BASE='https://raw.githubusercontent.com/pwdel/qgis/main/qgis_projects/Utah/paria-river-ranch/output/mobile/gaia/'
records={r['name']:r for r in json.loads((ROOT/'docs/mobile-layouts.json').read_text())}
report=[]
for folder in sorted(OUT.glob('*-custom-map-sources')):
 for tif in sorted(folder.glob('*.tif')):
  name=tif.stem;dest=TILES/name
  subprocess.run(['gdal2tiles.py','--xyz','--zoom=8-13','--resampling=bilinear','--webviewer=none','--processes=2',str(tif),str(dest)],check=True,stdout=subprocess.DEVNULL)
  rec=records[name];coords=rec['corners_lonlat'];bbox=[min(c[0] for c in coords),min(c[1] for c in coords),max(c[0] for c in coords),max(c[1] for c in coords)]
  spec={'tilejson':'2.2.0','name':'Utah riding | '+name,'description':'Planning map, research October 2026. Main map only. Consult atlas legends: cell slope is not trail grade; snow is exploratory; fire is historical, not forecast.','version':'1.0.0','scheme':'xyz','tiles':[BASE+'tiles/'+name+'/{z}/{x}/{y}.png'],'minzoom':8,'maxzoom':13,'bounds':bbox,'center':[(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2,11],'attribution':'USGS, Utah UGRC, USFS, BLM, NOAA and other cited public sources; methods: https://github.com/pwdel/qgis/blob/main/qgis_projects/Utah/paria-river-ranch/docs/RIDING-SOURCES.md'}
  (OUT/(name+'.tilejson.json')).write_text(json.dumps(spec,indent=2)+'\n')
  files=list(dest.rglob('*.png'));report.append({'name':name,'tile_count':len(files),'bytes':sum(f.stat().st_size for f in files),'bounds':bbox,'minzoom':8,'maxzoom':13})
  print(name,len(files),'tiles',flush=True)
(ROOT/'docs/gaia-tiles.json').write_text(json.dumps(report,indent=2)+'\n')
