"""Editable native QGIS projects and layouts, no rasterized map artwork."""
import json,math,gc,zipfile
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QFont
from qgis.PyQt.QtCore import Qt,QVariant
from shapely.geometry import shape
R=Path(__file__).resolve().parents[1];D=R/'data';O=R/'output/pdf'
app=QgsApplication([],False);app.initQgis();pr=QgsProject.instance()
crs=QgsCoordinateReferenceSystem();assert crs.createFromWkt('LOCAL_CS["Boundary Waters journey diagram - NOT GEOGRAPHIC",LOCAL_DATUM["Schematic origin",0],UNIT["diagram unit",1],AXIS["X",EAST],AXIS["Y",NORTH]]')
pr.setCrs(crs);pr.setFilePathStorage(Qgis.FilePathType.Relative);pr.setTitle('A Draught of the Eastern Lakes | Journey Network')
net=json.load(open(D/'network.json'));A=json.load(open(D/'assumptions.json'));INK='#111111'
def font(s,italic=False,bold=False):
 f=QFont('Baskerville');f.setPointSizeF(s);f.setItalic(italic);f.setBold(bold);return f
def line(w=.2,style='solid'):return QgsLineSymbol.createSimple({'line_color':INK,'line_width':str(w),'line_style':style,'capstyle':'round','joinstyle':'round'})
def text(lay,s,x,y,w,h,size=10,italic=False,bold=False):
 i=QgsLayoutItemLabel(lay);i.setText(s);i.setFont(font(size,italic,bold));i.setFontColor(QColor(INK));i.setMargin(0);lay.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,h));return i
def rule(lay,x,y,w,th=.15):
 i=QgsLayoutItemShape(lay);i.setShapeType(QgsLayoutItemShape.Shape.Rectangle);i.setSymbol(QgsFillSymbol.createSimple({'color':INK,'outline_style':'no'}));lay.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,th))
def labels(l,s,italic=False):
 l.renderer().setSymbol(QgsMarkerSymbol.createSimple({'size':'0','color':'transparent','outline_style':'no'}))
 p=QgsPalLayerSettings();p.fieldName='label';p.placement=Qgis.LabelPlacement.OverPoint;p.priority=10;p.displayAll=True
 f=QgsTextFormat();f.setFont(font(s,italic));f.setSize(s);f.setColor(QColor(INK));f.setLineHeight(1.1)
 b=QgsTextBufferSettings();b.setEnabled(True);b.setSize(.65);b.setColor(QColor('white'));f.setBuffer(b);p.setFormat(f)
 props=QgsPropertyCollection()
 for key,value in [(QgsPalLayerSettings.Property.PositionX,'x'),(QgsPalLayerSettings.Property.PositionY,'y')]:props.setProperty(key,QgsProperty.fromField(value))
 props.setProperty(QgsPalLayerSettings.Property.Hali,QgsProperty.fromExpression("'Center'"));props.setProperty(QgsPalLayerSettings.Property.Vali,QgsProperty.fromExpression("'Half'"));p.setDataDefinedProperties(props)
 l.setLabeling(QgsVectorLayerSimpleLabeling(p));l.setLabelsEnabled(True)
