"""Verify saved output, source preservation, layout extents and portability."""
import os,json,math,zipfile,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import QgsApplication,QgsProject,QgsLayoutItemMap,QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsPointXY
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources';D=ROOT/'derived'
checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
# Canonical KML geometry retained exactly, not snapped to modern trails.
n={'k':'http://www.opengis.net/kml/2.2'};tree=ET.parse(S/'2008-boundary-waters.kml');source=[]
for p in tree.findall('.//k:Placemark',n):
 c=p.find('.//k:LineString/k:coordinates',n)
 if c is not None:source.append((p.findtext('k:name',namespaces=n),[list(map(float,v.split(',')[:2])) for v in c.text.split()]))
route=json.loads((D/'route.geojson').read_text())['features']
check('Five KML segments / 160 vertices preserved exactly',[(f['properties']['name'],f['geometry']['coordinates']) for f in route]==source and sum(len(c) for _,c in source)==160)
landings=json.loads((S/'portage-landings.geojson').read_text())['features'];views=json.loads((D/'portage-views.json').read_text())
check('Twelve approach views, none claimed field verified',len(landings)==len(views)==12 and all(f['properties']['field_verified'] is False for f in landings))
check('Three explicit low-confidence candidates',{f['properties']['id'] for f in landings if f['properties']['confidence']=='low'}=={'P01','P10','P11'})
check('Water viewpoint and sightline derivation checks recorded',all(f['properties']['view_in_named_lake'] and f['properties']['sightline_in_water_2m_tolerance'] for f in landings))
check('Terrain views have equal angular scale, no canopy, finite local elevations',all(v['vertical_exaggeration']==1 and v['horizontal_fov_deg']==v['vertical_fov_deg'] and v['canopy'] is False and 400<v['water_elevation_estimate_m']<650 for v in views))
app=QgsApplication([],False);app.initQgis();p=QgsProject.instance();check('QGIS project reopens',p.read(str(ROOT/'boundary-waters.qgz')))
check('All local data layers valid',all(l.isValid() for l in p.mapLayers().values()))
layouts=p.layoutManager().layouts();check('Six editable layouts',len(layouts)==6)
for layout in layouts:
 for m in [i for i in layout.items() if isinstance(i,QgsLayoutItemMap)]:check(layout.name()+' has finite map extent and scale',not m.extent().isEmpty() and math.isfinite(m.scale()) and m.scale()>0)
with zipfile.ZipFile(ROOT/'boundary-waters.qgz') as z:
 xml=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.qgs'))))
 check('Every project layer has a relative file path',all(el.text.startswith('./') for el in xml.findall('./projectlayers/maplayer/datasource')))
 pics=[el.attrib['file'] for el in xml.findall('.//LayoutItem') if el.attrib.get('file')]
 check('All layout picture paths portable',len(pics)==24 and all(v.startswith('./') for v in pics))
 for v in pics:check('Picture exists: '+v,(ROOT/v).exists())
# Every approach must lie on the associated detail sheet, not merely on overview.
tx=QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),p.crs(),p)
for i,l in enumerate(sorted([x for x in layouts if x.name()[:2] in ['02','03','04','05']],key=lambda x:x.name())):
 m=next(x for x in l.items() if isinstance(x,QgsLayoutItemMap))
 for f in landings[i*3:i*3+3]:
  pt=tx.transform(QgsPointXY(*f['geometry']['coordinates']));check(f['properties']['id']+' contained by assigned detail sheet',m.extent().contains(pt))
r=PdfReader(ROOT/'output/pdf/boundary-waters-six-page-atlas.pdf');check('Exactly six PDF pages',len(r.pages)==6)
for i,page in enumerate(r.pages,1):
 check(f'Page {i} exact 17x11 inch dimensions',abs(float(page.mediabox.width)-1224)<.1 and abs(float(page.mediabox.height)-792)<.1)
 check(f'Page {i} searchable text',(len(page.extract_text() or '')>500))
attachments=r.trailer['/Root']['/Names']['/EmbeddedFiles']['/Names']
check('Twelve full original depth maps embedded',len(attachments)==24)
panel_by_slug={v['lake']:v for v in json.loads((D/'depth-panels.json').read_text())}
for i in range(0,len(attachments),2):
 slug=str(attachments[i]).replace('-original-depth-map.pdf','');data=attachments[i+1].get_object()['/EF']['/F'].get_object().get_data()
 check(slug+' embedded PDF identical to source',data==(ROOT/panel_by_slug[slug]['source']).read_bytes())
check('Twenty-five clickable report/map citations',sum(len(pg.get('/Annots',[])) for pg in r.pages)>=25)
fish=json.loads((S/'fisheries.json').read_text());check('Thirteen dated lake fish records',len(fish)==13 and all(f['survey_year'] and f['source_url'].startswith('https://www.dnr.state.mn.us/') for f in fish))
panels=json.loads((D/'depth-panels.json').read_text());check('Twelve source-linked unregistered historic depth panels',len(panels)==12 and all(v['georeferenced'] is False and v['source_url'].startswith('https://files.dnr.state.mn.us/') for v in panels))
check('No fabricated Watap depth map','watap' not in [v['lake'] for v in panels])
result={'status':'passed','checks':checks,'check_count':len(checks),'qgis_version':'3.22.16','limits':['Visual QA recorded separately','Terrain omits canopy; approximate map-derived candidates','Long-lake depth labels require original attachments or digital zoom','No Avenza/GeoPDF positioning certification']}
(ROOT/'docs/validation.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for d in [S,ROOT/'output/pdf'] for f in d.rglob('*') if f.is_file() and '__pycache__' not in str(f)}
(ROOT/'docs/manifest-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASSED',len(checks),'checks')
