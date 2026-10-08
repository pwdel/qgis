"""Build a portable QGIS project with six editable landscape atlas layouts."""
import os,json,math,textwrap
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import *
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor,QFont
from osgeo import gdal
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DictionaryObject,NameObject,ArrayObject,FloatObject,TextStringObject,DecodedStreamObject
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources';D=ROOT/'derived';O=ROOT/'output/pdf';P=ROOT/'previews'
O.mkdir(parents=True,exist_ok=True);P.mkdir(exist_ok=True)
app=QgsApplication([],False);app.initQgis();pr=QgsProject.instance();pr.setCrs(QgsCoordinateReferenceSystem('EPSG:26915'));pr.setFilePathStorage(Qgis.FilePathType.Relative)
pr.setTitle('Boundary Waters | 2008 route, lake evidence & canoe-eye terrain')
INK='#233e3c';MUTED='#566863';RUST='#a94d2d';PAPER='#f8f5eb';WATER='#c6dfe6';BLUE='#286480';GOLD='#c18a31'
COLORS=['#b84e33','#75559b','#258494','#b07620','#586f35']
def vl(path,title):
 l=QgsVectorLayer(str(path),title,'ogr');assert l.isValid(),path;pr.addMapLayer(l);return l
def rl(path,title):
 l=QgsRasterLayer(str(path),title);assert l.isValid(),path;pr.addMapLayer(l);return l
def line(col,w=.3,dash=False):return QgsLineSymbol.createSimple({'line_color':col,'line_width':str(w),'line_style':'dash' if dash else 'solid'})
def labeling(l,field,size=9,col=INK,expr=False):
 p=QgsPalLayerSettings();p.fieldName=field;p.isExpression=expr;p.priority=10 if field=='label' else (2 if field=='abs_depth' else 8);p.displayAll=(field=='label')
 if l.geometryType()==QgsWkbTypes.LineGeometry:p.placement=QgsPalLayerSettings.Line;p.repeatDistance=70
 f=QgsTextFormat();f.setFont(QFont('DejaVu Sans',size));f.setSize(size);f.setColor(QColor(col));b=QgsTextBufferSettings();b.setEnabled(True);b.setSize(.75);b.setColor(QColor(PAPER));f.setBuffer(b);p.setFormat(f);l.setLabeling(QgsVectorLayerSimpleLabeling(p));l.setLabelsEnabled(True)
terrain=rl(D/'terrain-relief.tif','Minnesota lidar relief | 8m output from 0.5m service')
rl(D/'lidar-valid-8m.tif','Elevation metres | no bathymetry, zero source cells masked')
hydro=vl(S/'hydrography.geojson','DNR water polygons');hydro.renderer().setSymbol(QgsFillSymbol.createSimple({'color':WATER,'outline_color':'#719fab','outline_width':'.18'}))
# All hydro polygons shown; named route lakes get a separate clear label layer.
contours=vl(S/'depth-contours.geojson','DNR digital lake contours | sparse route coverage, feet')
contours.renderer().setSymbol(line('#4d94ac',.16));labeling(contours,'abs_depth',6,BLUE)
trails=vl(S/'portages.geojson','USFS mapped portage trails');trails.renderer().setSymbol(line('#713d2e',.5,True))
wild=vl(S/'wilderness.geojson','BWCA wilderness boundary');wild.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':'#6b865f','outline_width':'.35','outline_style':'dash'}))
routes=vl(D/'route.geojson','2008 supplied route | historical sketch geometry')
cats=[QgsRendererCategory(i+1,line(c,.75),n) for i,(c,n) in enumerate(zip(COLORS,['Day 1','Day 2','Day 3','Fourth Day','Last Day']))];routes.setRenderer(QgsCategorizedSymbolRenderer('segment',cats))
points=vl(D/'trip-points.geojson','2008 camps, entry/exit and personal observations')
cats=[]
for val,col,shape in [('camp',INK,'triangle'),('fish',GOLD,'star'),('other',INK,'square')]:
 cats.append(QgsRendererCategory(val,QgsMarkerSymbol.createSimple({'name':shape,'color':col,'outline_color':'white','outline_width':'.3','size':'3.2'}),val))