ls=[]
for file,title,kind,size in [('lakes','Lake puddles | approximate size classes','fill',0),('hatching','Engraved lake hatching','line',.08),('carries','Straight carries | double carry model','line',.22),('rivers','Water connections | not portages','dash',.25),('hills','Engraved terrain candidates','line',.12),('names','Lake names','label',12),('paddle-times','Hours between lettered connections','label',8),('carry-times','Carry letters, rods and hours','label',8),('hill-labels','High-ground reference IDs','label',8),('endpoints','S departure / T hypothetical turnaround','label',9)]:
 data=json.load(open(D/f'schematic-{file}.json'));features=data['features'];l=QgsVectorLayer(features[0]['geometry']['type'],title,'memory');l.setCrs(crs);provider=l.dataProvider()
 keys=list(dict.fromkeys(k for f in features for k in f['properties']));fields=[]
 for k in keys:
  v=next((f['properties'].get(k) for f in features if f['properties'].get(k) is not None),'')
  fields.append(QgsField(k,QVariant.Bool if isinstance(v,bool) else QVariant.Double if isinstance(v,(int,float)) else QVariant.String))
 provider.addAttributes(fields);l.updateFields()
 for f in features:
  qf=QgsFeature(l.fields());qf.setGeometry(QgsGeometry.fromWkt(shape(f['geometry']).wkt));qf.setAttributes([f['properties'].get(k) for k in keys]);provider.addFeatures([qf])
 l.updateExtents()
 options=QgsVectorFileWriter.SaveVectorOptions();options.driverName='GPKG';options.layerName=file;options.actionOnExistingFile=QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer if (D/'diagram.gpkg').exists() else QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
 result=QgsVectorFileWriter.writeAsVectorFormatV3(l,str(D/'diagram.gpkg'),pr.transformContext(),options);assert result[0]==QgsVectorFileWriter.WriterError.NoError,result
 l=QgsVectorLayer(str(D/'diagram.gpkg')+'|layername='+file,title,'ogr');assert l.isValid() and l.crs().isValid();assert not l.crs().isGeographic();pr.addMapLayer(l);l.setCustomProperty('teaching/coordinates','local diagram units; not geographic');ls.append(l)
 if kind=='fill':l.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'white','outline_color':INK,'outline_width':'.24','joinstyle':'round'}))
 elif kind in ['line','dash']:l.renderer().setSymbol(line(size,'dash' if kind=='dash' else 'solid'))
 else:labels(l,size,file in ['names','hill-labels'])
 l.saveNamedStyle(str(R/'styles'/f'{file}.qml'))
order=[ls[i] for i in [9,8,7,6,5,4,1,0,3,2]]
root=pr.layerTreeRoot();root.setHasCustomLayerOrder(True);root.setCustomLayerOrder(order)
pr.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(0,0,404,210),crs));pr.setBackgroundColor(QColor('white'))
def layout(name,subtitle):
 lay=QgsPrintLayout(pr);lay.initializeDefaults();lay.setName(name);lay.pageCollection().page(0).setPageSize(QgsLayoutSize(431.8,279.4));pr.layoutManager().addLayout(lay)
 text(lay,'A DRAUGHT OF THE EASTERN LAKES',14,8,330,7,10,False,True)
 text(lay,'The Canoe Traveller\'s Network',14,16,330,14,27)
 text(lay,subtitle,15,31,395,7,9,True);rule(lay,15,40,402,.22)
 return lay
lay=layout('01 | The journey chart','Seventeen lakes about Clearwater  /  Connections & travelling hours  /  A modern hypothetical exercise')
m=QgsLayoutItemMap(lay);lay.addLayoutItem(m);m.setId('schematic-map');m.attemptMove(QgsLayoutPoint(14,43));m.attemptResize(QgsLayoutSize(404,210));m.setCrs(crs);m.setLayers(order);m.setKeepLayerSet(True);m.setKeepLayerStyles(True);m.zoomToExtent(QgsRectangle(0,0,404,210));m.setBackgroundColor(QColor('white'))
text(lay,'THE NORTHERN CHAIN',304,49,107,6,9,True)
text(lay,'Small puddles stand for lakes.\nLetters name their connecting passages.\nRead a-b as the crossing from a to b.',304,58,109,18,9)
rule(lay,15,252,402,.2)
text(lay,'READING THE DRAUGHT',15,255,75,6,9,False,True)
text(lay,'Lake figures: paddling hours between letters.  Straight links: carry rods (~) & double-carry hours.\nS = Clearwater departure; T = imagined turning place.  * = approximate carry geometry.  Dashed = water link.',15,262,252,11,8)
text(lay,'Not to scale: take no bearings from this drawing.\nWindbound? Wait; that time is outside these ranges.\nGeographic companion & full assumptions in the project.',281,256,137,18,8,True)
# Instructor pages use native QGIS text items for editable tabular content.
key=layout('02 | Timing and itineraries','The instructor\'s key  /  Ordinary tandem team  /  Double carries  /  Model assumptions, not observed travel times')
text(key,'I.  THREE PRE-DESIGNED JOURNEYS',15,47,210,8,13,False,True)
y=59
for r,desc in zip(net['routes'],['Clearwater - West Pike - Pine - Little Caribou - Caribou - Clearwater','Clearwater - West Pike - East Pike - John - Little John - McFarland\nPine - Little Caribou - Caribou - Clearwater','Clearwater - Mountain - Watap - Rove - Rose; return by the same chain']):
 text(key,r['name']+'  /  '+r['display'],15,y,250,7,12);text(key,desc,15,y+8,250,13,9,True);y+=29
