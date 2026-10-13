"""Native QGIS 4 project, styles, editable print layouts, and monochrome charts."""
import json,math,os
from pathlib import Path
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QFont
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtXml import QDomDocument
R=Path(__file__).resolve().parents[1];D=R/'derived';O=R/'output/pdf';P=R/'previews'
for d in [R/'styles',R/'layouts',O,P]:d.mkdir(exist_ok=True,parents=True)
app=QgsApplication([],False);app.initQgis();pr=QgsProject.instance();crs=QgsCoordinateReferenceSystem('EPSG:26915');pr.setCrs(crs);pr.setFilePathStorage(Qgis.FilePathType.Relative)
pr.setTitle('A Draught of Clearwater & the Eastern Lakes | Navigation Exercises')
meta=json.loads((D/'map-data.json').read_text());mag=json.loads((R/'sources/magnetic-model.json').read_text())['response']['geomagnetic-field-model-result']['field-value']['declination']['value'];gamma=meta['grid_convergence_deg']
student_group=pr.layerTreeRoot().addGroup('STUDENT | ink chart & broad clues')
instructor_group=pr.layerTreeRoot().addGroup('INSTRUCTOR | answers & source evidence (hidden)')
reference_group=pr.layerTreeRoot().addGroup('REFERENCE | elevation raster (hidden)')
FONT='Baskerville';INK='#171717'
def font(size,italic=False,bold=False):
 f=QFont(FONT);f.setPointSizeF(size);f.setItalic(italic);f.setBold(bold);return f
def labelstyle(layer,field,size,italic=False):
 p=QgsPalLayerSettings();p.fieldName=field;p.priority=8
 f=QgsTextFormat();f.setFont(font(size,italic));f.setSize(size);f.setColor(QColor(INK))
 b=QgsTextBufferSettings();b.setEnabled(True);b.setSize(.6);b.setColor(QColor('white'));f.setBuffer(b);p.setFormat(f)
 if layer.geometryType()==Qgis.GeometryType.Point:p.placement=Qgis.LabelPlacement.OrderedPositionsAroundPoint;p.dist=1.1
 else:p.placement=Qgis.LabelPlacement.OverPoint
 layer.setLabeling(QgsVectorLayerSimpleLabeling(p));layer.setLabelsEnabled(True)
def line(width=.2,style='solid',color=INK):return QgsLineSymbol.createSimple({'line_color':color,'line_width':str(width),'line_style':style,'capstyle':'round','joinstyle':'round'})
def layer(file,title,role='student'):
 l=QgsVectorLayer(str(D/(file+'.geojson')),title,'ogr');assert l.isValid(),file
 pr.addMapLayer(l,False);(student_group if role=='student' else instructor_group).addLayer(l);l.setCustomProperty('teaching/role',role);l.setCustomProperty('teaching/file',file)
 md=l.metadata();md.setTitle(title);md.setAbstract('Clearwater teaching experiment. See README.md and docs/geometry-validation.json for provenance and limitations.');l.setMetadata(md)
 return l
context=layer('context-water','Neighbouring waters');context.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'white','outline_color':'#777777','outline_width':'.13'}))
lakes=layer('lakes','Lake shore');lakes.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'white','outline_color':INK,'outline_width':'.25','joinstyle':'round'}))
echo=layer('shore-echo','Engraved shore accents');echo.renderer().setSymbol(line(.075,color='#666666'))
hach=layer('hachures','Hill hachures');hach.renderer().setSymbol(line(.105,color='#555555'))
clues=layer('clues','Passage clue area');clues.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':INK,'outline_width':'.23','outline_style':'dot'}));labelstyle(clues,'label',11,True)
high=layer('high-points','High ground (metres)');high.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'triangle','color':'white','outline_color':INK,'outline_width':'.3','size':'2.2'}));labelstyle(high,'label',8)
labels=layer('lake-labels','Lake names');labels.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','size':'0','color':'transparent','outline_style':'no'}));labelstyle(labels,'label',13,True)
start=layer('start','Departure / return');start.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'diamond','color':INK,'outline_color':'white','outline_width':'.35','size':'3.4'}));labelstyle(start,'label',9,True)
recorded=layer('portages-recorded','Recorded trail segments','instructor');recorded.renderer().setSymbol(line(.48,'dash'))
approx=layer('passages-approximate','Approximate passage sketches','instructor');approx.renderer().setSymbol(line(.38,'dot'))
lands=layer('landings-instructor','Candidate landings','instructor');lands.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','size':'1.8','color':'white','outline_color':INK,'outline_width':'.3'}))
ra=layer('route-a','A | Inner circuit paddling','instructor');ra.renderer().setSymbol(line(.38,'dash'))
rb=layer('route-b','B | Eastern circuit paddling','instructor');rb.renderer().setSymbol(line(.35,'dash dot'))
sights=layer('terrain-sightlines','Terrain-only reference sightlines','instructor');sights.renderer().setSymbol(line(.18,'dot',color='#777777'))
terrain=QgsRasterLayer(str(R/'sources/lidar-route-8m.tif'),'Source elevation | 8m bare earth');assert terrain.isValid();pr.addMapLayer(terrain,False);reference_group.addLayer(terrain);terrain.setCustomProperty('teaching/role','reference')
# All loaded layers use the project CRS. Save source transform for documented reuse.
src=QgsCoordinateReferenceSystem('EPSG:4326');ops=QgsDatumTransform.operations(src,crs);op=next(x for x in ops if '(1)' in x.name and x.isAvailable)
ctx=pr.transformContext();ctx.addCoordinateOperation(src,crs,op.proj,False);pr.setTransformContext(ctx)
base=[start,high,labels,clues,echo,lakes,hach]
answers=[lands,recorded,approx,ra,rb]+base
for l in pr.mapLayers().values():
 if isinstance(l,QgsVectorLayer):l.saveNamedStyle(str(R/'styles'/(l.customProperty('teaching/file')+'.qml')))
