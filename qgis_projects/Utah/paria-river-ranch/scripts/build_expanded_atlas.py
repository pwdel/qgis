"""Add editable terrain, seasonal snow and camping layouts; retain first edition."""
import os,json,math,calendar,shutil,zipfile
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import *
from qgis.PyQt.QtGui import QColor,QFont
from qgis.PyQt.QtCore import Qt
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject,AnnotationBuilder
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources';D=ROOT/'derived'/'expansion';O=ROOT/'output'/'pdf'/'expanded';P=ROOT/'previews'/'expanded'
for x in [D,O,P]:x.mkdir(parents=True,exist_ok=True)
# QGIS can change SQLite journal headers on open. Isolate the context GeoPackage
# before any QGIS read so original edition snapshots remain byte-identical.
shutil.copy2(ROOT/'derived/atlas.gpkg',D/'atlas-context.gpkg')
input_project=ROOT/'_expansion-input.qgz'
with zipfile.ZipFile(ROOT/'paria-river-ranch.qgz') as src, zipfile.ZipFile(input_project,'w',zipfile.ZIP_DEFLATED) as dst:
 for entry in src.namelist():
  data=src.read(entry)
  if entry.endswith('.qgs'):data=data.replace(b'./derived/atlas.gpkg',b'./derived/expansion/atlas-context.gpkg')
  dst.writestr(entry,data)
app=QgsApplication([],False);app.initQgis();project=QgsProject.instance();assert project.read(str(input_project))
project.setFilePathStorage(Qgis.FilePathType.Relative)
INK='#273d39';RUST='#9c5433';BLUE='#16768b';CREAM='#fcfaf4'
AREAS=['02-ranch','03-mount-carmel','04-red-canyon'];NAMES=['Paria River Ranch','Mount Carmel & Bay Bill','Red Canyon & plateau edge']
records=[];pdfs=[]
def label(l,t,x,y,w,h,size=10,bold=False,color=INK):
 a=QgsLayoutItemLabel(l);a.setText(t);font=QFont('DejaVu Sans',int(size),QFont.Bold if bold else QFont.Normal);font.setPointSizeF(size);a.setFont(font);a.setFontColor(QColor(color));l.addLayoutItem(a);a.attemptMove(QgsLayoutPoint(x,y));a.attemptResize(QgsLayoutSize(w,h));return a

def box(l,x,y,w,h,col):
 a=QgsLayoutItemShape(l);a.setShapeType(QgsLayoutItemShape.Rectangle);a.setSymbol(QgsFillSymbol.createSimple({'color':col,'outline_style':'no'}));l.addLayoutItem(a);a.attemptMove(QgsLayoutPoint(x,y));a.attemptResize(QgsLayoutSize(w,h));return a

def layout(title,sub,num):
 l=QgsPrintLayout(project);l.initializeDefaults();l.pageCollection().page(0).setPageSize(QgsLayoutSize(438.15,285.75));box(l,0,0,438.15,285.75,CREAM);box(l,12,11,2,21,RUST)
 label(l,title,18,10,384,14,23,True);label(l,sub,18,27,400,8,9,False,RUST);label(l,f'{num:02}',407,9,20,17,28,True,RUST)
 return l

def footer(l,source,warning):
 label(l,'SOURCES (click for URLs)  '+source,12,265,414,6,7)
 label(l,'08 OCT 2026  /  PLANNING DRAFT  /  '+warning+'  /  Avenza: second pass',12,273,414,5,7,True,RUST)

