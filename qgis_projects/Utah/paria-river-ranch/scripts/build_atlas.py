"""Build a portable QGIS project and four print-first equestrian planning sheets."""
import json
import math
import os
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import numpy as np
from osgeo import gdal, ogr, osr
from qgis.core import *
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import Qt
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from pypdf.generic import AnnotationBuilder

ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'sources'; D=ROOT/'derived'; O=ROOT/'output'/'pdf'
for p in [D,O,ROOT/'previews']:p.mkdir(parents=True,exist_ok=True)
gdal.UseExceptions()
app=QgsApplication([],False);app.initQgis()
project=QgsProject.instance();project.setCrs(QgsCoordinateReferenceSystem('EPSG:26912'))
project.setFilePathStorage(Qgis.FilePathType.Relative)
project.setTitle('Paria River Ranch | Utah equestrian planning atlas')
INK='#273d39';RUST='#9c5433';BLUE='#16768b';GOLD='#c17c21';PURPLE='#823b71'

def terrain(name):
    src=S/(name+'-dem.tif')
    gdal.DEMProcessing(str(D/(name+'-hillshade.tif')),str(src),'hillshade',
      creationOptions=['COMPRESS=DEFLATE'],computeEdges=False)
    gdal.DEMProcessing(str(D/(name+'-slope-degrees.tif')),str(src),'slope',
      creationOptions=['COMPRESS=DEFLATE'],computeEdges=False)
    ds=gdal.Open(str(src));a=ds.ReadAsArray();nd=ds.GetRasterBand(1).GetNoDataValue()
    valid=np.isfinite(a)&(a!=nd) if nd is not None else np.isfinite(a)
    return dict(pixel_size_m=list(map(abs,[ds.GetGeoTransform()[1],ds.GetGeoTransform()[5]])),
        valid_fraction=float(valid.mean()),min_m=float(a[valid].min()),max_m=float(a[valid].max()),
        native_resolution='Unresolved service mosaic' if name!='thunder-native' else '1m source product, reprojected at 1m')

terrain_stats={}
for n in ['01-region','02-ranch','03-mount-carmel','04-red-canyon']:
    terrain_stats[n]=terrain(n)
if (S/'thunder-native-1m.tif').exists():
    gdal.DEMProcessing(str(D/'thunder-native-slope-degrees.tif'),str(S/'thunder-native-1m.tif'),'slope',
      creationOptions=['COMPRESS=DEFLATE'],computeEdges=False)
    gdal.DEMProcessing(str(D/'thunder-native-hillshade.tif'),str(S/'thunder-native-1m.tif'),'hillshade',
      creationOptions=['COMPRESS=DEFLATE'],computeEdges=False)
    slope=gdal.Open(str(D/'thunder-native-slope-degrees.tif'));a=slope.ReadAsArray()
    good=np.isfinite(a)&(a>=0)&(a<=90)
    terrain_stats['native']={'pixel_size_m':1,'valid_fraction':float(good.mean()),
      'over_30_fraction':float(((a>=30)&good).sum()/good.sum()),
      'over_45_fraction':float(((a>=45)&good).sum()/good.sum()),
      'interpretation':'Whole crop terrain cell slopes; not trail grade or a recommended avoidance boundary.'}
    out=gdal.GetDriverByName('GTiff').Create(str(D/'thunder-slope-screen.tif'),a.shape[1],a.shape[0],4,gdal.GDT_Byte,options=['COMPRESS=DEFLATE'])
    out.SetProjection(slope.GetProjection());out.SetGeoTransform(slope.GetGeoTransform())
    rgba=np.zeros((4,*a.shape),dtype='uint8')
    # Missing samples must not be confused with low slopes inside the analysis footprint.
    for b,c in enumerate((110,110,110,95)):rgba[b][~good]=c
    for low,high,color in [(30,45,(217,150,38,120)),(45,91,(135,48,99,160))]:
        mask=(a>=low)&(a<high)&good
        for b,c in enumerate(color):rgba[b][mask]=c
    for b in range(4):out.GetRasterBand(b+1).WriteArray(rgba[b])
    out.GetRasterBand(4).SetColorInterpretation(gdal.GCI_AlphaBand);out=None