points.setRenderer(QgsCategorizedSymbolRenderer('kind',cats));labeling(points,'label',8)
lakes=vl(D/'lake-labels.geojson','Route lake names | [S] recent stocking record')
lakes.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','size':'0','outline_style':'no','color':'transparent'}));labeling(lakes,'label',9,BLUE)
lands=vl(S/'portage-landings.geojson','Candidate approach landings | not field verified')
cats=[]
for val,col in [('medium',RUST),('low',GOLD)]:cats.append(QgsRendererCategory(val,QgsMarkerSymbol.createSimple({'name':'circle','size':'2.7','color':PAPER,'outline_color':col,'outline_width':'.6'}),val))
lands.setRenderer(QgsCategorizedSymbolRenderer('confidence',cats));labeling(lands,'id',7,RUST)
views=vl(D/'viewpoints.geojson','Canoe viewpoint positions');views.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'cross','size':'2.3','color':RUST,'outline_color':RUST}))
sights=vl(D/'sightlines.geojson','Viewpoint to candidate bearing');sights.renderer().setSymbol(line(RUST,.22,True))
frames=vl(D/'sheet-frames.geojson','Detail sheet footprints');frames.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':RUST,'outline_width':'.35','outline_style':'dash'}));labeling(frames,'sheet',10,RUST)
common=[points,lands,views,sights,routes,trails,lakes,contours,wild,hydro,terrain]
sheets=json.loads((D/'sheets.json').read_text());fish=json.loads((S/'fisheries.json').read_text());panel={x['lake']:x for x in json.loads((D/'depth-panels.json').read_text())};landing={f['properties']['id']:f['properties'] for f in json.loads((S/'portage-landings.geojson').read_text())['features']}
portage_groups=[['P01','P02','P03'],['P04','P05','P06'],['P07','P08','P09'],['P10','P11','P12']]
depth_groups=[['hungry-jack','moss','duncan'],['rose','rove','mountain'],['clearwater','west-pike','east-pike'],['pine','little-caribou','caribou']]
from PIL import Image
(D/'depth-display').mkdir(exist_ok=True)
for slug,p in panel.items():
 im=Image.open(ROOT/p['image']).convert('L');im.thumbnail((2400,1800),Image.Resampling.LANCZOS);im.save(D/'depth-display'/(slug+'.png'))
layout_records=[];links=[]
def label(l,text,x,y,w,h,size=9,bold=False,col=INK):
 i=QgsLayoutItemLabel(l);i.setText(text);font=QFont('DejaVu Sans',int(size),QFont.Bold if bold else QFont.Normal);font.setPointSizeF(size);i.setFont(font);i.setFontColor(QColor(col));i.setMargin(0);l.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,h));return i
def box(l,x,y,w,h,col,border=None):
 i=QgsLayoutItemShape(l);i.setShapeType(QgsLayoutItemShape.Rectangle);i.setSymbol(QgsFillSymbol.createSimple({'color':col,'outline_color':border or col,'outline_width':'.2'}));l.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,h));return i
def picture(l,path,x,y,w,h):
 i=QgsLayoutItemPicture(l);l.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,h));i.setPicturePath(str(path));i.setResizeMode(QgsLayoutItemPicture.Zoom);return i
def header(l,num,title,sub):
 box(l,0,0,431.8,279.4,PAPER);box(l,12,11,2,17,RUST);label(l,title,19,9,370,14,23,True);label(l,sub,19,24,379,7,8.5,False,MUTED);label(l,f'{num:02d} / 06',393,13,27,9,12,True,RUST)
def footer(l,num):
 label(l,'BOUNDARY WATERS  /  HISTORICAL ROUTE ATLAS     •     Source check: 08 OCT 2026',12,265,260,5,7,True,MUTED)
 label(l,'KML 2008 • MN DNR • MnGeo lidar • USFS trails  |  References & limits: sheet 06',12,271,345,4,6.7,False,MUTED)
 label(l,'17 × 11 in  |  Print 100%',355,270,65,5,7,False,MUTED)
def newlayout(name):
 l=QgsPrintLayout(pr);l.initializeDefaults();l.setName(name);l.pageCollection().pages()[0].setPageSize(QgsLayoutSize(431.8,279.4));l.renderContext().setDpi(600);return l