def save(l,name):
 l.setName(name);project.layoutManager().addLayout(l);p=O/(name+'.pdf');cfg=QgsLayoutExporter.PdfExportSettings();cfg.dpi=220;cfg.textRenderFormat=QgsRenderContext.TextFormatAlwaysText;cfg.appendGeoreference=False
 assert QgsLayoutExporter(l).exportToPdf(str(p),cfg)==QgsLayoutExporter.Success
 r=PdfReader(str(p));w=PdfWriter();pg=r.pages[0];pg.mediabox=RectangleObject([0,0,1242,810]);pg.bleedbox=RectangleObject([0,0,1242,810]);pg.trimbox=RectangleObject([9,9,1233,801]);w.add_page(pg)
 w.add_annotation(page_number=0,annotation=AnnotationBuilder.link(rect=(34,40,1210,62),url='https://github.com/pwdel/qgis/blob/main/qgis_projects/Utah/paria-river-ranch/docs/EXPANSION-SOURCES.md'))
 w.add_metadata({'/Title':name,'/Subject':'Horse terrain, snow and camping planning; not field verified or Avenza tested'})
 with p.open('wb') as f:w.write(f)
 records.append({'name':name,'pdf':str(p.relative_to(ROOT)),'maps':[{'scale':it.scale(),'extent':it.extent().toString()} for it in l.items() if isinstance(it,QgsLayoutItemMap)]});pdfs.append(p);print('exported',name,flush=True)

def raster(path,name):
 a=QgsRasterLayer(str(path),name);assert a.isValid(),path;project.addMapLayer(a);return a

def vector(path,name):
 a=QgsVectorLayer(str(path),name,'ogr');assert a.isValid(),path;project.addMapLayer(a);return a

def named(prefix):return next(x for x in project.mapLayers().values() if x.name().startswith(prefix))
def textstyle(v,field,size=8):
 p=QgsPalLayerSettings();p.fieldName=field;p.placement=QgsPalLayerSettings.OrderedPositionsAroundPoint
 f=QgsTextFormat();f.setFont(QFont('DejaVu Sans'));f.setSize(size);f.setColor(QColor(INK));b=QgsTextBufferSettings();b.setEnabled(True);b.setSize(.8);b.setColor(QColor('white'));f.setBuffer(b);p.setFormat(f);v.setLabeling(QgsVectorLayerSimpleLabeling(p));v.setLabelsEnabled(True)

def mapitem(l,layers,bbox,x,y,w,h,scale=False):
 m=QgsLayoutItemMap(l);l.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(x,y));m.attemptResize(QgsLayoutSize(w,h));m.setCrs(project.crs());m.setLayers(layers);m.setKeepLayerSet(True);m.setExtent(QgsRectangle(*bbox));m.setFrameEnabled(True);m.setFrameStrokeColor(QColor('#a49c8f'));m.setFrameStrokeWidth(QgsLayoutMeasurement(.2));assert math.isfinite(m.scale())
 if scale:
  label(l,'N\n↑',x+2,y+2,10,13,10,True)
  s=QgsLayoutItemScaleBar(l);s.setStyle('Single Box');s.setLinkedMap(m);s.setUnits(QgsUnitTypes.DistanceMiles);s.setUnitsPerSegment(1);s.setNumberOfSegments(2);s.setNumberOfSegmentsLeft(0);s.setUnitLabel('mi');s.setFont(QFont('DejaVu Sans',7));s.setHeight(1.1);l.addLayoutItem(s);s.attemptMove(QgsLayoutPoint(x,y+h+1))
  label(l,f'1:{round(m.scale()):,}  |  Grid north  |  NAD83 / UTM 12N',x+82,y+h+1,w-80,7,7)
 return m