(ROOT/'docs'/'terrain-analysis.json').write_text(json.dumps(terrain_stats,indent=2)+'\n')

# Portable curated vector layers; source-native originals remain separately preserved.
gpkg=D/'atlas.gpkg'
if gpkg.exists():gpkg.unlink()
vector_names=['planning-points','roads','state-trails','usfs-trails','trailheads','lidar-coverage']
for i,n in enumerate(vector_names):
    opts=dict(format='GPKG',layerName=n.replace('-','_'),dstSRS='EPSG:26912',options=['-mapFieldType','StringList=String'])
    if i:opts['accessMode']='update'
    gdal.VectorTranslate(str(gpkg),str(S/(n+'.geojson')),**opts)

def vector(name,title):
    l=QgsVectorLayer(str(gpkg)+'|layername='+name.replace('-','_'),title,'ogr')
    assert l.isValid(),title
    project.addMapLayer(l);return l
def raster(path,title):
    l=QgsRasterLayer(str(path),title);assert l.isValid(),str(path)
    project.addMapLayer(l);return l
def line(color,width=.4,dash=False):
    return QgsLineSymbol.createSimple({'line_color':color,'line_width':str(width),'line_style':'dash' if dash else 'solid'})
def labels(l,field,size=9,color=INK):
    p=QgsPalLayerSettings();p.fieldName=field
    if l.geometryType()==QgsWkbTypes.LineGeometry:
        p.placement=QgsPalLayerSettings.Line;p.mergeLines=True;p.repeatDistance=80;p.priority=4
    elif l.geometryType()==QgsWkbTypes.PolygonGeometry:
        p.placement=QgsPalLayerSettings.Horizontal;p.priority=10;p.displayAll=True
    f=QgsTextFormat();f.setFont(QFont('DejaVu Sans',size));f.setSize(size);f.setColor(QColor(color))
    b=QgsTextBufferSettings();b.setEnabled(True);b.setSize(.8);b.setColor(QColor('#fffdf7'));f.setBuffer(b)
    p.setFormat(f);l.setLabeling(QgsVectorLayerSimpleLabeling(p));l.setLabelsEnabled(True)

roads=vector('roads','Road classes | trailer fit unverified')
root=QgsRuleBasedRenderer.Rule(None)
for text,expr,col,w,dash in [
 ('US/state highways','to_int("CARTOCODE") >= 1 AND to_int("CARTOCODE") <= 6',RUST,.6,False),
 ('Major unpaved roads','"CARTOCODE" = \'9\'','#b78339',.55,True),
 ('Published high-clearance / 4WD','"CARTOCODE" = \'16\'','#a52d36',.5,True),
 ('Other mapped roads','to_int("CARTOCODE") >= 7 AND to_int("CARTOCODE") <= 18 AND "CARTOCODE" NOT IN (\'9\',\'16\')','#96745a',.22,True)]:
    assert not QgsExpression(expr).hasParserError(),expr
    root.appendChild(QgsRuleBasedRenderer.Rule(line(col,w,dash),filterExp=expr,label=text))
roads.setRenderer(QgsRuleBasedRenderer(root))
road_labels=roads.clone();road_labels.setName('Named approach roads | source names')
road_labels.setSubsetString("\"FULLNAME\" IN ('HWY 89','HWY 12','HWY 9','TOM BEST SPRING RD','COTTONWOOD CANYON','EAST FORK RD')")
labels(road_labels,'FULLNAME',9,RUST);project.addMapLayer(road_labels)
trails=vector('state-trails','State trails | published horse-use attributes')
root=QgsRuleBasedRenderer.Rule(None)
for text,expr,col,w in [('HorseAllowed = Yes (mapping)','"HorseAllowed" = \'Yes\'',BLUE,.65),
                       ('Other paths | horse status unresolved','"HorseAllowed" IS NULL OR "HorseAllowed" != \'Yes\'','#6d6b66',.3)]:
    root.appendChild(QgsRuleBasedRenderer.Rule(line(col,w,True),filterExp=expr,label=text))
