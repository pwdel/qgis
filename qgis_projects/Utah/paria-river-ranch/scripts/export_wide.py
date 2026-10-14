"""Map-first GeoPDFs and individually cited RFC 7946 vector exports."""
import os,json,re,math,zipfile,shutil,hashlib
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
import numpy as np
from scipy.ndimage import distance_transform_edt
from osgeo import gdal,ogr,osr
from qgis.core import *
from qgis.PyQt.QtGui import QFont,QColor
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,ArrayObject,FloatObject,TextStringObject,DictionaryObject,NumberObject
from expansion_terrain import COLORS
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources/wide';D=ROOT/'derived/wide';OUT=ROOT/'output/pdf/wide'
OUT.mkdir(parents=True,exist_ok=True)
a=QgsApplication([],False);a.initQgis();p=QgsProject.instance();assert p.read(str(ROOT/'paria-river-ranch-riding-atlas.qgz'))
URL='https://github.com/pwdel/qgis/blob/main/qgis_projects/Utah/paria-river-ranch/'
for layer in p.mapLayers().values():
 if not layer.crs().isValid() and layer.dataProvider().crs().isValid():layer.setCrs(layer.dataProvider().crs())
areas=[('ranch','02-ranch',2),('mount-carmel','03-mount-carmel',8),('red-canyon','04-red-canyon',14)]
records=[];vectors=[];coverage=[]
def main(lo):return max([x for x in lo.items() if isinstance(x,QgsLayoutItemMap)],key=lambda x:x.sizeWithUnits().width()*x.sizeWithUnits().height())
original={lo.name():main(lo).layers() for lo in p.layoutManager().layouts() if any(isinstance(x,QgsLayoutItemMap) for x in lo.items())}
# Rebuild slope screening from the expanded elevation grid and mapped trail corridor.
for slug,key,start in areas:
 dem=gdal.Open(str(S/(key+'-dem.tif')));gdal.DEMProcessing(str(D/(key+'-slope-degrees.tif')),dem,'slope')
 sd=gdal.Open(str(D/(key+'-slope-degrees.tif')));deg=sd.ReadAsArray();gt=sd.GetGeoTransform();valid=(deg>=0)&(deg<90);grade=100*np.tan(np.deg2rad(np.where(valid,deg,0)))
 trails=ogr.Open(str(S/'state-trails.geojson'));src=trails.GetLayer();dstsr=osr.SpatialReference();dstsr.ImportFromEPSG(26912);transform=osr.CoordinateTransformation(src.GetSpatialRef(),dstsr)
 mem=ogr.GetDriverByName('Memory').CreateDataSource('');ly=mem.CreateLayer('trails',dstsr,ogr.wkbUnknown)
 for f in src:
  g=f.GetGeometryRef()
  if g:
   g=g.Clone();g.Transform(transform);n=ogr.Feature(ly.GetLayerDefn());n.SetGeometry(g);ly.CreateFeature(n)
 mask=gdal.GetDriverByName('MEM').Create('',sd.RasterXSize,sd.RasterYSize,1,gdal.GDT_Byte);mask.SetGeoTransform(gt);mask.SetProjection(sd.GetProjection());gdal.RasterizeLayer(mask,[1],ly,burn_values=[1]);corridor=distance_transform_edt(mask.ReadAsArray()==0,sampling=(abs(gt[5]),gt[1]))<=150
 rgba=np.zeros((4,sd.RasterYSize,sd.RasterXSize),dtype='uint8')
 for lo,hi,col in COLORS:
  sel=valid&corridor&(grade>=lo)&(grade<hi)
  for band,c in enumerate(col):rgba[band][sel]=c
 for band,c in enumerate((100,100,100,160)):rgba[band][corridor&~valid]=c
 ds=gdal.GetDriverByName('GTiff').Create(str(D/(key+'-slope-overlay.tif')),sd.RasterXSize,sd.RasterYSize,4,gdal.GDT_Byte,options=['COMPRESS=DEFLATE']);ds.SetGeoTransform(gt);ds.SetProjection(sd.GetProjection())
 for band in range(4):ds.GetRasterBand(band+1).WriteArray(rgba[band])
 ds.GetRasterBand(4).SetColorInterpretation(gdal.GCI_AlphaBand);ds=None
 print('terrain',key,flush=True)