# A native vector compass asset; geographic positions remain true to the GIS data.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="160" height="170" viewBox="0 0 160 170"><g transform="translate(80 86)">']
svg.append('<circle r="43" fill="white" stroke="#171717" stroke-width=".8"/>')
for i in range(16):
 a=i*22.5;length=57 if i%4==0 else (43 if i%2==0 else 29);width=7 if i%4==0 else 4
 svg.append(f'<g transform="rotate({a-gamma})"><path d="M 0 {-length} L {-width} 0 L 0 12 Z" fill="#171717"/><path d="M 0 {-length} L {width} 0 L 0 12 Z" fill="white" stroke="#171717" stroke-width=".6"/></g>')
svg.append('</g><g font-family="Baskerville,serif" font-size="16" text-anchor="middle"><text x="78" y="17">N</text><text x="147" y="92">E</text><text x="82" y="165">S</text><text x="12" y="92">W</text></g></svg>')
(R/'styles/compass.svg').write_text(''.join(svg))

def text(layout,s,x,y,w,h,size=10,italic=False,bold=False):
 i=QgsLayoutItemLabel(layout);i.setText(s);i.setFont(font(size,italic,bold));i.setFontColor(QColor(INK));i.setMargin(0);layout.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,h));return i
def rect(layout,x,y,w,h):
 i=QgsLayoutItemShape(layout);i.setShapeType(QgsLayoutItemShape.Shape.Rectangle);i.setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':INK,'outline_width':'.16'}));layout.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));i.attemptResize(QgsLayoutSize(w,h));return i
from qgis.PyQt.QtCore import QPointF
from qgis.PyQt.QtGui import QPolygonF
def rule(layout,x,y,w,stroke=.15):
 i=QgsLayoutItemPolyline(QPolygonF([QPointF(0,0),QPointF(w,0)]),layout);i.setSymbol(line(stroke));layout.addLayoutItem(i);i.attemptMove(QgsLayoutPoint(x,y));return i

def setvisible(ls):
 ids={l.id() for l in ls}
 for node in pr.layerTreeRoot().findLayers():node.setItemVisibilityChecked(node.layerId() in ids)
for name,ls in [('Student | clues only',base),('Instructor | both circuits',answers),('Instructor | circuit A',[lands,recorded,approx,ra]+base),('Instructor | circuit B',[lands,recorded,approx,rb]+base)]:
 setvisible(ls)
 model=QgsLayerTreeModel(pr.layerTreeRoot())
 record=QgsMapThemeCollection.createThemeFromCurrentState(pr.layerTreeRoot(),model)
 pr.mapThemeCollection().insert(name,record)

