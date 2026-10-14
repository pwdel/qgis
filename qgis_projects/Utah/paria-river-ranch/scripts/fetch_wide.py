"""Fetch a 1.5x linear extent without overwriting the researched editions."""
import json, concurrent.futures, datetime
from pathlib import Path
from osgeo import gdal
import fetch_sources as fs
import fetch_fire_data as fire
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'sources/wide'; D=ROOT/'derived/wide'
S.mkdir(exist_ok=True);D.mkdir(exist_ok=True)
fire.SRC=S;fire.OUT=D
AREAS=[]
for key in ['02-ranch','03-mount-carmel','04-red-canyon']:
 a=json.loads((ROOT/'sources'/(key+'-extent.json')).read_text());b=a['bbox_utm12'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;w=(b[2]-b[0])*1.5;h=(b[3]-b[1])*1.5
 a.update(bbox_utm12=[cx-w/2,cy-h/2,cx+w/2,cy+h/2],width_m=w,height_m=h,expansion_linear=1.5,created='2026-10-14');fs.save(S/(key+'-extent.json'),a);AREAS.append(a)
def rasters(a):
 key=a['id'];b=a['bbox_utm12'];base={'bbox':','.join(map(str,b)),'bboxSR':26912,'imageSR':26912,'size':'3300,2237','f':'json'}
 for kind,url,extra in [('topo','https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/export',{'format':'png32','dpi':220}),('dem','https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage',{'format':'tiff','pixelType':'F32','renderingRule':json.dumps({'rasterFunction':'None'}),'interpolation':'RSP_BilinearInterpolation'})]:
  target=S/(key+'-'+kind+'.tif')
  if target.exists():continue
  p={**base,**extra}
  if key=='03-mount-carmel' and kind=='dem':p['size']='2400,1627'
  r,u=fs.js(url,p);fs.save(S/(key+'-'+kind+'-request.json'),{'url':u,'parameters':p,'response':r,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});data,_=fs.get(r['href']);tmp=S/(key+'-download.'+('png' if kind=='topo' else 'tif'));tmp.write_bytes(data);e=r['extent']
  gdal.Translate(str(target),str(tmp),outputSRS='EPSG:26912',outputBounds=[e['xmin'],e['ymax'],e['xmax'],e['ymin']],creationOptions=['COMPRESS=DEFLATE']);tmp.unlink();print(key,kind,flush=True)
 return key

def vectors(a):
 for label,base,layer in [('occurrences',fire.FOD,0),('perimeters',fire.MTBS,63),('ownership','https://gis.trustlands.utah.gov/mapping/rest/services/Land_Ownership/FeatureServer',0)]:
  if not (D/(a['id']+'-'+label+'.geojson')).exists():fire.records(base,layer,a,label)
  print(a['id'],label,flush=True)

def context():
 fs.OUT=S;fs.BBOX='-113.0,36.90,-111.45,38.05'
 for name in ['state-trails','roads','trailheads','usfs-trails']:
  fs.fetch_features((name,fs.SERVICES[name]));print('context',name,flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  jobs=[ex.submit(rasters,a) for a in AREAS]+[ex.submit(vectors,a) for a in AREAS]+[ex.submit(context)]
  for j in concurrent.futures.as_completed(jobs):print('DONE',j.result(),flush=True)
