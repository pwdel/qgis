"""Export existing researched maps; run in the project's QGIS/GDAL environment."""
import os, json, shutil, zipfile, hashlib, math, xml.etree.ElementTree as ET
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import *
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor
from osgeo import gdal, osr
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject, AnnotationBuilder
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/mobile'
PDF=OUT/'geopdf'; QFIELD=OUT/'qfield'; GAIA=OUT/'gaia'
for d in [PDF,QFIELD,GAIA]:d.mkdir(parents=True,exist_ok=True)
app=QgsApplication([],False);app.initQgis()
p=QgsProject.instance();assert p.read(str(ROOT/'paria-river-ranch-riding-atlas.qgz'))
assert all(l.isValid() for l in p.mapLayers().values())
URL='https://github.com/pwdel/qgis/blob/main/qgis_projects/Utah/paria-river-ranch/'
AREAS=[('ranch','02-ranch',2,'R'),('mount-carmel','03-mount-carmel',8,'M'),('red-canyon','04-red-canyon',14,'D')]
records=[];frames={};main_frames={}
def maps(lo):return [x for x in lo.items() if isinstance(x,QgsLayoutItemMap)]
def main(lo):return max(maps(lo),key=lambda x:x.sizeWithUnits().width()*x.sizeWithUnits().height())
def bounds(r):return [r.xMinimum(),r.yMinimum(),r.xMaximum(),r.yMaximum()]
def jsonwrite(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def render(layers,extent,path,width=3000):
 settings=QgsMapSettings();settings.setLayers(layers);settings.setDestinationCrs(p.crs());settings.setTransformContext(p.transformContext());settings.setBackgroundColor(QColor('white'))
 height=round(width*extent.height()/extent.width());settings.setOutputSize(QSize(width,height));settings.setOutputDpi(220);settings.setExtent(extent)
 job=QgsMapRendererParallelJob(settings);job.start();job.waitForFinished();assert not job.errors(),str(job.errors());assert job.renderedImage().save(str(path))
 return settings.visibleExtent(),width,height
# The largest frame is the GPS frame. Other insets remain visual reference only.
for lo in sorted(p.layoutManager().layouts(),key=lambda x:x.name()):
 if not maps(lo):continue
 m=main(lo);lo.setReferenceMap(m)
 for item in lo.items():
  if isinstance(item,QgsLayoutItemLabel):
   text=item.text().replace('Avenza: second pass','GeoPDF: main map only').replace('Avenza is second pass','GeoPDF: main map only')
   item.setText(text)
 cfg=QgsLayoutExporter.PdfExportSettings();cfg.dpi=220;cfg.appendGeoreference=True;cfg.writeGeoPdf=False;cfg.textRenderFormat=QgsRenderContext.TextFormatAlwaysText
 target=PDF/(lo.name()+'.pdf');assert QgsLayoutExporter(lo).exportToPdf(str(target),cfg)==QgsLayoutExporter.Success
 reader=PdfReader(str(target));writer=PdfWriter();page=reader.pages[0]
 assert page.get('/VP'),lo.name()
 page.trimbox=RectangleObject([9,9,1233,801]);page.bleedbox=RectangleObject([0,0,1242,810]);writer.add_page(page)
 writer.add_annotation(page_number=0,annotation=AnnotationBuilder.link(rect=(34,40,1210,62),url=URL+'docs/RIDING-SOURCES.md'))
 writer.add_metadata({'/Title':lo.name(),' /Subject'.strip():'Geospatial main map; insets not GPS frames; researched 2026-10-09'})
 with target.open('wb') as f:writer.write(f)
 rect=m.extent();tr=QgsCoordinateTransform(m.crs(),QgsCoordinateReferenceSystem('EPSG:4326'),p)
 corners=[tr.transform(QgsPointXY(x,y)) for x,y in [(rect.xMinimum(),rect.yMinimum()),(rect.xMinimum(),rect.yMaximum()),(rect.xMaximum(),rect.yMaximum()),(rect.xMaximum(),rect.yMinimum())]]
 rec={'name':lo.name(),'pdf':str(target.relative_to(ROOT)),'crs':m.crs().authid(),'bounds':bounds(rect),'corners_lonlat':[[c.x(),c.y()] for c in corners],'map_mm':[m.pos().x(),m.pos().y(),m.sizeWithUnits().width(),m.sizeWithUnits().height()]}
 records.append(rec);main_frames[lo.name()]=m
 print('GeoPDF',lo.name(),flush=True)
# Full companion retains three profile pages without artificial georeferencing.
w=PdfWriter()
for lo in sorted(p.layoutManager().layouts(),key=lambda x:x.name()):
 path=PDF/(lo.name()+'.pdf') if maps(lo) else ROOT/'output/pdf/riding'/(lo.name()+'.pdf')
 w.append(str(path))
with (PDF/'utah-riding-geospatial-atlas.pdf').open('wb') as f:w.write(f)
p.setTitle('Utah riding atlas | GeoPDF main map reference frames');p.setFilePathStorage(Qgis.FilePathType.Relative);p.setFileName(str(ROOT/'paria-river-ranch-geopdf.qgz'));assert p.write()
# Capture native layer sets before building mobile projects.
for slug,area,start,prefix in AREAS:
 w=PdfWriter();themes={};selected={}
 for offset,kind in [(0,'Access'),(1,'Terrain - cell slopes, not trail grade'),(2,'Snow - October exploratory context'),(3,'Camping - ownership, verify permission'),(5,'Fire - historical incidents and perimeters')]:
  lo=next(l for l in p.layoutManager().layouts() if l.name().startswith(f'{start+offset:02}-'))
  w.append(str(PDF/(lo.name()+'.pdf')));m=main(lo);themes[kind]=[l.id() for l in m.layers()]
  for frame in maps(lo):
   for l in frame.layers():selected[l.id()]=l
  # Map-only TIFFs: custom tile preparation, never advertised as direct Gaia imports.
  tifdir=GAIA/(slug+'-custom-map-sources');tifdir.mkdir(exist_ok=True)
  png=tifdir/(lo.name()+'.png');extent,width,height=render(m.layers(),m.extent(),png)
  ds=gdal.Translate(str(tifdir/(lo.name()+'.tif')),str(png),format='GTiff',creationOptions=['COMPRESS=DEFLATE','TILED=YES'])
  ds.SetGeoTransform([extent.xMinimum(),extent.width()/width,0,extent.yMaximum(),0,-extent.height()/height]);sr=osr.SpatialReference();sr.ImportFromEPSG(26912);ds.SetProjection(sr.ExportToWkt());ds.SetMetadata({'TITLE':lo.name(),'SOURCE':URL+'docs/RIDING-SOURCES.md','LIMITATIONS':'Planning draft; see companion atlas. Terrain cell slope is not trail grade; snow exploratory; fire history not forecast.'});ds=None;png.unlink()
  if offset==5:
   small=min(maps(lo),key=lambda x:x.sizeWithUnits().width());themes['Fire - annual model, not October forecast']=[l.id() for l in small.layers()]
 with (PDF/(slug+'-five-maps.pdf')).open('wb') as f:w.write(f)
 access=main(next(l for l in p.layoutManager().layouts() if l.name().startswith(f'{start:02}-')))
 for month in range(1,13):
  snow=next(l for l in p.mapLayers().values() if l.name().startswith(f'Snow context {month:02}'))
  ids=themes['Snow - October exploratory context'];themes[f'Snow - {month:02} exploratory context']=[snow.id() if p.mapLayer(i).name().startswith('Snow context') else i for i in ids]
 for l in p.mapLayers().values():
  if l.name().startswith(slug+' |') or l.name().startswith(area+' |') or l.name().startswith('NOAA station snow normals'):selected[l.id()]=l
 profile=next(l for l in selected.values() if 'profile routes and ascent' in l.name());themes['Trails - modeled ascent attributes']=[profile.id()]+themes['Access']
 frames[slug]={'selected':list(selected),'themes':themes,'extent':bounds(access.extent()),'area':area}
# Each package has isolated local copies and no print-picture dependencies.
for slug,area,start,prefix in AREAS:
 info=frames[slug];folder=QFIELD/slug;folder.mkdir(exist_ok=True);mobile=QgsProject();mobile.setCrs(p.crs());mobile.setTransformContext(p.transformContext());mobile.setFilePathStorage(Qgis.FilePathType.Relative)
 copied={};idmap={}
 for oldid in info['selected']:
  original=p.mapLayer(oldid);layer=original.clone();source=original.source();parts=source.split('|',1);src=Path(parts[0]);assert src.is_file(),source
  rel=src.relative_to(ROOT);dest=folder/'data'/rel
  if src not in copied:
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);copied[src]=dest
  suffix='|'+parts[1] if len(parts)>1 else '';layer.setDataSource(str(copied[src])+suffix,original.name(),original.providerType());assert layer.isValid(),layer.name()
  # setDataSource preserves compatible renderers; explicitly restore all style XML.
  style=QgsMapLayerStyle();style.readFromLayer(original);style.writeToLayer(layer)
  if isinstance(layer,QgsVectorLayer):layer.setReadOnly(True)
  mobile.addMapLayer(layer);idmap[oldid]=layer
 tree=mobile.layerTreeRoot();model=QgsLayerTreeModel(tree)
 # Themes in QGIS 3.22 retain visibility/styles, not independent drawing orders.
 # Keep all vectors above overlay rasters and all overlays above opaque basemaps.
 def rank(layer):
  name=layer.name()
  if isinstance(layer,QgsVectorLayer):
   return {QgsWkbTypes.PointGeometry:0,QgsWkbTypes.LineGeometry:1,QgsWkbTypes.PolygonGeometry:2}.get(layer.geometryType(),3)
  if 'USGS topographic' in name:return 30
  if 'hillshade' in name:return 40
  if 'service elevation' in name:return 50
  return 20
 tree.setHasCustomLayerOrder(True)
 tree.setCustomLayerOrder(sorted(mobile.mapLayers().values(),key=lambda layer:(rank(layer),layer.name())))
 # Empty GeoJSON without declared geometry is a valid nonspatial evidence table.
 info['themes']={name:[i for i in ids if not isinstance(idmap[i],QgsVectorLayer) or idmap[i].isSpatial()] for name,ids in info['themes'].items()}
 for name,oldids in info['themes'].items():
  layers=[idmap[i] for i in oldids]
  for node in tree.findLayers():node.setItemVisibilityChecked(node.layer() in layers)
  mobile.mapThemeCollection().insert(name,QgsMapThemeCollection.createThemeFromCurrentState(tree,model))
 mobile.mapThemeCollection().applyTheme('Access',tree,model)
 mobile.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(*info['extent']),mobile.crs()))
 mobile.setTitle(slug+' | offline riding planning maps');mobile.setFileName(str(folder/(slug+'.qgz')));assert mobile.write()
 # Offline documentation preserves evidence and explains colors; PDFs include profile/fire context.
 for directory in ['docs','sources/profiles']:
  for src in (ROOT/directory).glob('*'):
   if src.is_file() and src.suffix in ['.md','.json','.csv']:
    dest=folder/'reference'/directory/src.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 for src in [ROOT/'sources/evidence.json',ROOT/'docs/types.json',ROOT/'output/pdf/riding'/f'{start+4:02}-{slug}-profiles.pdf',PDF/(slug+'-five-maps.pdf')]:
  dest=folder/'reference'/src.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 # Native theme preview for verification independent of print layouts.
 preview=OUT/'previews';preview.mkdir(exist_ok=True)
 for name in ['Access','Terrain - cell slopes, not trail grade','Snow - October exploratory context','Camping - ownership, verify permission','Fire - historical incidents and perimeters']:
  ids=info['themes'][name];render([idmap[i] for i in ids],QgsRectangle(*info['extent']),preview/(slug+'-'+name.split(' - ')[0].lower()+'.png'),width=1400)
 mobile.clear()
 # GPX: retain each disconnected mapped component as a separate track, no fabricated z values.
 ns='http://www.topografix.com/GPX/1/1';ET.register_namespace('',ns)
 def el(parent,name,text=None,**attrs):
  x=ET.SubElement(parent,'{'+ns+'}'+name,attrs)
  if text is not None:x.text=str(text)
  return x
 g=ET.Element('{'+ns+'}gpx',{'version':'1.1','creator':'Utah riding atlas - QGIS export'})
 meta=el(g,'metadata');el(meta,'name',slug+' riding planning data');el(meta,'desc','Planning draft. Map-clipped tracks may be incomplete. Published horse use is not current permission. Water/parking are references, not surveyed access. Research 2026-10-09.');link=el(meta,'link',href=URL+'docs/RIDING-SOURCES.md');el(link,'text','Sources and limitations')
 points=json.loads((ROOT/'sources/planning-points.geojson').read_text())['features'];pointcount=0
 evidence={'area':slug,'tracks':[],'waypoints':[]}
 for ft in points:
  prop=ft['properties']
  if not prop['id'].startswith(prefix):continue
  lon,lat=ft['geometry']['coordinates'];wp=el(g,'wpt',lat=f'{lat:.9f}',lon=f'{lon:.9f}');el(wp,'name',prop['label']);el(wp,'desc',json.dumps(prop,ensure_ascii=False));li=el(wp,'link',href=URL+'docs/SOURCES.md');el(li,'text','Evidence registry');pointcount+=1;evidence['waypoints'].append(ft)
 tracks=json.loads((ROOT/'sources/profiles'/(area+'-routes.geojson')).read_text())['features']
 for ft in tracks:
  prop=ft['properties'];assert ft['geometry']['type']=='LineString';t=el(g,'trk');el(t,'name',prop['label']+f" [component {prop['component']}/{prop['component_count']}]");el(t,'desc',json.dumps(prop,ensure_ascii=False)+'; Planning geometry, not a recorded ride. Do not infer cliff clearance or trail safety.');li=el(t,'link',href=URL+'docs/profile-methods.md');el(li,'text','Profile methods and source limitations');seg=el(t,'trkseg')
  for lon,lat,*rest in ft['geometry']['coordinates']:el(seg,'trkpt',lat=f'{lat:.9f}',lon=f'{lon:.9f}')
  evidence['tracks'].append(ft)
 ET.ElementTree(g).write(GAIA/(slug+'-trails-and-points.gpx'),encoding='utf-8',xml_declaration=True);jsonwrite(GAIA/(slug+'-evidence.json'),evidence)
 info['track_count']=len(tracks);info['waypoint_count']=pointcount;info['layer_count']=len(info['selected'])
 print('Prepared QField and Gaia',slug,flush=True)
jsonwrite(ROOT/'docs/mobile-layouts.json',records);jsonwrite(ROOT/'docs/mobile-packages.json',frames)
print('Export complete; run packaging and validation after adding MOBILE.md.',flush=True)