roads=named('Road classes');roadnames=named('Named approach');trails=named('State trails');points=named('Planning references')
topos={n:named(n+' | USGS') for n in AREAS};extents={n:json.loads((S/(n+'-extent.json')).read_text())['bbox_utm12'] for n in AREAS}
terrain=json.loads((ROOT/'docs'/'expansion-terrain.json').read_text());climate=json.loads((S/'expansion-snow'/'snow-climatology.json').read_text());stations={x['id']:x for x in climate['stations']}
station_layer=vector(S/'expansion-snow'/'snow-stations.geojson','NOAA station snow normals | inspect months and elevations')
station_layer.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'diamond','color':BLUE,'size':'3'}));textstyle(station_layer,'name')
frames=named('Detail sheet footprints');fp=frames.labeling().settings();fp.fieldName="CASE WHEN \"sheet\" = '03 / MT CARMEL' THEN '06 / MT CARMEL' WHEN \"sheet\" = '04 / RED CANYON' THEN '10 / RED CANYON' ELSE \"sheet\" END";fp.isExpression=True;frames.setLabeling(QgsVectorLayerSimpleLabeling(fp))
reviews=vector(D/'review-points.geojson','Nearby lower-ground review points | not cliff heights');reviews.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'circle','color':'white','outline_color':'#632c61','outline_width':'.65','size':'4'}));textstyle(reviews,'label')
# Consistent satellite scale for all twelve months; no smoothing or probabilistic relabeling.
snows=[];SC=[(0,'#f5f4ee'),(1,'#e0edf2'),(5,'#b8d5e6'),(10,'#87b4d1'),(25,'#4a89b2'),(50,'#225b91'),(75,'#16376c'),(100,'#231445')]
for mo in range(1,13):
 a=raster(S/'expansion-snow'/f'snowcover-ensemble-p50-{mo:02}.tif',f'Snow context {mo:02} | exploratory satellite ensemble')
 shader=QgsColorRampShader();shader.setColorRampType(QgsColorRampShader.Interpolated);shader.setColorRampItemList([QgsColorRampShader.ColorRampItem(v,QColor(c),str(v)) for v,c in SC]);rs=QgsRasterShader();rs.setRasterShaderFunction(shader);a.setRenderer(QgsSingleBandPseudoColorRenderer(a.dataProvider(),1,rs));a.renderer().setOpacity(.78);snows.append(a)

# Grade examples share a constant horizontal scale, so their steepness is visually comparable.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="980" height="125" viewBox="0 0 980 125">']
for i,g in enumerate([30,45,60,90]):
 x=10+i*245;rise=g*.62;y=95;run=62;col=['#efc146','#eb8631','#c14631','#873a73'][i]
 svg.append(f'<path d="M{x} {y} L{x+run} {y-rise} L{x+run} {y} Z" fill="{col}" opacity=".55"/><path d="M{x} {y} L{x+run} {y-rise}" stroke="{col}" stroke-width="4"/><text x="{x+80}" y="50" font-family="DejaVu Sans" font-size="20" fill="{INK}">{g}% / {math.degrees(math.atan(g/100)):.1f}°</text><text x="{x+80}" y="74" font-family="DejaVu Sans" font-size="14" fill="{INK}">rise {g} per 100 run</text>')
svg.append('</svg>');(D/'grade-key.svg').write_text(''.join(svg))
def picture(l,path,x,y,w,h):
 p=QgsLayoutItemPicture(l);l.addLayoutItem(p);p.attemptMove(QgsLayoutPoint(x,y));p.attemptResize(QgsLayoutSize(w,h));p.setPicturePath(str(path));return p

def base_page(original,num,title):
 orig=project.layoutManager().layoutByName(original);assert orig
 l=orig.clone()
 for it in l.items():
  if isinstance(it,QgsLayoutItemLabel):
   txt=it.text()
   if txt==original[:2]:it.setText(f'{num:02}')
   if '02  Paria River' in txt:it.setText(txt.replace('03  Mount Carmel','06  Mount Carmel').replace('04  Red Canyon','10  Red Canyon'))
 save(l,f'{num:02}-{title}-access' if num>1 else '01-regional-overview')
base_page('01-region',1,'region')

