"""Snapshot complete ArcGIS bbox queries; fail on missing IDs or service errors."""
import json, urllib.request, urllib.parse, concurrent.futures
from pathlib import Path
S=Path(__file__).resolve().parents[1]/'sources'
B='https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_dnr/'
BBOX='-90.51,48.025,-90.07,48.135'
def request(url,p):
 u=url+'?'+urllib.parse.urlencode(p)
 with urllib.request.urlopen(u,timeout=90) as r:j=json.load(r)
 if 'error' in j:raise RuntimeError(j['error'])
 return j,u
def fetch(task):
 name,url=task
 meta,_=request(url,{'f':'json'});(S/(name+'-service.json')).write_text(json.dumps(meta))
 p={'f':'json','geometry':BBOX,'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','where':'1=1','returnIdsOnly':'true'}
 ids,u=request(url+'/query',p); ids=ids.get('objectIds') or []; features=[]; requests=[u]
 for start in range(0,len(ids),150):
  j,u=request(url+'/query',{'f':'geojson','objectIds':','.join(map(str,ids[start:start+150])),'outFields':'*','outSR':4326,'returnGeometry':'true'})
  features+=j['features'];requests.append(u)
 assert len(features)==len(ids),(name,len(features),len(ids))
 (S/(name+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','features':features}))
 (S/(name+'-requests.json')).write_text(json.dumps({'urls':requests,'object_ids':ids,'count':len(features)},indent=2))
 print(name,len(features),[f['properties'] for f in features[:1]],flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:list(e.map(fetch,[('hydrography',B+'water_dnr_hydrography/FeatureServer/1'),('depth-contours',B+'water_lake_bathymetry/MapServer/0'),('wilderness',B+'bdry_boundary_waters_canoe_area/FeatureServer/2')]))