def mapitem(l,s,x,y,w,h,layers):
 m=QgsLayoutItemMap(l);l.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(x,y));m.attemptResize(QgsLayoutSize(w,h));m.setCrs(pr.crs());m.setLayers(layers);m.setKeepLayerSet(True);m.setExtent(QgsRectangle(*s['bbox']));assert math.isfinite(m.scale()) and m.scale()>0;m.setBackgroundColor(QColor('#eeeae0'));m.setFrameEnabled(True);m.setFrameStrokeColor(QColor('#b8bdb1'));m.setFrameStrokeWidth(QgsLayoutMeasurement(.2))
 grid=m.grid();grid.setEnabled(True);grid.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'));grid.setIntervalX(.1 if s['width_m']>20000 else .05);grid.setIntervalY(.04 if s['width_m']>20000 else .02);grid.setStyle(QgsLayoutItemMapGrid.Cross);grid.setLineSymbol(line('#929a90',.1));grid.setCrossLength(.8);grid.setAnnotationEnabled(True);grid.setAnnotationPrecision(2);grid.setAnnotationFont(QFont('DejaVu Sans',6))
 for side in [QgsLayoutItemMapGrid.Left,QgsLayoutItemMapGrid.Right,QgsLayoutItemMapGrid.Top,QgsLayoutItemMapGrid.Bottom]:grid.setAnnotationPosition(QgsLayoutItemMapGrid.InsideMapFrame,side)
 grid.setAnnotationDisplay(QgsLayoutItemMapGrid.LongitudeOnly,QgsLayoutItemMapGrid.Top);grid.setAnnotationDisplay(QgsLayoutItemMapGrid.LatitudeOnly,QgsLayoutItemMapGrid.Right);grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll,QgsLayoutItemMapGrid.Left);grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll,QgsLayoutItemMapGrid.Bottom)
 label(l,'N ↑',x+w-13,y+2,11,6,9,True)
 # UTM grid north differs from true north by about 2 degrees here; explicitly label.
 label(l,'grid',x+w-13,y+8,11,4,5.5)
 bar=QgsLayoutItemScaleBar(l);bar.setStyle('Single Box');bar.setLinkedMap(m);bar.applyDefaultSize();bar.setUnits(QgsUnitTypes.DistanceKilometers);bar.setUnitsPerSegment(1 if s['width_m']>20000 else .5);bar.setNumberOfSegments(2);bar.setNumberOfSegmentsLeft(0);bar.setUnitLabel('km');bar.setFont(QFont('DejaVu Sans',7));bar.setHeight(1.5);l.addLayoutItem(bar);bar.attemptMove(QgsLayoutPoint(x+3,y+h-11));bar.setBackgroundEnabled(True);bar.setBackgroundColor(QColor(PAPER));bar.setBoxContentSpace(1)
 return m
for idx,s in enumerate(sheets):
 l=newlayout(s['id']);header(l,idx+1,s['title'],'CANOE COUNTRY  /  LAKE DEPTHS, FISHERIES EVIDENCE & EXPERIMENTAL PORTAGE VIEWS');footer(l,idx+1)
 if idx==0:
  m=mapitem(l,s,12,36,396,185,[frames]+common)
  label(l,'FOLLOW THE FIVE SOURCE SEGMENTS',12,227,150,6,10,True,RUST)
  for j,(name,col) in enumerate(zip(['Day 1','Day 2','Day 3','Fourth Day','Last Day'],COLORS)):
   box(l,12+j*35,237,8,1.5,col);label(l,name,22+j*35,233.5,26,7,8)
  label(l,'C1–C5: historical camps  •  F1/F2: personal bass observations\nP01–P12: candidate landings; crosses mark canoe viewpoints.',12,245,180,13,8)
  label(l,'READ BEFORE USING',213,227,100,6,10,True,RUST)
  label(l,'Sheets 02–05 pair route maps with separate historic depth scans.\nPage 06 separates surveyed fish, stocking and observations.\nRoute lines are historical sketches; they sometimes cross land.\nGray land has no lidar in this crop. Terrain views omit trees.',213,235,195,24,8.4)
 else:
  m=mapitem(l,s,12,36,296,143,common)
  label(l,'Colored line: 2008 route  •  Brown dash: USFS portage  •  Green dash: BWCA boundary  •  Blue numbers: depth feet  •  [S]: stocking',12,179.3,296,4,6.8)
  label(l,'LAKE DEPTH REFERENCE  /  FEET',12,184,170,6,10,True,RUST)
  label(l,'Independent historic scans • orientation/scale differ from route map • full originals included',12,191,296,5,7,False,MUTED)
  for k,slug in enumerate(depth_groups[idx-1]):
   p=panel[slug];x=12+k*100;name=slug.replace('-',' ').title();box(l,x,200,96,56,'#ffffff','#b7bfb8');label(l,name,x+2,200,92,6,9,True,BLUE)
   picture(l,D/'depth-display'/(slug+'.png'),x+2,207,92,40)
   interval=p['contour_interval'];label(l,(interval+' interval' if interval!='See contour labels' else 'See labels')+' | '+(str(p.get('survey_year')) if p.get('survey_year') else 'date unknown'),x+2,249,92,5,6.5,False,MUTED)
   links.append({'page':idx,'rect_mm':[x,200,96,56],'url':p.get('source_url','https://www.dnr.state.mn.us/lakefind/index.html')})
  label(l,'CANOE-EYE TERRAIN  /  EXPERIMENT',319,36,101,6,9,True,RUST)
  for k,pid in enumerate(portage_groups[idx-1]):
   p=landing[pid];y=45+k*70
   title=p['from_lake']+' → '+p['to_lake'];title=title.replace('Pine via West Pike junction','Pine (junction)')
   label(l,pid+'  '+title,319,y,101,10,8.4,True)
   picture(l,D/'portage-views'/(pid+'.png'),319,y+10,55,55)
   low=p['confidence']=='low';text='UNRESOLVED\nLANDING' if low else 'Mapped candidate\nNot field verified'
   label(l,text,376,y+13,43,12,7,True,RUST if low else MUTED)
   label(l,f"{p['view_distance_m']:.0f}m offshore\n{p['view_bearing_deg']:.0f}° true bearing\nCross = viewpoint\nCircle = candidate\nBare earth; no trees\nNo exaggeration",376,y+28,43,33,7.3,False,MUTED)
  label(l,'P01: trail/shore mismatch (~383m). P10/P11: no USFS trail.\nUse these three as research candidates, not aim points.',319,257,102,9,6.2,False,RUST)
 pr.layoutManager().addLayout(l);layout_records.append({'id':s['id'],'scale':m.scale(),'extent':m.extent().toString(),'num':idx+1})
