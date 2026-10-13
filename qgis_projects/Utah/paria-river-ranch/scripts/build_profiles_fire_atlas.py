"""Create the 19-page riding edition from the preserved expanded project.
Run after trail_profiles.py and fetch_fire_data.py. Local paths remain portable.
"""
import os,json,math,shutil,zipfile,textwrap
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QFont
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject,AnnotationBuilder
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'derived/riding';O=ROOT/'output/pdf/riding'
for x in [D,O]:x.mkdir(parents=True,exist_ok=True)
# Isolate mutable GeoPackages from both earlier editions.
replacements={}
for old,new in [('derived/atlas.gpkg','derived/riding/original-context.gpkg'),('derived/expansion/atlas-context.gpkg','derived/riding/expanded-context.gpkg')]:
 shutil.copy2(ROOT/old,ROOT/new);replacements[old.encode()]=new.encode()
tmp=ROOT/'_riding-input.qgz'
with zipfile.ZipFile(ROOT/'paria-river-ranch-expanded.qgz') as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as dst:
 for name in src.namelist():
  data=src.read(name)
  if name.endswith('.qgs'):
   for old,new in replacements.items():data=data.replace(old,new)
  dst.writestr(name,data)
app=QgsApplication([],False);app.initQgis();project=QgsProject.instance();assert project.read(str(tmp))
project.setFilePathStorage(Qgis.FilePathType.Relative)
INK='#273d39';RUST='#9c5433';CREAM='#fcfaf4';BLUE='#16768b'
AREAS=['02-ranch','03-mount-carmel','04-red-canyon'];SLUGS=['ranch','mount-carmel','red-canyon'];NAMES=['Paria River Ranch','Mount Carmel & Bay Bill','Red Canyon & plateau edge']
SOURCE_URL='https://github.com/pwdel/qgis/blob/main/qgis_projects/Utah/paria-river-ranch/docs/RIDING-SOURCES.md'
records=[];pdfs=[]
def label(l,t,x,y,w,h,size=10,bold=False,color=INK):
 a=QgsLayoutItemLabel(l);a.setText(t);f=QFont('DejaVu Sans');f.setPointSizeF(size);f.setBold(bold);a.setFont(f);a.setFontColor(QColor(color));l.addLayoutItem(a);a.attemptMove(QgsLayoutPoint(x,y));a.attemptResize(QgsLayoutSize(w,h));return a

def box(l,x,y,w,h,col):
 a=QgsLayoutItemShape(l);a.setShapeType(QgsLayoutItemShape.Rectangle);a.setSymbol(QgsFillSymbol.createSimple({'color':col,'outline_style':'no'}));l.addLayoutItem(a);a.attemptMove(QgsLayoutPoint(x,y));a.attemptResize(QgsLayoutSize(w,h));return a

def layout(title,sub,num):
 l=QgsPrintLayout(project);l.initializeDefaults();l.pageCollection().page(0).setPageSize(QgsLayoutSize(438.15,285.75));box(l,0,0,438.15,285.75,CREAM);box(l,12,11,2,21,RUST)
 label(l,title,18,10,384,14,23,True);label(l,sub,18,27,400,8,9,False,RUST);label(l,f'{num:02}',407,9,20,17,28,True,RUST);return l

def footer(l,source,warning):
 label(l,'SOURCES (click for URLs)  '+source,12,265,414,6,7)
 label(l,'09 OCT 2026  /  PLANNING DRAFT  /  '+warning+'  /  Avenza: second pass',12,273,414,5,7,True,RUST)

def picture(l,path,x,y,w,h):
 assert Path(path).exists(),path
 p=QgsLayoutItemPicture(l);l.addLayoutItem(p);p.attemptMove(QgsLayoutPoint(x,y));p.attemptResize(QgsLayoutSize(w,h));p.setPicturePath(str(path));return p

def vector(path,name):
 v=QgsVectorLayer(str(path),name,'ogr');assert v.isValid(),path;project.addMapLayer(v);return v

def named(prefix):return next(v for v in project.mapLayers().values() if v.name().startswith(prefix))

def mapitem(l,layers,bbox,x,y,w,h):
 m=QgsLayoutItemMap(l);l.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(x,y));m.attemptResize(QgsLayoutSize(w,h));m.setCrs(project.crs());m.setLayers(layers);m.setKeepLayerSet(True)
 # Expand bbox to fit the requested physical aspect without moving other items.
 cx=(bbox[0]+bbox[2])/2;cy=(bbox[1]+bbox[3])/2;bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
 if bw/bh<w/h:bw=bh*w/h
 else:bh=bw*h/w
 m.setExtent(QgsRectangle(cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2));assert math.isfinite(m.scale());m.setFrameEnabled(True)
 label(l,f'N ↑  |  1:{round(m.scale()):,}  |  NAD83 / UTM 12N',x,y+h+1,w,6,7)
 return m