full=meta['extent'];west=[full[0],full[1]+300,712250,full[3]];east=[709100,full[1],full[2],full[3]-100]
pages=[('01','All the eastern lakes',full),('02','Clearwater & the inner circuit',west),('03','The Pike lakes & eastern passage',east)]
records=[]
for audience in ['Student','Instructor']:
 for num,title,bounds in (pages if audience=='Student' else [('01','Circuit A - the inner loop',full),('02','Circuit B - the eastern loop',full),('03','Circuit A - Clearwater & inner passage',west),('04','Circuit B - the eastern passage',east)]):
  route_layer=ra if num in ['01','03'] else rb
  active_answers=[lands,recorded,approx,route_layer]+base
  name=f'{audience} {num} - {title}'
  lay=QgsPrintLayout(pr);lay.initializeDefaults();lay.setName(name);lay.pageCollection().pages()[0].setPageSize(QgsLayoutSize(431.8,279.4));lay.renderContext().setDpi(300)
  text(lay,'A DRAUGHT OF',15,7,250,8,10,False,True)
  text(lay,'Clearwater & the Eastern Lakes',14,16,335,16,28)
  text(lay,title+'  /  A study in compass, distance & observation',15,34,330,8,11,True)
  text(lay,('THE EXERCISE' if audience=='Student' else 'THE INSTRUCTOR\'S KEY')+f'   /   {num}',338,12,79,8,9,False,True)
  text(lay,'Canoe country, Minnesota\nA modern chart in the manner of an old draught',338,24,79,14,8,True)
  rule(lay,15,45,402,.3)
  m=QgsLayoutItemMap(lay);lay.addLayoutItem(m);m.setId('teaching-map');m.attemptMove(QgsLayoutPoint(15,51));m.attemptResize(QgsLayoutSize(402,151));m.setCrs(crs);m.setLayers(base if audience=='Student' else active_answers);m.setKeepLayerSet(True);m.setKeepLayerStyles(True);m.zoomToExtent(QgsRectangle(*bounds));m.setBackgroundColor(QColor('white'));m.setFrameEnabled(True);m.setFrameStrokeWidth(QgsLayoutMeasurement(.18));m.setFrameStrokeColor(QColor(INK))
  grid=m.grid();grid.setEnabled(True);grid.setCrs(crs);grid.setIntervalX(1000);grid.setIntervalY(1000);grid.setStyle(QgsLayoutItemMapGrid.GridStyle.Cross);grid.setCrossLength(.45);grid.setLineSymbol(line(.08,color='#777777'));grid.setAnnotationEnabled(True);grid.setAnnotationPrecision(0);grid.setAnnotationFont(font(6));grid.setAnnotationFormat(QgsLayoutItemMapGrid.AnnotationFormat.Decimal)
  for side in [QgsLayoutItemMapGrid.BorderSide.Left,QgsLayoutItemMapGrid.BorderSide.Right,QgsLayoutItemMapGrid.BorderSide.Top,QgsLayoutItemMapGrid.BorderSide.Bottom]:
   grid.setAnnotationPosition(QgsLayoutItemMapGrid.AnnotationPosition.InsideMapFrame,side)
  grid.setAnnotationDisplay(QgsLayoutItemMapGrid.DisplayMode.HideAll,QgsLayoutItemMapGrid.BorderSide.Top);grid.setAnnotationDisplay(QgsLayoutItemMapGrid.DisplayMode.HideAll,QgsLayoutItemMapGrid.BorderSide.Right)
  pic=QgsLayoutItemPicture(lay);lay.addLayoutItem(pic);pic.attemptMove(QgsLayoutPoint(389,55));pic.attemptResize(QgsLayoutSize(22,24));pic.setPicturePath(str(R/'styles/compass.svg'));text(lay,'True north',389,80,25,5,6,True)
  bar=QgsLayoutItemScaleBar(lay);bar.setStyle('Line Ticks Middle');bar.setLinkedMap(m);bar.applyDefaultSize();bar.setUnits(Qgis.DistanceUnit.Kilometers);bar.setUnitsPerSegment(1);bar.setNumberOfSegments(2);bar.setNumberOfSegmentsLeft(0);bar.setUnitLabel('km');fmt=QgsTextFormat();fmt.setFont(font(8));fmt.setSize(8);bar.setTextFormat(fmt);bar.setHeight(1.5);lay.addLayoutItem(bar);bar.attemptMove(QgsLayoutPoint(350,180));bar.setBackgroundEnabled(True);bar.setBackgroundColor(QColor('white'));bar.setBoxContentSpace(1)
  # Bottom three-column apparatus, deliberately restrained to leave the map dominant.
  text(lay,'I.  THE TWO CIRCUITS',15,209,125,7,11,False,True)
  text(lay,'A  Clearwater - West Pike - Pine\n     Little Caribou - Caribou - Clearwater\nB  Clearwater - West Pike - East Pike - John\n     Little John - McFarland - Pine\n     Little Caribou - Caribou - Clearwater',15,219,130,31,9)
  text(lay,'Trace your course in pencil; choose the carries from the clues.',15,250,130,8,7.4,True)
  text(lay,'II.  BY COMPASS & RULE',156,209,120,7,11,False,True)
  text(lay,f'Grid crosses are 1 km apart. Map is grid-north up.\nAt chart centre: true bearing = grid bearing + {gamma:.1f}°.\nMagnetic bearing = grid bearing + {gamma-mag:.1f}°.\nVariation {abs(mag):.1f}° W; WMM2025, 12 October 2026.\nMeasure two landmark bearings; pencil their back-bearings.',156,219,126,31,9)
  text(lay,'Print at 100%. The line below must measure 50 mm.',156,250,128,5,7.4,True);rule(lay,156,259,50,.25)
  text(lay,'III.  SIGNS & OBSERVATIONS',293,209,125,7,11,False,True)
  legend=QgsLayoutItemLegend(lay);legend.setTitle('');legend.setAutoUpdateModel(False);legend.setLinkedMap(m);root=legend.model().rootGroup();root.clear()
  for l in ([clues,high,start] if audience=='Student' else [recorded,approx,route_layer]):root.addLayer(l)
  legend.setStyleFont(QgsLegendStyle.Style.SymbolLabel,font(8));legend.setStyleFont(QgsLegendStyle.Style.Subgroup,font(8));legend.setSymbolWidth(7);legend.setSymbolHeight(2);legend.setBoxSpace(0);lay.addLayoutItem(legend);legend.attemptMove(QgsLayoutPoint(293,220));legend.attemptResize(QgsLayoutSize(125,20))
  if audience=='Student':note='Dotted areas are broad clues, not exact landing positions.\nH points and hachures show bare-earth high ground.\nTree cover and landmark recognition are unverified.'
  else:note='Trail and landing evidence is not field verified.\nDotted sketches include gaps in the USFS record.\nWater legs are hypothetical, not surveyed tracks.'
  text(lay,note,293,242,125,16,7.7,True)
  rule(lay,15,264,402,.2)
  text(lay,'EXPERIMENTAL TEACHING CHART  |  Exact carries deliberately withheld from the student edition.',15,268,260,5,7,False,True)
  text(lay,'MN DNR waters / USFS trails 2026-10-12 / MnGeo lidar 8 m / BGS WMM2025\nNAD83 / UTM 15N (EPSG:26915); source notes & evidence: README and docs/',280,267,137,9,6.4)
  pr.layoutManager().addLayout(lay)
  template_path=R/'layouts'/(audience.lower()+'-'+num+'.qpt'); template_context=QgsReadWriteContext(); template_context.setPathResolver(QgsPathResolver(str(template_path))); lay.saveAsTemplate(str(template_path),template_context); template_path.write_text(template_path.read_text().replace(str(R)+'/', '../'))
  records.append({'name':name,'audience':audience,'num':num,'scale':m.scale(),'extent':[m.extent().xMinimum(),m.extent().yMinimum(),m.extent().xMaximum(),m.extent().yMaximum()]})