trails.setRenderer(QgsRuleBasedRenderer(root))
usfs=vector('usfs-trails','USFS trail records | inspect attributes')
usfs.renderer().setSymbol(line('#5b6f63',.3,True))
heads=vector('trailheads','All source trailhead references')
heads.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'square','color':'#ffffff','outline_color':INK,'size':'2'}))
coverage=vector('lidar-coverage','Lidar coverage | source discovery')
coverage.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':'#705686','outline_width':'.3'}))
points=vector('planning-points','Planning references | critical evidence')
cats=[]
for value,col,shape in [('AdvertisedPotable',BLUE,'diamond'),('SeasonalStockOnly',GOLD,'diamond'),
                       ('SurfaceWaterUnverified',RUST,'triangle'),('Unknown',INK,'square')]:
    cats.append(QgsRendererCategory(value,QgsMarkerSymbol.createSimple({'name':shape,'color':col,'outline_color':'white','outline_width':'.5','size':'3.8'}),value))
points.setRenderer(QgsCategorizedSymbolRenderer('water_status',cats));labels(points,'label',9)
topos={};slopes={}
for n in ['01-region','02-ranch','03-mount-carmel','04-red-canyon']:
    topos[n]=raster(S/(n+'-topo.tif'),n+' | USGS topographic context')
    slopes[n]=raster(D/(n+'-slope-degrees.tif'),n+' | hillside slope degrees (not route grade)')
    raster(D/(n+'-hillshade.tif'),n+' | 3DEP hillshade')
    raster(S/(n+'-dem.tif'),n+' | 3DEP service elevation metres')
native=None;native_frame=None
if (D/'thunder-slope-screen.tif').exists():
    native=raster(D/'thunder-slope-screen.tif','Native 1m slope screening | 30-45 / 45+ degrees')
    raster(D/'thunder-native-slope-degrees.tif','Thunder Mountain | 1m slope degrees')
    raster(D/'thunder-native-hillshade.tif','Thunder Mountain | 1m hillshade')
    raster(S/'thunder-native-1m.tif','Thunder Mountain | 1m source terrain crop')
    sample=QgsVectorLayer('Polygon?crs=EPSG:26912','Native terrain footprint','memory')
    f=QgsFeature();f.setGeometry(QgsGeometry.fromRect(native.extent()));sample.dataProvider().addFeatures([f]);sample.updateExtents()
    opt=QgsVectorFileWriter.SaveVectorOptions();opt.driverName='GPKG';opt.layerName='native_terrain_footprint';opt.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
    QgsVectorFileWriter.writeAsVectorFormatV3(sample,str(gpkg),project.transformContext(),opt)
    native_frame=QgsVectorLayer(str(gpkg)+'|layername=native_terrain_footprint','Native 1m analysis footprint','ogr')
    native_frame.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':PURPLE,'outline_width':'.4','outline_style':'dash'}));project.addMapLayer(native_frame)

extents={n:json.loads((S/(n+'-extent.json')).read_text()) for n in topos}
frames=QgsVectorLayer('Polygon?crs=EPSG:26912&field=sheet:string','Detail sheet footprints','memory')
for n in list(extents)[1:]:
    f=QgsFeature(frames.fields());f['sheet']=n[:2]+' / '+{'02-ranch':'RANCH','03-mount-carmel':'MT CARMEL','04-red-canyon':'RED CANYON'}[n]
    f.setGeometry(QgsGeometry.fromRect(QgsRectangle(*extents[n]['bbox_utm12'])));frames.dataProvider().addFeatures([f])
