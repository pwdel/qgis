"""Validate evidence, complete downloads, PDFs, and relocated QGIS data paths."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import QgsApplication,QgsProject,QgsLayoutItemMap,QgsRuleBasedRenderer,QgsExpression
from osgeo import gdal,ogr,osr
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'sources'
app=QgsApplication([],False);app.initQgis()
report={'checks':{},'limitations':['No field inspections or current manager confirmations.',
 'Not tested in Avenza. QGIS validation runs in 3.22.16; macOS QGIS 4 GUI not certified.']}

def check(name,condition):
    assert condition,name
    report['checks'][name]=True

e=json.loads((S/'evidence.json').read_text())['records'];byid={x['id']:x for x in e}
check('unique evidence IDs',len(byid)==len(e))
for r in e:
    check('evidence scope '+r['id'],all(k in r for k in ['title','publisher','url','supported_claim','limitations','retrieved_at','observed_at','retrieval_status']))
    check('nonempty scope '+r['id'],bool(r['supported_claim'] and r['limitations']))
    if r['id']!='E19':check('web citation '+r['id'],r['url'].startswith('https://'))
points=json.loads((S/'planning-points.geojson').read_text())['features']
types=json.loads((ROOT/'docs'/'types.json').read_text())
for f in points:
    p=f['properties'];xy=f['geometry']['coordinates']
    for key,values in types.items():
        if key!='profile_version':check('type '+f['id']+' '+key,p[key] in values)
    check('point bounds '+f['id'],-113<xy[0]<-111 and 36.9<xy[1]<38)
    check('critical evidence '+f['id'],bool(p['evidence_ids']) and all(x in byid for x in p['evidence_ids']))
    check('coordinate evidence '+f['id'],p['coordinate_evidence_id'] in byid)
    check('recheck '+f['id'],bool(p['recheck']) and p['current_conditions']=='Unknown')
    check('no invented rig measurements '+f['id'],all(p[k] is None for k in ['rig_length_m','turnaround_diameter_m','entrance_width_m','road_grade_percent','water_flow_lpm']))
    if p['water_status']=='AdvertisedPotable':check('potable source '+f['id'],'E01' in p['evidence_ids'])
    if p['water_status']=='SeasonalStockOnly':check('stock source '+f['id'],'E03' in p['evidence_ids'])
check('all requested focal markers represented',{'R1','M1','M2','M3','D1','D2','D3','D4','D5'}=={x['id'] for x in points})
for name in ['roads','trailheads','state-trails','usfs-trails','lidar-coverage']:
    req=json.loads((S/(name+'-request.json')).read_text())
    ids=json.loads((S/(name+'-ids.json')).read_text())
    fc=json.loads((S/(name+'.geojson')).read_text())
    key=req['object_id_field'];actual=[x['properties'].get(key,x.get('id')) for x in fc['features']]
    check('complete feature IDs '+name,sorted(actual)==sorted(ids['objectIds']))
    check('complete feature count '+name,len(actual)==req['received_count']==req['requested_count'])

for path in list(S.glob('*.tif'))+list((ROOT/'derived').glob('*.tif')):
    ds=gdal.Open(str(path));check('raster opens '+path.name,ds is not None)
    crs=osr.SpatialReference(wkt=ds.GetProjection());check('raster CRS '+path.name,crs.GetAuthorityCode(None)=='26912')
    check('raster extent '+path.name,all(math.isfinite(x) for x in ds.GetGeoTransform()))
for name in ['01-region','02-ranch','03-mount-carmel','04-red-canyon']:
    d=json.loads((S/(name+'-dem-catalog.json')).read_text())
    check('catalog not truncated '+name,d['complete'])

pdfs=list((ROOT/'output'/'pdf').glob('*.pdf'))
check('five PDF files',len(pdfs)==5)
texts=[]
for path in pdfs:
    reader=PdfReader(str(path));combined='four-sheets' in path.name
    check('page count '+path.name,len(reader.pages)==(4 if combined else 1))
    for i,p in enumerate(reader.pages):
        check('media box '+path.name+str(i),list(p.mediabox)==[0,0,1242,810])
        check('trim box '+path.name+str(i),list(p.trimbox)==[9,9,1233,801])
        t=' '.join(p.extract_text().split());texts.append(t)
        check('searchable planning text '+path.name+str(i),'PLANNING DRAFT' in t and len(t)>900)
        annotations=p.get('/Annots',[])
        if hasattr(annotations,'get_object'):annotations=annotations.get_object()
        check('clickable source register '+path.name+str(i),any(a.get_object().get('/Subtype')=='/Link' for a in annotations))
check('water and terrain statements survive export',all(term in '\n'.join(texts).lower() for term in ['seasonal','hillside','bay bill','tom best']))

def verify_project(root,label):
    p=QgsProject();check(label+' project read',p.read(str(root/'paria-river-ranch.qgz')))
    check(label+' project CRS',p.crs().authid()=='EPSG:26912')
    check(label+' four layouts',len(p.layoutManager().layouts())==4)
    for l in p.mapLayers().values():
        check(label+' layer '+l.name(),l.isValid())
        check(label+' local path '+l.id(),not l.source().startswith(('http','/tmp/utah-atlas')) if label=='relocated' else not l.source().startswith('http'))
        if hasattr(l,'renderer') and isinstance(l.renderer(),QgsRuleBasedRenderer):
            for rule in l.renderer().rootRule().children():
                check(label+' style '+l.id()+rule.label(),not QgsExpression(rule.filterExpression()).hasParserError())
    for layout in p.layoutManager().layouts():
        size=layout.pageCollection().pages()[0].pageSize()
        check(label+' layout dimensions '+layout.name(),abs(size.width()-438.15)<.001 and abs(size.height()-285.75)<.001)
        maps=[i for i in layout.items() if isinstance(i,QgsLayoutItemMap)]
        check(label+' map exists '+layout.name(),len(maps)==1)
        check(label+' finite scale '+layout.name(),math.isfinite(maps[0].scale()) and maps[0].scale()>0)
    p.clear()
verify_project(ROOT,'original')
with tempfile.TemporaryDirectory(prefix='utah-relocated-') as td:
    dest=Path(td)/'atlas'
    shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns('previews','output','__pycache__'))
    verify_project(dest,'relocated')

manifest=[]
for base in [S,ROOT/'derived']:
    for f in sorted(base.rglob('*')):
        if f.is_file() and f.name not in ['manifest.json'] and '__pycache__' not in str(f):
            manifest.append({'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(S/'manifest.json').write_text(json.dumps({'algorithm':'sha256','files':manifest},indent=2)+'\n')
report['passed']=len(report['checks']);report['qgis_version']='3.22.16';report['visual_review']='Recorded separately after final PDF rendering.'
(ROOT/'docs'/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS',report['passed'],'checks; all PDFs, source IDs, raster CRS, evidence and relocated project verified')