# Keep renderer and labels when replacing data sources.
for l in list(p.mapLayers().values()):
 name=l.name();new=None
 for slug,key,start in areas:
  if name==key+' | USGS topographic context':new=S/(key+'-topo.tif')
  if name==slug+' | terrain slopes within 150m of mapped trails':new=D/(key+'-slope-overlay.tif')
  if name==slug+' | historical fire perimeters':new=D/(key+'-perimeters.geojson')
  if name==slug+' | reported fire discovery points 1992-2024':new=D/(key+'-occurrences.geojson')
  if name==slug+' | official Utah ownership':new=D/(key+'-ownership.geojson')
 for label,stem in [('State trails |','state-trails'),('Road classes |','roads'),('Named approach roads |','roads'),('All source trailhead','trailheads'),('USFS trail records','usfs-trails')]:
  if name.startswith(label):new=S/(stem+'.geojson')
 if new:
  style=QgsMapLayerStyle();style.readFromLayer(l);subset=l.subsetString() if isinstance(l,QgsVectorLayer) else None
  l.setDataSource(str(new),name,l.providerType());style.writeToLayer(l)
  if subset:l.setSubsetString(subset)
  assert l.isValid(),name
# Capture old extents in a vector file, documenting where profile/review evidence remains limited.
oldboxes=QgsVectorLayer('Polygon?crs=EPSG:26912&field=note:string','Original research footprint','memory')
for slug,key,start in areas:
 b=json.loads((ROOT/'sources'/(key+'-extent.json')).read_text())['bbox_utm12'];ft=QgsFeature(oldboxes.fields());ft.setGeometry(QgsGeometry.fromRect(QgsRectangle(*b)));ft['note']='Original review markers and profile routes; not newly surveyed';oldboxes.dataProvider().addFeatures([ft])
# Source layers remain native in the new project; replace layouts only.
for lo in list(p.layoutManager().layouts()):p.layoutManager().removeLayout(lo)
notes={
'access':'Road class does not establish horse-trailer clearance. Water and staging points need confirmation.',
 'terrain':'Cell slope near mapped trails, NOT trail grade or cliff height. Yellow 30-45%, orange 45-60%, red 60-90%, purple 90-150%, dark >150%.',
 'snow':'October satellite snow context; NOT trip probability or forecast. Monthly evidence and station normals are in the companion atlas.',
 'camping':'Ownership colors are NOT camping permission. Confirm current orders and horse-trailer access with the land manager.',
 'wildfire':'Historical incidents and large-fire perimeters, NOT current fire status or October burn probability. Restrictions must be checked before travel.'}