frames.updateExtents();frames.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':RUST,'outline_width':'.8'}));labels(frames,'sheet',11,RUST)
# Persist footprint geometry instead of leaving a memory provider in the project.
opt=QgsVectorFileWriter.SaveVectorOptions();opt.driverName='GPKG';opt.layerName='sheet_footprints';opt.actionOnExistingFile=QgsVectorFileWriter.CreateOrOverwriteLayer
QgsVectorFileWriter.writeAsVectorFormatV3(frames,str(gpkg),project.transformContext(),opt)
frames=QgsVectorLayer(str(gpkg)+'|layername=sheet_footprints','Detail sheet footprints','ogr')
frames.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'transparent','outline_color':RUST,'outline_width':'.8'}));labels(frames,'sheet',11,RUST);project.addMapLayer(frames)

def label(layout,text,x,y,w,h,size=10,bold=False,color=INK,html=False):
    item=QgsLayoutItemLabel(layout);item.setText(text);item.setFont(QFont('DejaVu Sans',size,QFont.Bold if bold else QFont.Normal))
    item.setFontColor(QColor(color));item.setMargin(0)
    layout.addLayoutItem(item);item.attemptMove(QgsLayoutPoint(x,y));item.attemptResize(QgsLayoutSize(w,h));return item
def box(layout,x,y,w,h,color):
    item=QgsLayoutItemShape(layout);item.setShapeType(QgsLayoutItemShape.Rectangle)
    item.setSymbol(QgsFillSymbol.createSimple({'color':color,'outline_style':'no'}));layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x,y));item.attemptResize(QgsLayoutSize(w,h));return item
def block(layout,title,body,y,height):
    label(layout,title,320,y,105,8,11,True,RUST)
    label(layout,body,320,y+9,105,height-9,10)

