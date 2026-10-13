"""Validate riding PDF, data provenance, offline project and preservation."""
import os,json,hashlib,math,shutil,tempfile,re,csv
from osgeo import gdal
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pypdf import PdfReader
from qgis.core import *
ROOT=Path(__file__).resolve().parents[1];checks={}
def check(name,value):
 checks[name]=bool(value)
 if not value:raise AssertionError(name)
for record in json.loads((ROOT/'sources/manifest.json').read_text())['files']:
 p=ROOT/record['path'];check('preserved original '+record['path'],hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'])
for record in json.loads((ROOT/'docs/expanded-manifest.json').read_text())['files']:
 p=ROOT/record['path'];check('preserved expansion '+record['path'],hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'])

fire=json.loads((ROOT/'derived/fire-data/fire-summary.json').read_text())
for area,a in fire['areas'].items():
 check(area+' 12 monthly counts',len(a['monthly_counts'])==12)
 check(area+' count reconciliation',sum(a['monthly_counts'])+a['unknown_month_count']==a['occurrence_count'])
 check(area+' October correct',a['monthly_counts'][9]==a['october_count'])
 check(area+' source period',a['sample_period']==[1992,2024])
 for field,count in [('occurrences','occurrence_count'),('perimeters','perimeter_count')]:
  features=json.loads((ROOT/a[field]).read_text())['features'];check(area+' '+field+' geometry count',len(features)==a[count])
 annual=a['annual_burn_probability'];check(area+' no invented October odds',annual['october_probability'] is None and annual['monthly_probability'] is None)
 ds=gdal.Open(str(ROOT/annual['rendered_raster']));check(area+' official RGBA',ds is not None and ds.RasterCount==4);ds=None
 profile=json.loads((ROOT/'sources/profiles'/(area+'-profiles.json')).read_text())
 check(area+' full profile inventory',not profile['omitted_page_components'] and len(profile['profiles'])==len(profile['page_profile_ids']))
 check(area+' native provenance explicit',profile['native_resolution_verified'] is False)
 svg=(ROOT/profile['plot_svg']).read_text();check(area+' stable outlined chart fonts','<text' not in svg)
 for p in profile['profiles']:
  check(p['id']+' nonnegative totals',p['ascent_ft']>=0 and p['descent_ft']>=0)
  check(p['id']+' sample coverage',p['sample_count']==p['valid_samples']+p['gap_samples'])
  check(p['id']+' complete samples',sum(1 for _ in csv.DictReader((ROOT/p['csv']).open()))==p['sample_count'])

O=ROOT/'output/pdf/riding';combined=O/'paria-river-ranch-riding-atlas.pdf';pdfs=list(O.glob('*.pdf'))
check('20 pdf outputs',len(pdfs)==20)
for p in pdfs:
 r=PdfReader(str(p));check(p.name+' page count',len(r.pages)==(19 if p==combined else 1))
 for i,pg in enumerate(r.pages):
  key=p.name+str(i);check(key+' media box',list(pg.mediabox)==[0,0,1242,810]);check(key+' trim',list(pg.trimbox)==[9,9,1233,801]);check(key+' searchable text',len(pg.extract_text())>200)
  aa=pg.get('/Annots',[]);aa=aa.get_object() if hasattr(aa,'get_object') else aa
  check(key+' linked evidence',any('RIDING-SOURCES.md' in str(a.get_object().get('/A',{}).get('/URI','')) for a in aa))
text=[' '.join(p.extract_text().lower().split()) for p in PdfReader(str(combined)).pages]
for i in [5,11,17]:check('profile page '+str(i+1),all(s in text[i] for s in ['trail elevation','total climbing','feet','miles']))
for i in [6,12,18]:check('fire page '+str(i+1),all(s in text[i] for s in ['fire','october','restriction']))
app=QgsApplication([],False);app.initQgis();p=QgsProject.instance()
def validate_project(path,tag):
 check(tag+' opens',p.read(str(path)));check(tag+' 19 layouts',len(p.layoutManager().layouts())==19)
 for layer in p.mapLayers().values():
  check(tag+' layer '+layer.name(),layer.isValid())
  if isinstance(layer,QgsVectorLayer) and layer.featureCount()>0:check(tag+' readable '+layer.name(),next(layer.getFeatures(),None) is not None)
 for l in p.layoutManager().layouts():
  for it in l.items():
   if isinstance(it,QgsLayoutItemMap):
    check(tag+' map '+it.uuid(),math.isfinite(it.scale()) and it.scale()>0)
    if l.name().endswith('-wildfire'):
     area=['02-ranch','03-mount-carmel','04-red-canyon'][[7,13,19].index(int(l.name()[:2]))]
     expected=fire['areas'][area]['extent']['bbox_utm12'];b=it.extent();actual=[b.xMinimum(),b.yMinimum(),b.xMaximum(),b.yMaximum()]
     check(tag+' fire exact analysis bounds '+it.uuid(),max(abs(x-y) for x,y in zip(actual,expected))<.01)
   if isinstance(it,QgsLayoutItemPicture) and it.picturePath():check(tag+' image '+it.uuid(),Path(it.picturePath()).exists())
validate_project(ROOT/'paria-river-ranch-riding-atlas.qgz','local ');p.clear()
with tempfile.TemporaryDirectory(prefix='utah-riding-check-') as t:
 target=Path(t)/'atlas';shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__','previews','output'))
 validate_project(target/'paria-river-ranch-riding-atlas.qgz','relocated ');p.clear()
files=[]
for folder in ['sources/profiles','sources/fire-data','sources/fire-orders','derived/profiles','derived/fire-data','derived/riding','output/pdf/riding']:
 for f in sorted((ROOT/folder).rglob('*')):
  if f.is_file():files.append({'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(ROOT/'docs/riding-manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n')
(ROOT/'docs/riding-validation.json').write_text(json.dumps({'status':'PASS','count':len(checks),'checks':checks},indent=2)+'\n')
print('PASS',len(checks),'checks')