def save(l,name):
 l.setName(name);project.layoutManager().addLayout(l);p=O/(name+'.pdf');cfg=QgsLayoutExporter.PdfExportSettings();cfg.dpi=220;cfg.textRenderFormat=QgsRenderContext.TextFormatAlwaysText;cfg.appendGeoreference=False
 assert QgsLayoutExporter(l).exportToPdf(str(p),cfg)==QgsLayoutExporter.Success
 r=PdfReader(str(p));w=PdfWriter();pg=r.pages[0];pg.mediabox=RectangleObject([0,0,1242,810]);pg.bleedbox=RectangleObject([0,0,1242,810]);pg.trimbox=RectangleObject([9,9,1233,801]);w.add_page(pg)
 w.add_annotation(page_number=0,annotation=AnnotationBuilder.link(rect=(34,40,1210,62),url=SOURCE_URL))
 w.add_metadata({'/Title':name,'/Subject':'Trail elevation, fire history and dated authority; planning estimates'})
 with p.open('wb') as f:w.write(f)
 pdfs.append(p);records.append({'name':name,'pdf':str(p.relative_to(ROOT))});print('exported',name,flush=True)

# Clone before removing old layout inventory; old files themselves remain untouched.
old={r['name']:project.layoutManager().layoutByName(r['name']).clone() for r in json.loads((ROOT/'docs/expanded-layouts.json').read_text())}
for lo in list(project.layoutManager().layouts()):project.layoutManager().removeLayout(lo)
frames=named('Detail sheet footprints');fp=frames.labeling().settings();fp.fieldName="CASE WHEN \"sheet\" = '03 / MT CARMEL' THEN '08 / MT CARMEL' WHEN \"sheet\" = '04 / RED CANYON' THEN '14 / RED CANYON' ELSE \"sheet\" END";fp.isExpression=True;frames.setLabeling(QgsVectorLayerSimpleLabeling(fp))
def prior(oldname,num):
 l=old[oldname]
 for it in l.items():
  if isinstance(it,QgsLayoutItemLabel):
   t=it.text()
   if t==oldname[:2]:t=f'{num:02}'
   if '02  Paria River' in t:t=t.replace('06  Mount Carmel','08  Mount Carmel').replace('10  Red Canyon','14  Red Canyon')
   it.setText(t)
 save(l,f'{num:02}'+oldname[2:])

# New pages are implemented below from the analysis output contracts.
def profile_page(idx,num):
 n=AREAS[idx];l=layout(NAMES[idx]+' / trail elevation','ROUTE PROFILES  /  CLIMBING, DESCENT AND DIRECTION OF TRAVEL',num)
 routes=vector(ROOT/'sources/profiles'/(n+'-routes.geojson'),SLUGS[idx]+' | profile routes and ascent estimates');routes.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':BLUE,'line_width':'.5'}));project.layerTreeRoot().findLayer(routes.id()).setItemVisibilityChecked(False)
 picture(l,ROOT/'derived/profiles'/(n+'-profiles.svg'),12,39,414,209)
 label(l,'Axes vary by trail; drawn profile angles do not measure grade. Y = feet from start; X = miles. Total climbing / descent are separate estimates.',12,249,414,6,8)
 label(l,'3DEP mosaic fallback: 15 / 10 / 13.75m output cells; native lidar provenance unverified. 30m sampling; smoothing and 3m noise threshold. Cutouts: orientation only.',12,256,414,6,7.5)
 footer(l,'P01  UGRC / USFS trail geometry + USGS 3DEP; full route samples and methods linked','Cliffs, footing and horse permission require separate review')
 save(l,f'{num:02}-{SLUGS[idx]}-profiles')