text(key,'Totals are moving + handling hours, not days or daily targets.\nRest, camps, queues, difficult weather and windbound waits add time.\nBoth directions use the same broad scenario envelope; wind direction\nchanges which end of the range is plausible.',15,149,235,25,10)
text(key,'II.  HOW THE HOURS ARE RECKONED',15,184,230,8,13,False,True)
model_note = f"""Paddle: geographic water-path distance, plus 15-30% indirect travel;
20-35% on more winding paths. Divide by {A['paddle_kmh'][0]:g} km/h (favourable) or
{A['paddle_kmh'][1]:g} km/h (adverse but travelable). These are teaching assumptions.

Carry: {A['carry_traversals'][0]} loaded walks at {A['loaded_walk_kmh'][1]:g}-{A['loaded_walk_kmh'][0]:g} km/h, {A['carry_traversals'][1]} return at {A['return_walk_kmh'][1]:g}-{A['return_walk_kmh'][0]:g} km/h,
plus {A['handling_minutes'][0]:g}-{A['handling_minutes'][1]:g} minutes of handling per connection. One rod = {A['rod_metres']:g} m.

Bounds round outward to quarter hours. A 0-0.25 h label means
a brief nonzero leg. All rod counts are derived, not official counts."""
text(key,model_note,15,197,246,61,10)
text(key,'III.  HIGH GROUND & UNCERTAINTY',277,47,140,8,13,False,True)
source={f['properties']['id']:f['properties'] for f in json.load(open(D/'geographic-high-points.geojson'))['features']}
y=59
for f in json.load(open(D/'schematic-hill-labels.json'))['features']:
 p=f['properties'];g=source[p['source_id']];text(key,p['label']+'  /  near '+g['near_lake'],277,y,138,7,10);y+=8
text(key,'These are bare-earth terrain candidates, not verified\nvisible peaks. Tree cover can obscure them. Their\nschematic placement is illustrative; use the separate\ngeographic project for true positions and bearings.',277,y+5,139,28,9)
text(key,'Carry a: USFS line is incomplete; published digitized\nGPX supplies an approximate full passage.\nCarries h and i: published sketches, no matching\nUSFS geometry. Water links f and m are not carries.\n\nClearwater-Deer was omitted: the recorded trail\nstops short of the lakes. Deer connects via Caribou.\n\nRose is a terminal branch. Its T point, like those on\nDeer, Alder and Crystal, is a hypothetical water\nturnaround, not a campsite or landing.',277,153,139,66,9)
text(key,'SOURCES & REPRODUCTION',277,231,139,7,10,False,True)
text(key,'MN DNR waters / USFS trails / MnGeo terrain\nFriends of BWCA digitized loop / Parks Canada history\nTiming context: Poudre Paddlers; NPS wind variability\nFull citations and limitations: docs/SOURCES.md',277,241,139,24,8)
rule(key,15,267,402);text(key,'Model version: 12 October 2026  |  Geographic measurements and diagram units are kept separate.',15,270,390,5,7)
# Tables: two leg pages, no clipped cells, all 51 records referenced.
rows=net['legs'];chunks=[rows[i:i+26] for i in range(0,len(rows),26)]
for idx,chunk in enumerate(chunks):
 table=layout(f'{3+idx:02} | Leg register','The reckoning of each passage  /  Source-backed distances; modeled hours  /  All distances below are geographic')
 headers=[('ID',15),('Lake / connection',31),('Points',150),('Mode',179),('Base km',222),('Extra paddle',257),('Hours',304),('Evidence',352)]
 for s,x in headers:text(table,s,x,47,65,7,10,False,True)
 rule(table,15,56,402)
 for i,r in enumerate(chunk):
  y=60+i*7.1;n=r['from_lake'] if r['mode']=='paddle' else r['from_lake']+' / '+r['to_lake']
  evidence='water model' if r['mode']=='paddle' else 'approximate*' if r['approximate'] else 'USFS + shore'
  vals=[r['id'],n,r['from_point']+'-'+r['to_point'] if r['mode']=='paddle' else '',r['mode'],('<0.01' if 0<r['distance_m']<10 else f"{r['distance_m']/1000:.2f}"),f"{100*r['detour_low']:.0f}-{100*r['detour_high']:.0f}%" if r['mode']=='paddle' else '-',('same landing' if r['mode']=='paddle' and r['distance_m']<1 else r['display']),evidence]
  for (s,x),v in zip(headers,vals):text(table,v,x,y,120 if x==31 else 65,6,9)
  rule(table,15,y+6.5,402,.04)
 text(table,'* Approximate passage sketches or short water links. Full source records, exact hours and assumptions: data/leg-times.csv.',15,254,402,8,8,True)
 text(table,'Paddle points are identified by the connecting letters on the chart. S = departure; T = hypothetical turning place.',15,264,402,7,8)