CAMPKEY={'Bureau of Land Management':'#ead8b2','National Monument':'#d9c18f','National Wilderness Area':'#c9abd1','National Forest':'#bbd1be','Private':'#e4bcbc','State Trust Lands':'#b7cee3','Other State':'#d3d3dd','Bankhead-Jones Land Use Lands':'#d7d1b4'}
CAMPBLOCKS=[[
 ('RANCH / BOOKED HORSE CAMP','The private ranch advertises horse camping.\nBook with the host; confirm rig placement,\nstock water and tank filling. [E01]'),
 ('PUBLIC LAND HAS DIFFERENT RULES','Grand Staircase-Escalante: free overnight\npermit. Paria Canyon wilderness: separate\nadvance overnight permit; no motor vehicles.\nNeither establishes a horse-trailer campsite.\nWhite House is car / walk-in camping. [C10/C11/C13]'),
 ('BOUNDARIES ARE CONTEXT','Pink: private land. Blue: state trust land.\nDo not cross or camp without the applicable\npermission. Blank outside Utah is unmapped,\nnot open land. Ownership is not a legal\ncampsite or route-access inventory. [C01/C12]')],[
 ('OFFICIAL BARRACKS STAGING','BLM documents river-corridor dispersed\ncamping and a staging kiosk, with no water.\nThis is not a measured trailer turnout.\nThe historical M1 lead is a different point.\nUse the official kiosk as a reference. [C02]'),
 ('PRIVATE RANCH / DIFFICULT ROAD','Private Barracks Ranch interrupts access.\nBLM warns of difficult travel beyond it;\na drawn road is not a trailer endorsement.\nDo not enter private land on the strength\nof a historic riding guide. [C02/E05]'),
 ('STATE TRUST / BLM PATCHWORK','State parcels have separate conditions\nand exceptions. Riverbank space does not\nprove legal camping or flood-safe staging.\nBay Bill campsite geometry and horse-\ntrailer fit remain unresolved. [C02/C12]')],[
 ('COYOTE HOLLOW / HORSE CAMP','Current listing: reservable sites with\nequestrian priority. Seasonal stock water\ncan run dry; confirm supply. It is not an\non-trail refill promise. [C03/E03]'),
 ('POSTED WATER / CORRALS','2026 orders: 300ft restrictions at designated,\nposted water sources; posted listed corrals\nhave May 1-Nov 15 camping restrictions.\nThese are not every stream or corral.\nNo speculative buffers drawn. [C05/C06]'),
 ('TOM BEST / CHECK CURRENT SIGNS','Old Tom Best order expired May 15, 2026.\nReplacement status remains unresolved.\nDave\'s Hollow has a current designated-site\nrestriction. Local rules override general\nforest camping assumptions. [C07/C09/C14]')]]