# Final reference page
l=newlayout('06-fisheries');header(l,6,'What the lake records actually say','FISHERIES REGISTER  /  POSITIVE CATCHES, DATED STOCKING & DATA LIMITS');footer(l,6)
label(l,'Survey = latest returned standard fish-catch survey; newer temperature/oxygen visits are not fish population surveys.',12,36,400,6,9)
xs=[12,69,91,112,271];ws=[57,22,21,159,149]
heads=['LAKE / DNR ID','MAX FT¹','SURVEY','ANGLING SPECIES CAUGHT²','STOCKING REPORT³']
for x,w,h in zip(xs,ws,heads):box(l,x,46,w,9,INK);label(l,h,x+2,47,w-4,7,7.5,True,'#ffffff')
codes={'bluegill':'BG','green sunfish':'GS','hybrid sunfish':'HS','northern pike':'NP','smallmouth bass':'SMB','walleye':'WAE','yellow perch':'YP','lake trout':'LT','muskellunge':'MUS'}
for i,f in enumerate(fish):
 y=55+i*10.3
 for x,w in zip(xs,ws):box(l,x,y,w,10.3,'#edf0e6' if i%2==0 else PAPER)
 label(l,f["lake"],14,y+.4,54,4.8,8.2,True,BLUE);label(l,f['id'],14,y+5,54,4,6.2,False,MUTED)
 label(l,str(f['max_depth_ft']),71,y+2,18,6,9);label(l,str(f['survey_year']),93,y+2,19,6,8.5)
 species=', '.join(codes.get(s,s) for s in f['game_species']);label(l,species,114,y+2,153,6,8.5)
 stocks=f['stocking_records'];stock='No data in current 10-year report'
 if stocks:stock=stocks[0]['species']+': '+', '.join(str(r['year']) for r in stocks)
 label(l,stock,273,y+2,145,6,8)
 links.append({'page':5,'rect_mm':[12,y,408,10.3],'url':f['source_url']})