for slug,key,start in areas:
 folder=OUT/slug;folder.mkdir(exist_ok=True);geo=folder/'geojson';geo.mkdir(exist_ok=True)
 info=json.loads((S/(key+'-extent.json')).read_text());extent=QgsRectangle(*info['bbox_utm12']);exportlayers={}
 for offset,kind in [(0,'access'),(1,'terrain'),(2,'snow'),(3,'camping'),(5,'wildfire')]:
  oldname=next(n for n in original if n.startswith(f'{start+offset:02}-'));layers=original[oldname]
  # Review letters reference original analysis, which remains in the companion.
  layers=[l for l in layers if 'review markers' not in l.name()]
  for l in layers:
   if isinstance(l,QgsVectorLayer):exportlayers[l.id()]=l
   else:
    bound=QgsCoordinateTransform(l.crs(),p.crs(),p).transformBoundingBox(l.extent());bound.grow(0.000001)
    coverage.append({'area':slug,'theme':kind,'layer':l.name(),'covers_map_bbox':bound.contains(extent),'source':str(Path(l.source()).relative_to(ROOT))})
  lo=QgsPrintLayout(p);lo.initializeDefaults();lo.setName(slug+'-'+kind+'-wide');lo.pageCollection().pages()[0].setPageSize(QgsLayoutSize(320,238));p.layoutManager().addLayout(lo)
  def label(text,x,y,w,h,size,bold=False):
   item=QgsLayoutItemLabel(lo);item.setText(text);font=QFont('DejaVu Sans');font.setPointSizeF(size);font.setBold(bold);item.setFont(font);lo.addLayoutItem(item);item.attemptMove(QgsLayoutPoint(x,y));item.attemptResize(QgsLayoutSize(w,h));return item
  label(slug.replace('-',' ').title()+' | '+kind.title()+' | expanded riding map',8,3,305,10,14,True)
  m=QgsLayoutItemMap(lo);lo.addLayoutItem(m);m.attemptMove(QgsLayoutPoint(8,16));m.attemptResize(QgsLayoutSize(304,304*202/298));m.setCrs(p.crs());m.setLayers(layers);m.setKeepLayerSet(True);m.setExtent(extent);assert math.isfinite(m.scale());lo.setReferenceMap(m)
  label(notes[kind],8,223,305,6,6.6)
  label('Planning draft | 1.5x original width and height | Sources, full legends and limitations: companion-atlas.pdf and reference/ | 14 Oct 2026',8,230,305,5,6.5)
  cfg=QgsLayoutExporter.PdfExportSettings();cfg.dpi=240;cfg.appendGeoreference=True;cfg.writeGeoPdf=False
  path=folder/(slug+'-'+kind+'-wide.pdf');assert QgsLayoutExporter(lo).exportToPdf(str(path),cfg)==QgsLayoutExporter.Success
  r=PdfReader(str(path));page=r.pages[0];gcs=DictionaryObject({NameObject('/Type'):NameObject('/PROJCS'),NameObject('/EPSG'):NumberObject(26912),NameObject('/WKT'):TextStringObject(p.crs().toWkt(QgsCoordinateReferenceSystem.WKT_PREFERRED))});measure=DictionaryObject({NameObject('/Type'):NameObject('/Measure'),NameObject('/Subtype'):NameObject('/GEO'),NameObject('/GCS'):gcs});view=DictionaryObject({NameObject('/Type'):NameObject('/Viewport'),NameObject('/Measure'):measure});page[NameObject('/VP')]=ArrayObject([view]);arr=lambda v:ArrayObject([FloatObject(x) for x in v]);factor=72/25.4;ph=float(page.mediabox.height);mh=m.sizeWithUnits().height()
  view[NameObject('/BBox')]=arr([8*factor,ph-(16+mh)*factor,312*factor,ph-16*factor]);view[NameObject('/Name')]=TextStringObject('Map frame only')
  measure[NameObject('/LPTS')]=arr([0,0,0,1,1,1,1,0]);measure[NameObject('/Bounds')]=arr([0,0,0,1,1,1,1,0]);rect=m.extent();tr=QgsCoordinateTransform(p.crs(),QgsCoordinateReferenceSystem('EPSG:4326'),p);corners=[tr.transform(QgsPointXY(x,y)) for x,y in [(rect.xMinimum(),rect.yMinimum()),(rect.xMinimum(),rect.yMaximum()),(rect.xMaximum(),rect.yMaximum()),(rect.xMaximum(),rect.yMinimum())]];measure[NameObject('/GPTS')]=arr([v for c in corners for v in (c.y(),c.x())])
  w=PdfWriter();w.add_page(page);w.add_metadata({'/Title':lo.name(),'/Subject':notes[kind]})
  with path.open('wb') as f:w.write(f)
  records.append({'file':str(path.relative_to(ROOT)),'area':slug,'theme':kind,'bounds':info['bbox_utm12'],'corners_lonlat':[[c.x(),c.y()] for c in corners]});print('PDF',path.name,flush=True)
 # Include original profile and USFS attributes as distinct layers, no invented trail extensions.
 for l in p.mapLayers().values():
  if l.name().startswith(slug+' | profile routes') or l.name().startswith('USFS trail records') or l.name().startswith('All source trailhead'):exportlayers[l.id()]=l
 for lid,l in exportlayers.items():
  if not l.isSpatial():continue
  bbox=QgsGeometry.fromRect(extent);tx=QgsCoordinateTransform(p.crs(),l.crs(),p);bbox.transform(tx);back=QgsCoordinateTransform(l.crs(),QgsCoordinateReferenceSystem('EPSG:4326'),p);features=[];repairs=0
  for f in l.getFeatures(QgsFeatureRequest().setFilterRect(bbox.boundingBox())):
   g=f.geometry()
   if g.isEmpty():continue
   if not g.isGeosValid():g=g.makeValid();repairs+=1
   g=g.intersection(bbox)
   if g.isEmpty():continue
   assert g.isGeosValid(),l.name();g.transform(back)
   props=json.loads(QgsJsonExporter(l).exportFeature(f))['properties'];props.update(atlas_layer=l.name(),atlas_source=URL+'docs/RIDING-SOURCES.md',atlas_input=URL+str(Path(l.source().split('|')[0]).relative_to(ROOT)),atlas_note='Clipped planning data. Geometry is not surveyed navigation; current access and water require verification.')
   features.append({'type':'Feature','geometry':json.loads(g.asJson(10)),'properties':props})
  name=re.sub(r'[^a-z0-9]+','-',l.name().lower()).strip('-');path=geo/(name+'.geojson');path.write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False)+'\n');vectors.append({'file':str(path.relative_to(ROOT)),'features':len(features),'repaired_input_geometries':repairs,'layer':l.name()})
 # Original charts, legends and restrictions keep their documented research date/extent.
 shutil.copy2(ROOT/'output/mobile/geopdf'/(slug+'-five-maps.pdf'),folder/'companion-atlas.pdf')
 ref=folder/'reference';ref.mkdir(exist_ok=True)
 for fn in ['GOVERNANCE.md','SOURCES.md','EXPANSION-SOURCES.md','RIDING-SOURCES.md','profile-methods.md']:
  if (ROOT/'docs'/fn).exists():shutil.copy2(ROOT/'docs'/fn,ref/fn)
 shutil.copy2(ROOT/'output/pdf/riding'/f'{start+4:02}-{slug}-profiles.pdf',folder/'original-trail-profiles.pdf')
 (folder/'READ-ME.txt').write_text('UTAH RIDING MAPS - EXPANDED EDITION\n\nFive individual GeoPDFs: access, terrain, October snow, camping and wildfire history. Import each PDF as a separate map. GeoJSON files are separate vector layers, not PDFs. GeoPDF keeps the visual styling; GeoJSON imports may require styling in your app. The PDF map frame has GPS metadata; headings/footers do not. iPhone app behavior has not been field-tested.\n\nEach new map is 1.5 times the previous width AND height (2.25 times its area), with the same center. New USGS topography, regional elevation and official trail/road, land ownership and fire-history queries cover the wider area. Elevation is a service DEM, not verified native lidar. Terrain colors describe cell slope within 150m of mapped trails, not trail grade or cliff height. Blank slope color is not proof of safety. Original profile and review evidence has not been extended or resurveyed.\n\nCompanion atlas and original trail profiles retain ORIGINAL extents, legends, charts and dated research. Do not apply their fire counts to the wider maps. Snow is exploratory satellite context, not a calibrated trip probability. Ownership does not grant camping permission. No source establishes horse-trailer clearance or guaranteed water. The original restriction research is dated October 2026; check current orders before travel.\n\nGeoJSON preserves source attributes and adds atlas_source and atlas_input citation links. Geometry is clipped to the expanded map; disconnected segments remain disconnected. Invalid source geometry is repaired before clipping; counts are recorded in the public wide-manifest.json. Raster imagery (snow and terrain) remains in PDFs and is not misrepresented as vector GeoJSON.\n\nFull evidence: '+URL+'docs/RIDING-SOURCES.md\n')
# Save relative project referencing expanded local source data.
p.setFilePathStorage(Qgis.FilePathType.Relative);p.setFileName(str(ROOT/'paria-river-ranch-wide.qgz'));assert p.write()
manifest={'created':'2026-10-14','linear_expansion':1.5,'area_multiplier':2.25,'device_tested':False,'pdfs':records,'geojson':vectors,'raster_coverage':coverage}
(ROOT/'docs/wide-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for slug,key,start in areas:
 with zipfile.ZipFile(OUT/(slug+'-share.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted((OUT/slug).rglob('*')):
   if f.is_file():z.write(f,f.relative_to(OUT/slug))
print('DONE',len(records),'PDFs',len(vectors),'GeoJSONs',flush=True)