def fire_page(idx,num):
 n=AREAS[idx];c=json.loads((D/'layout-data.json').read_text())[n]
 l=layout(NAMES[idx]+' / wildfire report','HISTORY, SEASONAL ACTIVITY AND FIRE RESTRICTIONS  /  OCTOBER FOCUS',num)
 label(l,'MAPPED HISTORICAL FIRE FOOTPRINTS',12,36,260,7,9,True)
 per=vector(ROOT/c['perimeters'],SLUGS[idx]+' | historical fire perimeters')
 renderer=QgsRuleBasedRenderer(QgsFillSymbol.createSimple({'color':'207,91,57,80','outline_color':'#a83f28','outline_width':'.35'}))
 root=renderer.rootRule();root.children()[0].setFilterExpression("lower(\"fire_type\") NOT LIKE '%prescribed%'")
 rule=QgsRuleBasedRenderer.Rule(QgsFillSymbol.createSimple({'color':'91,129,157,65','outline_color':'#477791','outline_width':'.35'}));rule.setFilterExpression("lower(\"fire_type\") LIKE '%prescribed%'");rule.setLabel('Prescribed fire');root.appendChild(rule);per.setRenderer(renderer)
 pal=QgsPalLayerSettings();pal.fieldName="coalesce(\"fire_name\", 'Fire') || ' / ' || to_string(\"year\")";pal.isExpression=True
 fmt=QgsTextFormat();fmt.setFont(QFont('DejaVu Sans'));fmt.setSize(7);buf=QgsTextBufferSettings();buf.setEnabled(True);buf.setSize(.8);buf.setColor(QColor('white'));fmt.setBuffer(buf);pal.setFormat(fmt);per.setLabeling(QgsVectorLayerSimpleLabeling(pal));per.setLabelsEnabled(True)
 ext=json.loads((ROOT/'sources'/(n+'-extent.json')).read_text())['bbox_utm12'];topo=named(n+' | USGS');trails=named('State trails');roads=named('Named approach')
 occ=vector(ROOT/c['occurrences'],SLUGS[idx]+' | reported fire discovery points 1992-2024');occ.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','color':'#a65d31','outline_style':'no','size':'1.1'}));occ.setOpacity(.65)
 mapitem(l,[trails,roads,occ,per,topo],ext,38,44,141*298/202,141)
 box(l,12,194,5,3,'#cf5b39');label(l,'Wildfire',19,191,45,7,7)
 box(l,65,194,5,3,'#5b819d');label(l,'Prescribed fire',72,191,58,7,7)
 label(l,c['history_caption'],132,190,140,11,6.8)
 label(l,'Dots: reported discovery points; approximate locations.',12,198,260,6,6.7)
 picture(l,ROOT/c['monthly_chart'],12,205,260,47)
 label(l,c['monthly_caption'],12,254,260,9,7)
 label(l,c['annual_title'],284,36,142,7,9,True)
 if c.get('annual_raster'):
  r=QgsRasterLayer(str(ROOT/c['annual_raster']),SLUGS[idx]+' | annual fire likelihood visualization');assert r.isValid();project.addMapLayer(r)
  assert r.bandCount()>=3, 'Annual image must preserve official rendered colors'
  mapitem(l,[roads,r,topo],ext,295,44,81*298/202,81)
 else:
  box(l,284,44,142,81,'#eae7df');label(l,'Annual probability map unavailable.\nNo local numerical chance is assigned.',292,66,124,30,12,True)
 for k in range(11):picture(l,D/f'wrc-swatch-{k:02}.png',284+k*12.9,132,12.9,3)
 label(l,'Lower  <  official annual likelihood classes  >  Higher',284,135,142,5,6.6)
 label(l,c['annual_caption'],284,141,142,12,6.5)
 label(l,'AUTHORITY / DATED RESTRICTION CHECK',284,154,142,7,9,True,RUST)
 y=164
 for block in c['blocks']:
  label(l,block['title'],284,y,142,7,8.5,True,RUST)
  lines='\n'.join(textwrap.wrap(block['body'],width=83,break_long_words=False))
  height=3.8*len(lines.splitlines())+2
  label(l,lines,284,y+7,142,height,7.5);y+=height+10
 assert y<=265,(n,y)
 footer(l,'F01-F04 fire history / annual model; F05 dated orders and outlook. All periods, thresholds and update links in source key.','Historical activity is not October trip probability')
 save(l,f'{num:02}-{SLUGS[idx]}-wildfire')

prior('01-regional-overview',1)
for idx,slug in enumerate(SLUGS):
 start=2+idx*6;oldstart=2+idx*4
 for offset,kind in enumerate(['access','terrain','snow','camping']):prior(f'{oldstart+offset:02}-{slug}-{kind}',start+offset)
 profile_page(idx,start+4);fire_page(idx,start+5)
writer=PdfWriter()
for p in pdfs:writer.append(str(p))
writer.add_metadata({'/Title':'Paria River Ranch - Horse Riding Atlas','/Subject':'19 sheets: access, terrain, snow, camping, trail profiles and wildfire'})
with (O/'paria-river-ranch-riding-atlas.pdf').open('wb') as f:writer.write(f)
project.setTitle('Paria River Ranch | 19-page horse riding atlas');project.setFileName(str(ROOT/'paria-river-ranch-riding-atlas.qgz'));assert project.write()
(ROOT/'docs/riding-layouts.json').write_text(json.dumps(records,indent=2)+'\n');tmp.unlink()
print('saved 19-page riding atlas',flush=True)