# Save project and portable templates.
for ext in ['qgz','qgs']:
 pr.setFileName(str(R/f'journey-network.{ext}'));assert pr.write()
for lay in pr.layoutManager().layouts():
 fn=lay.name().split(' | ')[0];ctx=QgsReadWriteContext();ctx.setPathResolver(QgsPathResolver(str(R/'layouts'/f'{fn}.qpt')));lay.saveAsTemplate(str(R/'layouts'/f'{fn}.qpt'),ctx)
 ex=QgsLayoutExporter(lay);s=QgsLayoutExporter.PdfExportSettings();s.dpi=300;s.forceVectorOutput=True;s.textRenderFormat=Qgis.TextRenderFormat.AlwaysText;s.appendGeoreference=False
 assert ex.exportToPdf(str(O/f'sheet-{fn}.pdf'),s)==QgsLayoutExporter.ExportResult.Success
 print('Export',fn,flush=True)
# Separate true-coordinate project; no schematic layers in it.
del ex,lay,m,key,table
pr.clear();crsg=QgsCoordinateReferenceSystem('EPSG:26915');pr.setCrs(crsg);pr.setFilePathStorage(Qgis.FilePathType.Relative);pr.setTitle('Journey network | geographic measurement evidence')
for n,title,kind in [('lakes','Geographic lakes','fill'),('connections','Recorded or approximate connections','line'),('modeled-connections','Length model with straight shoreline extensions (hidden)','dash'),('paddles','Hypothetical base water paths','dash'),('landings','Source-derived landings and hypothetical turns','point'),('high-points','Terrain candidates (visibility unverified)','point')]:
 l=QgsVectorLayer(str(D/f'geographic-{n}.geojson'),title,'ogr');assert l.isValid();pr.addMapLayer(l)
 if kind=='fill':l.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'white','outline_color':'black','outline_width':'.2'}));extent=l.extent()
 elif kind in ['line','dash']:l.renderer().setSymbol(line(.3,'dash' if kind=='dash' else 'solid'))
 else:l.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'triangle' if n=='high-points' else 'circle','size':'2','color':'white','outline_color':'black'}))

for node in pr.layerTreeRoot().findLayers():
 if 'shoreline extensions' in node.layer().name():node.setItemVisibilityChecked(False)
pr.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent,crsg));pr.setFileName(str(R/'geographic-evidence.qgz'));assert pr.write()
# Normalize QGIS layout fallback references as well as ordinary datasource paths.
for p in R.glob('*.qgs'):p.write_text(p.read_text().replace(str(R)+'/', './'))
for p in (R/'layouts').glob('*.qpt'):p.write_text(p.read_text().replace(str(R)+'/', '../'))
for p in R.glob('*.qgz'):
 temp=p.with_suffix('.tmp')
 with zipfile.ZipFile(p) as src,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as dst:
  for info in src.infolist():
   data=src.read(info.filename)
   if info.filename.endswith('.qgs'):data=data.decode().replace(str(R)+'/', './').encode()
   dst.writestr(info,data)
 temp.replace(p)
pr.clear();del l,ls,order,root;gc.collect();app.exitQgis()
