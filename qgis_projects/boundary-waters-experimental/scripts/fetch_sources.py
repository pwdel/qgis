"""Explicit acquisition of additional public hydrography and trail evidence."""
import json,urllib.request,urllib.parse,datetime,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/'sources'; old=R.parent/'boundary-waters'/'sources'
for name in ['lidar-route-8m.tif','lidar-route-request.json','lidar-service.json','portage-landings.geojson','portage-usfs-layer.json','hydrography-service.json']:
 shutil.copy2(old/name,S/name)
log=[]
def get(base,params,name):
 url=base+'?'+urllib.parse.urlencode(params)
 with urllib.request.urlopen(url,timeout=90) as r: data=json.load(r)
 assert 'error' not in data,data
 (S/name).write_text(json.dumps(data,indent=2))
 log.append({'url':url,'path':name,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 return data
bbox='-90.42,48.015,-89.97,48.125'
base='https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublish_01/MapServer/0/query'
a=get(base,dict(f='json',where='1=1',geometry=bbox,geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outSR=4326,outFields='*',returnGeometry='true'),'usfs-trails.json')
assert not a.get('exceededTransferLimit')
print('Trails',len(a['features']),flush=True)
base='https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/water_dnr_hydrography/FeatureServer/1/query'
a=get(base,dict(f='json',where='1=1',geometry=bbox,geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',returnIdsOnly='true'),'hydro-ids.json')
features=[]
for i in range(0,len(a['objectIds']),150):
 b=get(base,dict(f='geojson',objectIds=','.join(map(str,a['objectIds'][i:i+150])),outSR=4326,outFields='*',returnGeometry='true'),f'hydro-{i//150}.json')
 features+=b['features']
(S/'hydrography.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features}))
(S/'acquisition.json').write_text(json.dumps(log,indent=2))
print('Hydro',len(features),flush=True)
for f in json.load(open(S/'usfs-trails.json'))['features']:
 n=f['attributes'].get('trail_name','') or ''
 if any(s in n for s in ['JOHN','MCFAR','PIKE','CARIBOU','PINE']):print(f['attributes']['objectid'],n)