content={
'01-region':dict(title='A ranch base, three riding areas',subtitle='REGIONAL OVERVIEW  /  HAULING CONTEXT',blocks=[
 ('READ THE ATLAS', '02  Paria River Ranch and nearby canyons\n03  Mount Carmel / Bay Bill\n04  Red Canyon / Losee / Casto\n\nThese are separate hauling destinations.\nMap distances are not road mileage.',42,48),
 ('PLAN FOR THE WHOLE RIG', 'Road lines do not establish trailer fit.\nConfirm loaded rig length, width, height,\nground clearance, turning room and\nwet-weather access before committing.\nNo turnaround has been measured.',94,43),
 ('WATER IS A CRITICAL CLAIM', 'R1: ranch advertises potable supply. [E01]\nD4: seasonal horse-only hydrants. [E03]\nBlue streams are not verified supplies.\nFive gallons is not a daily maximum:\nUMN cites about 8-10 gallons for a typical\n1,000 lb horse, more with work/heat. [E15]',141,49),
 ('SCOPE STILL TO CONFIRM', 'Trip dates, horse count, exact rig and\nPeter\'s map extent remain open.\n"Red Mountain" may mean another place;\nthis draft covers the Coyote Hollow /\nRed Canyon / Thunder Mountain cluster.',195,43)],
 sources='E01 Ranch  |  E03 Recreation.gov  |  E09 UGRC roads  |  E13 USGS Topo  |  E15 UMN Extension'),
'02-ranch':dict(title='Paria River Ranch & canyon country',subtitle='RANCH DETAIL  /  WATER, ROAD ACCESS & RIDING LEADS',blocks=[
 ('R1  BASE & WATER', 'Ranch advertises potable water for\npeople and horses, corrals and rig stays.\nConfirm tank-fill permission, supply and\nrig placement with the host. [E01]\nReference pin is not a hydrant or gate.\nRanch: 323-347-9185',42,47),
 ('CONTACT STATION WATER', 'BLM lists drinking water at the Paria\nContact Station, not White House\ncampsites. Bulk filling and trailer\nturning are unverified; no exact water\noutlet pin has been invented. [E04]',94,43),
 ('ACCESS & CANYON HAZARDS', 'Old Paria access: the 2022 horse guide\nwarns about the steep, washboard exit\nwith a trailer. Treat as a historical\nwarning, not a present road rating. [E05]\nCheck flood conditions and restrictions\nfor each proposed canyon ride.',141,47),
 ('TRAILS ARE PLANNING LEADS', 'Teal dashes: HorseAllowed=Yes in UGRC.\nGray dashes: horse use unresolved.\nThe ranch route list is not permission\nfor every public-land segment. Paria\nCanyon has conflicting use context.\nNo complete ranch riding loop is verified.',195,45)],
 sources='E01/E02 Ranch/location  |  E04 BLM White House  |  E05 BCH Utah 2022  |  E09/E10 UGRC  |  E13 USGS'),
'03-mount-carmel':dict(title='Mount Carmel, Barracks & Bay Bill',subtitle='ACCESS INVESTIGATION  /  HISTORICAL RIDING LEADS',blocks=[
 ('M1  STAGING NEEDS CONFIRMATION', 'The 2022 riding guide describes staging\nat the Historic Barracks Corrals and\nwarns of poor trailer parking/turning\nfarther down the road. [E05]\nMarker is an approximate search area,\nnot a confirmed legal entrance.',42,48),
 ('M3  BAY BILL CANYON', 'The historical riding approach follows\nthe East Fork Virgin River corridor.\nCheck owner/manager access, gates,\nriver conditions and room to turn horses.\nFlooding and narrow terrain need a\nseparate go/no-go decision. [E05]',94,47),
 ('M2  BELLY OF THE DRAGON', 'A hiking tunnel carrying drainage,\nnot a verified horse route. Tourism\ncoordinates conflict; pin is approximate.\nDo not use this landmark as proof of\ntrailer parking or horse passage. [E07]',146,43),
 ('WATER & POSITION LIMITS', 'River water is unverified for supply,\nquality and stock access. Carry a plan\nthat does not depend on it.\nM1/M3 are area references, not exact\nturning points. No canyon route line\nhas been traced from prose.',195,45)],
 sources='E05 BCH Utah, pp. 1-2 (2022)  |  E07 Kane County tourism  |  E09/E10 UGRC  |  E13/E17 USGS'),
'04-red-canyon':dict(title='Red Canyon & the plateau edge',subtitle='LOSEE / CASTO / COYOTE HOLLOW / TOM BEST',blocks=[
 ('D1 / D2  LOSEE & CASTO', 'Published trailhead and horse-use data\nidentify riding leads. Trailer parking,\nturnaround dimensions and dispersed\ncampsite permission remain unverified.\nA trailhead is not an approved camp.\nCasto includes motorized-use segments.',42,47),
 ('D4  COYOTE HOLLOW WATER', 'Seasonal nonpotable hydrants for\nhorses only; supply may run out in late\nsummer/fall. Confirm before arrival.\nRecreation.gov describes backup water\nat Red Canyon Campground; confirm\nfill access and operation. [E03]',94,47),
 ('D3  THUNDER MOUNTAIN', 'Outlined sample: 1m terrain slopes.\nAmber: 30-45 degrees; purple: 45+.\nGray inside sample: no terrain data.\nHillside slope is not trail grade or an\nexact cliff boundary. Outside the sample\nno 1m slope check is shown. USFS reports\nexposure; original sheet is 404. [E06/E18]',146,48),
 ('D5  TOM BEST ROAD', 'Road lead, not a confirmed campsite.\nCurrent snow, mud and camping orders\nneed checking. Historic order expired\nMay 2026; neither closure nor permission\nis established by it. [E16/E19]\nPowell district: 435-676-9300',199,44)],
 sources='E03 Recreation.gov  |  E06 historical USFS lead  |  E08-E11 UGRC/USFS  |  E16 expired order  |  E18 USGS 1m'),
}

