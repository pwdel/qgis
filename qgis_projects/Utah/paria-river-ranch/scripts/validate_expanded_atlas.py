"""Checks data contracts, PDF exports and relocation; visual review is separate."""
import os,json,math,hashlib,shutil,tempfile,re
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import numpy as np
from osgeo import gdal
from pypdf import PdfReader
from qgis.core import *
ROOT=Path(__file__).resolve().parents[1];checks={}
def check(k,v):
 checks[k]=bool(v)
 if not v:raise AssertionError(k)
# Original evidence and derivatives must remain byte-identical.
for f in json.loads((ROOT/'sources/manifest.json').read_text())['files']:
 p=ROOT/f['path'];check('original snapshot '+f['path'],p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'])
for folder in ['expansion-snow','expansion-camping']:
 for f in json.loads((ROOT/'sources'/folder/'manifest.json').read_text()):
  fn=f.get('file',f.get('path'));p=ROOT/'sources'/folder/fn;check('source hash '+folder+'/'+fn,hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'])
for month in range(1,13):
 p=ROOT/'sources/expansion-snow'/f'snowcover-ensemble-p50-{month:02}.tif';ds=gdal.Open(str(p));a=ds.ReadAsArray();nd=ds.GetRasterBand(1).GetNoDataValue()
 check(f'snow {month} shape',a.shape==(300,372));check(f'snow {month} range',np.all((a==nd)|((a>=0)&(a<=100))))
 check(f'snow {month} resolution',abs(ds.GetGeoTransform()[1]-1/240)<1e-10)
climate=json.loads((ROOT/'sources/expansion-snow/snow-climatology.json').read_text())
for s in climate['stations']:
 check(s['id']+' twelve months',len(s['months'])==12)
 for m in s['months']:
  for key in ['snow_depth_day_frequency_pct','midmonth_snow_depth_ge_1_inch_pct']:
   val=m[key];val=val['value'] if isinstance(val,dict) else val
   check(f'{s["id"]}-{m["month"]}-{key}',val is None or 0<=val<=100)
for area in ['02-ranch','03-mount-carmel','04-red-canyon']:
 ds=gdal.Open(str(ROOT/'derived/expansion'/(area+'-lower-ground-100m.tif')));a=ds.ReadAsArray();valid=a!=-9999
 check(area+' drop nonnegative',np.all(a[valid]>=0));check(area+' UTM',ds.GetSpatialRef().GetAuthorityCode(None)=='26912')
 p=gdal.Open(str(ROOT/'derived/expansion'/(area+'-slope-percent.tif')));a=p.ReadAsArray();check(area+' slopes nonnegative',np.all(a[a!=-9999]>=0))
check('illustrated grade key',all(str(x)+'%' in (ROOT/'derived/expansion/grade-key.svg').read_text() for x in [30,45,60,90]))
review=json.loads((ROOT/'derived/expansion/review-points.geojson').read_text())
check('nine review locations',len(review['features'])==9)
for f in review['features']:check('review '+f['properties']['area']+f['properties']['id'],f['properties']['drop_m_rounded_5']%5==0 and f['properties']['radius_m']==100)
O=ROOT/'output/pdf/expanded';pdfs=list(O.glob('*.pdf'));check('14 PDFs',len(pdfs)==14)
combined=O/'paria-river-ranch-expanded-atlas.pdf'
check('13 combined pages',len(PdfReader(str(combined)).pages)==13)
for p in pdfs:
 r=PdfReader(str(p));check(p.name+' page count',len(r.pages)==(13 if p==combined else 1))
 for i,pg in enumerate(r.pages):
  prefix=p.name+str(i);check(prefix+' box',list(pg.mediabox)==[0,0,1242,810]);check(prefix+' trim',list(pg.trimbox)==[9,9,1233,801]);check(prefix+' searchable',len(pg.extract_text())>400)
  links=[a.get_object().get('/A',{}).get('/URI') for a in (pg.get('/Annots',[]).get_object() if hasattr(pg.get('/Annots',[]),'get_object') else pg.get('/Annots',[]))]
  check(prefix+' source link',any(u and 'EXPANSION-SOURCES.md' in u for u in links))
texts=[' '.join(p.extract_text().lower().split()) for p in PdfReader(str(combined)).pages]
for i in [2,6,10]:check(f'page{i+1} terrain distinction',all(t in texts[i] for t in ['not measured','not a vertical','30-45%','90-150']))
for i in [3,7,11]:check(f'page{i+1} snow distinction',all(t in texts[i] for t in ['satellite','not snow depth','noaa','1991-2020','oct','dec']))
for i in [4,8,12]:check(f'page{i+1} camping distinction','not a campsite permission map' in texts[i])
app=QgsApplication([],False);app.initQgis();p=QgsProject.instance()
def project_check(path,tag):
 check(tag+' project opens',p.read(str(path)));check(tag+' layout count',len(p.layoutManager().layouts())==17)
 for l in p.mapLayers().values():
  check(tag+' valid '+l.name(),l.isValid())
  if isinstance(l,QgsVectorLayer):check(tag+' features '+l.name(),l.featureCount()>0 and next(l.getFeatures(),None) is not None)
 for lo in p.layoutManager().layouts():
  for it in lo.items():
   if isinstance(it,QgsLayoutItemMap):check(tag+lo.name()+it.uuid(),math.isfinite(it.scale()) and it.scale()>0)
   if isinstance(it,QgsLayoutItemPicture) and it.picturePath():check(tag+' picture '+lo.name(),Path(it.picturePath()).exists())
project_check(ROOT/'paria-river-ranch-expanded.qgz','original ')
with tempfile.TemporaryDirectory(prefix='utah-portability-') as t:
 target=Path(t)/'atlas';shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__','previews'))
 p.clear();project_check(target/'paria-river-ranch-expanded.qgz','relocated ');p.clear()
manifest=[]
for folder in ['sources/expansion-snow','sources/expansion-camping','derived/expansion','output/pdf/expanded']:
 for f in sorted((ROOT/folder).rglob('*')):
  if f.is_file():manifest.append({'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(ROOT/'docs/expanded-manifest.json').write_text(json.dumps({'files':manifest},indent=2)+'\n')
(ROOT/'docs/expanded-validation.json').write_text(json.dumps({'status':'PASS','count':len(checks),'checks':checks},indent=2)+'\n')
print('PASS',len(checks),'checks; original snapshots intact; PDFs and relocated QGIS verified')