for idx,n in enumerate(AREAS):
 start=2+idx*4;slug=['ranch','mount-carmel','red-canyon'][idx];base_page(n,start,slug)
 pts=points.clone();pts.setSubsetString(["\"id\" LIKE 'R%'","\"id\" LIKE 'M%'","\"id\" LIKE 'D%'"][idx]);pts.setName(slug+' | area references');project.addMapLayer(pts)
 # TERRAIN
 l=layout(NAMES[idx]+' / terrain & exposure','HORSE & RIDER  /  STEEP GROUND, NEARBY DROPS AND FOOTING',start+1)
 overlay=raster(D/(n+'-slope-overlay.tif'),slug+' | terrain slopes within 150m of mapped trails')
 raster(D/(n+'-slope-percent.tif'),slug+' | percent terrain cell slope')
 raster(D/(n+'-lower-ground-100m.tif'),slug+' | ground below within 100m (not cliff height)')
 rev=reviews.clone();rev.setSubsetString(f'"area" = \'{n}\'');rev.setName(slug+' | review markers');project.addMapLayer(rev)
 layers=[rev,pts,trails,roadnames,overlay,topos[n]]
 mapitem(l,layers,extents[n],12,43,270,177,True)
 for j,p in enumerate(terrain[n]['review_points'][:2]):
  y=40+j*85;label(l,f'{p["id"]} / about {p["drop_m_rounded_5"]}m lower ground nearby',292,y,132,8,9,True)
  width=1600;height=width*63/132
  bbox=[p['x']-width/2,p['y']-height/2,p['x']+width/2,p['y']+height/2]
  hill=named(n+' | 3DEP hillshade')
  mapitem(l,[rev,trails,overlay,hill],bbox,292,y+9,132,63)
  label(l,'Lower ground within 100m; not a vertical cliff height.',292,y+73,134,6,7)
 label(l,f'MODEL LIMITS  /  {terrain[n]["cell_m"]:.1f}m output cells',292,210,134,7,9,True,RUST)
 label(l,'A-C: review sites on all mapped paths; horse use varies.\nTrail benches, edge clearance and footing are unresolved.\nSnow / mud can change traction; no safe grade is assigned.\nTeal: published horse use; gray paths: unresolved.',292,218,134,21,8)
 label(l,'PERCENT GRADE KEY  /  SHAPE EXAMPLES, NOT HORSE-SAFETY LIMITS',12,238,275,6,8,True)
 picture(l,D/'grade-key.svg',12,244,270,20)
 label(l,'TRAIL GRADE: not measured here.\nSIDE SLOPE: color is surrounding terrain.\nEXPOSURE: nearby lower ground is a screening clue.',292,242,134,18,8,True)
 # Map color classes are more detailed than the four key examples.
 label(l,'Color bins: 30-45% yellow | 45-60 orange | 60-90 rust | 90-150 purple | 150+ dark purple. Uncolored is not certified safe.',12,231,274,6,6.7)
 footer(l,'T01  USGS 3DEP + UGRC trails; 150m trail search corridor; original sources E10/E14; gray = missing slope','Slopes are terrain cells, not trail tread; exact cliff edges unknown')
 save(l,f'{start+1:02}-{slug}-terrain')
 # SNOW
 l=layout(NAMES[idx]+' / snow through the year','OCTOBER FOCUS  /  EXPLORATORY SATELLITE CONTEXT + NOAA STATION NORMALS',start+2)
 label(l,'OCTOBER  /  typical monthly snow cover',12,38,207,7,10,True)
 mapitem(l,[pts,trails,roadnames,snows[9],topos[n]],extents[n],12,47,202,137,True)
 for mo in range(12):
  x=227+(mo%4)*50;y=41+(mo//4)*48
  label(l,calendar.month_abbr[mo+1].upper(),x,y,47,6,8,True,RUST if mo==9 else INK)
  mapitem(l,[snows[mo],topos[n]],extents[n],x,y+7,47,36)
 label(l,'SATELLITE SCALE (%)  /  same colors in every month',227,187,201,7,8,True)
 for k,(v,c) in enumerate(SC):
  box(l,227+k*24,195,22,3,c);label(l,str(v),227+k*24,198,23,6,7)
 label(l,'Nominal 500m cells; ESA input 1km. DLR 2000-2025; ESA through 2023.\nAverage of source medians; method partly unreproduced. Not snow depth\nor a daily/trip probability. Zero typical cover does not mean no snow.\nNot locally validated; small summer patches may be artifacts.',12,194,209,19,7.5)
 label(l,'NEARBY STATIONS  /  MONTHLY NEW SNOWFALL (INCHES), 1991-2020',12,216,414,7,9,True)
 selected=[['USC00026180','USC00424508'],['USC00424508','USC00420086'],['USC00424755','USC00421008']][idx]
 for mo in range(12):label(l,calendar.month_abbr[mo+1],125+mo*19,224,18,6,7,True)
 for row,sid in enumerate(selected):
  s=stations[sid];short={'USC00026180':'Page','USC00424508':'Kanab','USC00420086':'Alton','USC00424755':'Kodachrome','USC00421008':'Bryce NP HQ'}[sid]
  label(l,f'{short} / {s["elevation_ft"]:,}ft',12,231+row*7,109,7,8,True)
  for mo,v in enumerate(s['months']):
   f=v['snowfall_inches'];txt='--' if f['value'] is None else f'{f["value"]:.1f}'+('*' if f['completeness_flag']!='S' else '')
   label(l,txt,125+mo*19,231+row*7,18,7,8)
  v=s['months'][9]['midmonth_snow_depth_ge_1_inch_pct'];txt='unknown' if v['value'] is None else str(v['value'])+'%'
  label(l,f'{short}: {txt} ({v["years"] or "?"} years)',361,230+row*8,66,8,7.5)
 label(l,'OCT 15: depth >=1in',361,222,67,7,7.5,True)
 label(l,'Station probabilities: smoothed 29-day calendar window around Oct 15; not trip odds. Nearby stations can lie outside these map frames.\n* Provisional normal (<24 complete years); months/flags in source data. Elevation alone cannot predict snow on a shaded or exposed trail.',12,247,414,12,7.5)
 footer(l,'S01 NOAA NCEI; S02 Celik & Hengl / OpenGeoHub, DOI 10.5281/zenodo.20610475, CC-BY-4.0; S03 NOAA ENSO','El Nino / La Nina can shift winter patterns; neither predicts October trail snow')
 save(l,f'{start+2:02}-{slug}-snow')
 # CAMPING
 l=layout(NAMES[idx]+' / camping context','LAND OWNERSHIP + DOCUMENTED CAMPING CONDITIONS  /  NOT A CAMPSITE PERMISSION MAP',start+3)
 own=vector(S/'expansion-camping'/(['ranch','barracks','red-canyon'][idx]+'-ownership.geojson'),slug+' | official Utah ownership')
 cats=[QgsRendererCategory(v,QgsFillSymbol.createSimple({'color':c,'outline_color':'#8c8275','outline_width':'.18'}),v) for v,c in CAMPKEY.items()]
 own.setRenderer(QgsCategorizedSymbolRenderer('state_lgd',cats));own.setOpacity(.7)
 cp=vector(S/'expansion-camping'/'camping-points.geojson',slug+' | official campsite/staging references');cp.renderer().setSymbol(QgsMarkerSymbol.createSimple({'name':'star','color':'#884144','outline_color':'white','size':'4'}));textstyle(cp,'name',8)
 mapitem(l,[cp,pts,trails,roadnames,roads,own,topos[n]],extents[n],12,43,286,194,True)
 for j,(head,body) in enumerate(CAMPBLOCKS[idx]):
  y=43+j*60;label(l,head,309,y,117,8,10,True,RUST);label(l,body,309,y+10,117,45,9)
 for k,(v,c) in enumerate(list(CAMPKEY.items())):
  x=12+(k%4)*103;y=249+(k//4)*8;box(l,x,y+1,5,4,c);label(l,v,x+7,y,96,7,7)
 footer(l,'C01-C14 official Utah ownership, BLM, USFS orders, Recreation.gov; source dates and unresolved geometry retained','Private / trust land and local orders interrupt general camping rules')
 save(l,f'{start+3:02}-{slug}-camping')

writer=PdfWriter()
for p in pdfs:writer.append(str(p))
writer.add_metadata({'/Title':'Paria River Ranch - Expanded Horse Riding Atlas','/Subject':'13 sheets: access, terrain exposure, snow and camping; planning draft'})
with (O/'paria-river-ranch-expanded-atlas.pdf').open('wb') as f:writer.write(f)
project.setTitle('Paria River Ranch | expanded horse atlas');project.setFileName(str(ROOT/'paria-river-ranch-expanded.qgz'));assert project.write()
(ROOT/'docs'/'expanded-layouts.json').write_text(json.dumps(records,indent=2)+'\n');input_project.unlink();print('saved 13-sheet expanded atlas',flush=True)