label(l,'READ THE LEGEND',12,194,135,7,11,True,RUST)
label(l,'LT lake trout  •  SMB smallmouth bass  •  NP northern pike\nWAE walleye  •  YP yellow perch  •  MUS muskellunge\nBG bluegill  •  GS green sunfish  •  HS hybrid sunfish\n[S] recent stocking record: Hungry Jack and Pine only\nGold F1/F2 stars: personal 2008 bass observations.\nDepth contours suggest structure, not proven fish locations.',12,204,194,39,8.1)
label(l,'EVIDENCE LIMITS',220,194,180,7,11,True,RUST)
label(l,'¹ Maximum depth is DNR lake metadata, not the deepest scan label.\n   Historical scans and metadata can disagree (e.g., East Pike).\n² Lake-wide catches, not mapped survey stations or current abundance.\n³ No recent stocking data does not mean never stocked.\nWatap: no DNR depth scan listed. Other scans may be old/incomplete.\nPortage silhouettes omit canopy; P04 has incomplete horizon coverage.',220,204,199,39,8)
label(l,'SOURCES & FULL DETAIL',12,246,150,6,9,True,RUST)
label(l,'DNR LakeFinder / lake maps & surveys  •  MnGeo second-generation lidar  •  USFS National Forest System Trails\nClickable lake rows open reports; depth panels open scans. Original depth PDFs are also embedded attachments. Full methods: README and docs/.',12,252,407,10,7.4)
pr.layoutManager().addLayout(l);layout_records.append({'id':'06-fisheries','num':6})
pr.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(*sheets[0]['bbox']),pr.crs()))
visible={q.id() for q in common}
for node in pr.layerTreeRoot().findLayers():node.setItemVisibilityChecked(node.layerId() in visible)
pr.setFileName(str(ROOT/'boundary-waters.qgz'));assert pr.write()
# Export text/vector maps; high-resolution depth scan images remain printable raster panels.
for rec in layout_records:
 l=pr.layoutManager().layoutByName(rec['id']);e=QgsLayoutExporter(l);settings=QgsLayoutExporter.PdfExportSettings();settings.dpi=600;settings.forceVectorOutput=True;settings.textRenderFormat=QgsRenderContext.TextFormatAlwaysText;settings.exportMetadata=True;settings.appendGeoreference=False
 result=e.exportToPdf(str(O/(rec['id']+'.pdf')),settings);assert result==QgsLayoutExporter.Success,result
 img=QgsLayoutExporter.ImageExportSettings();img.dpi=110;img.generateWorldFile=False;assert e.exportToImage(str(P/(rec['id']+'.png')),img)==QgsLayoutExporter.Success
 print('Exported',rec['id'],flush=True)
writer=PdfWriter()
for rec in layout_records:writer.append(str(O/(rec['id']+'.pdf')))
for ref in links:
 x,y,w,h=ref['rect_mm'];scale=72/25.4;rect=[x*scale,(279.4-y-h)*scale,(x+w)*scale,(279.4-y)*scale]
 ann=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),NameObject('/Rect'):ArrayObject([FloatObject(v) for v in rect]),NameObject('/Border'):ArrayObject([FloatObject(0)]*3),NameObject('/A'):DictionaryObject({NameObject('/S'):NameObject('/URI'),NameObject('/URI'):TextStringObject(ref['url'])})})
 writer.add_annotation(ref['page'],ann)
# PDF streams must be indirect objects. pypdf 3.4 add_attachment writes a
# direct embedded stream, which Poppler tolerates but Apple PDFKit rejects.
attachment_names=[]
for slug in sorted([s for group in depth_groups for s in group]):
 p=ROOT/panel[slug]['source'];name=slug+'-original-depth-map.pdf'
 stream=DecodedStreamObject();stream.set_data(p.read_bytes());stream[NameObject('/Type')]=NameObject('/EmbeddedFile')
 stream_ref=writer._add_object(stream)
 spec=DictionaryObject({NameObject('/Type'):NameObject('/Filespec'),NameObject('/F'):TextStringObject(name),NameObject('/UF'):TextStringObject(name),NameObject('/EF'):DictionaryObject({NameObject('/F'):stream_ref})})
 attachment_names.extend([TextStringObject(name),writer._add_object(spec)])
 names=writer._root_object.setdefault(NameObject('/Names'),DictionaryObject())
names[NameObject('/EmbeddedFiles')]=writer._add_object(DictionaryObject({NameObject('/Names'):ArrayObject(attachment_names)}))
writer.add_metadata({'/Title':'Boundary Waters | 2008 canoe route atlas','/Author':'pwdel/qgis','/Subject':'Historical trip, fisheries evidence, depth scans and experimental bare-earth portage views'})
with open(O/'boundary-waters-six-page-atlas.pdf','wb') as f:writer.write(f)
(D/'layouts.json').write_text(json.dumps(layout_records,indent=2));print('Saved project and six-page PDF',flush=True)