setvisible(base);instructor_group.setItemVisibilityChecked(False);reference_group.setItemVisibilityChecked(False)
pr.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(*full),crs));pr.setBackgroundColor(QColor('white'))
pr.setFileName(str(R/'clearwater-navigation.qgz'));assert pr.write()
pr.setFileName(str(R/'clearwater-navigation.qgs'));assert pr.write()
from portable_paths import normalize
normalize(R)
(D/'layouts.json').write_text(json.dumps(records,indent=2))
for rec in records:
 lay=pr.layoutManager().layoutByName(rec['name']);export=QgsLayoutExporter(lay);settings=QgsLayoutExporter.PdfExportSettings();settings.dpi=300;settings.forceVectorOutput=True;settings.textRenderFormat=Qgis.TextRenderFormat.AlwaysText;settings.appendGeoreference=False;settings.exportMetadata=True
 fn=rec['audience'].lower()+'-'+rec['num'];result=export.exportToPdf(str(O/(fn+'.pdf')),settings);assert result==QgsLayoutExporter.ExportResult.Success,result
 img=QgsLayoutExporter.ImageExportSettings();img.dpi=120;img.generateWorldFile=False;assert export.exportToImage(str(P/(fn+'.png')),img)==QgsLayoutExporter.ExportResult.Success
 print('Exported',fn,flush=True)
print('Saved QGZ, QGS, seven QPT layouts and styles',flush=True)