layout_records=[]
for index,(name,c) in enumerate(content.items(),1):
    layout=QgsPrintLayout(project);layout.initializeDefaults();layout.setName(name)
    page=layout.pageCollection().pages()[0];page.setPageSize(QgsLayoutSize(438.15,285.75))
    layout.renderContext().setDpi(300)
    box(layout,0,0,438.15,285.75,'#fcfaf4')
    box(layout,12,11,2,22,RUST)
    label(layout,c['title'],18,10,390,14,25,True)
    label(layout,'UTAH  /  PARIA RIVER RANCH     '+c['subtitle'],18,27,390,8,9,False,RUST)
    label(layout,f'{index:02d}',407,9,20,17,28,True,RUST)
    # A separate point layer per layout prevents later filters from changing earlier exports.
    pts=points.clone();pts.setName(name+' | planning references');project.addMapLayer(pts)
    filters={'01-region':"\"id\" = 'R1'",'02-ranch':"\"id\" LIKE 'R%'",'03-mount-carmel':"\"id\" LIKE 'M%'",'04-red-canyon':"\"id\" LIKE 'D%'"}
    pts.setSubsetString(filters[name])
    layers=[pts,frames,road_labels,topos[name]] if index==1 else [pts,road_labels,trails,roads]+([native_frame,native] if index==4 and native else [])+[topos[name]]
    m=QgsLayoutItemMap(layout);layout.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(12,42));m.attemptResize(QgsLayoutSize(298,202))
    m.setCrs(project.crs());m.setLayers(layers);m.setKeepLayerSet(True)
    # Headless singleton projects start with an empty extent; zoomToExtent cannot initialize it.
    m.setExtent(QgsRectangle(*extents[name]['bbox_utm12']))
    assert math.isfinite(m.scale()) and m.scale()>0
    m.setFrameEnabled(True);m.setFrameStrokeColor(QColor('#a49c8f'));m.setFrameStrokeWidth(QgsLayoutMeasurement(.25))
    # Geographic grid labels are deliberately sparse; grid north arrow remains explicit.
    grid=m.grid();grid.setEnabled(True);grid.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
    step=.25 if index==1 else .05 if index==2 else .02
    grid.setIntervalX(step);grid.setIntervalY(step);grid.setStyle(QgsLayoutItemMapGrid.Cross)
    grid.setLineSymbol(line('#b4b3a8',.15));grid.setCrossLength(1.2)
    grid.setAnnotationEnabled(True);grid.setAnnotationPrecision(2);grid.setAnnotationFont(QFont('DejaVu Sans',7))
    for side in [QgsLayoutItemMapGrid.Left,QgsLayoutItemMapGrid.Right,QgsLayoutItemMapGrid.Top,QgsLayoutItemMapGrid.Bottom]:
        grid.setAnnotationPosition(QgsLayoutItemMapGrid.InsideMapFrame,side)
    grid.setAnnotationDisplay(QgsLayoutItemMapGrid.LongitudeOnly,QgsLayoutItemMapGrid.Top)
    grid.setAnnotationDisplay(QgsLayoutItemMapGrid.LatitudeOnly,QgsLayoutItemMapGrid.Right)
    grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll,QgsLayoutItemMapGrid.Left)
    grid.setAnnotationDisplay(QgsLayoutItemMapGrid.HideAll,QgsLayoutItemMapGrid.Bottom)
    box(layout,19,48,18,17,'255,253,247,230');label(layout,'N\n↑',24,48,10,17,13,True)
    for title,body,y,height in c['blocks']:block(layout,title,body,y,height)
    # Scale bar uses geographic distance calculations from the projected map.
    scale=QgsLayoutItemScaleBar(layout);scale.setStyle('Single Box');scale.setLinkedMap(m)
    scale.setUnits(QgsUnitTypes.DistanceMiles);scale.setUnitsPerSegment(10 if index==1 else 1)
    scale.setNumberOfSegments(2);scale.setNumberOfSegmentsLeft(0);scale.setUnitLabel('mi');scale.setFont(QFont('DejaVu Sans',8));scale.setHeight(1.5)
    layout.addLayoutItem(scale);scale.attemptMove(QgsLayoutPoint(12,245))
    label(layout,f'1:{round(m.scale()):,} at actual size  |  Grid north  |  NAD83 / UTM 12N',95,248,215,7,8)
    label(layout,'LEGEND  Brown: highways   Ochre dashes: major unpaved roads   Teal dashes: published horse use   Gray/tan: other paths/roads',12,256,414,7,8)
    label(layout,'SOURCES (click for URLs)  '+c['sources'],12,264,414,6,7)
    label(layout,'PLANNING DRAFT  /  07 OCT 2026  /  Water, permissions & rig fit not field-verified  /  Blue streams are not refill promises  /  Avenza: second pass',12,272,414,5,7,True,RUST)
    project.layoutManager().addLayout(layout)
    pdf=O/(name+'.pdf');settings=QgsLayoutExporter.PdfExportSettings();settings.dpi=300
    settings.textRenderFormat=QgsRenderContext.TextFormatAlwaysText
    settings.appendGeoreference=False;settings.exportMetadata=True
    result=QgsLayoutExporter(layout).exportToPdf(str(pdf),settings)
    assert result==QgsLayoutExporter.Success,(name,result)
    # Apply exact print boxes and link the citation IDs to the human-readable source registry.
    r=PdfReader(str(pdf));w=PdfWriter();p=r.pages[0]
    p.mediabox=RectangleObject([0,0,1242,810]);p.bleedbox=RectangleObject([0,0,1242,810]);p.trimbox=RectangleObject([9,9,1233,801]);w.add_page(p)
    w.add_annotation(page_number=0,annotation=AnnotationBuilder.link(rect=(34,44,1210,62),
       url='https://github.com/pwdel/qgis/blob/main/qgis_projects/Utah/paria-river-ranch/docs/SOURCES.md'))
    w.add_metadata({'/Title':c['title'],'/Author':'pwdel','/Subject':'Source-backed equestrian planning draft; not Avenza validated'})
    with pdf.open('wb') as f:w.write(f)
    image_settings=QgsLayoutExporter.ImageExportSettings();image_settings.dpi=110
    result=QgsLayoutExporter(layout).exportToImage(str(ROOT/'previews'/(name+'.png')),image_settings)
    assert result==QgsLayoutExporter.Success
    layout_records.append({'name':name,'scale':m.scale(),'extent_utm12':extents[name]['bbox_utm12'],
       'page_mm':[438.15,285.75],'map_mm':[298,202],'pdf':str(pdf.relative_to(ROOT))})
    print('exported',name,flush=True)

writer=PdfWriter()
for n in content:writer.append(str(O/(n+'.pdf')))
writer.add_metadata({'/Title':'Paria River Ranch - Utah Horse Riding Atlas','/Subject':'Four-sheet planning draft. Avenza second pass.'})
with (O/'paria-river-ranch-four-sheets.pdf').open('wb') as f:writer.write(f)
project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(*extents['01-region']['bbox_utm12']),project.crs()))
# Open in an uncluttered overview; local data remain available in the layer tree.
visible={points.id(),frames.id(),topos['01-region'].id()}
for node in project.layerTreeRoot().findLayers():node.setItemVisibilityChecked(node.layerId() in visible)
project.setFileName(str(ROOT/'paria-river-ranch.qgz'));assert project.write()
(ROOT/'docs'/'layouts.json').write_text(json.dumps(layout_records,indent=2)+'\n')
print('saved project and combined PDF',flush=True)
