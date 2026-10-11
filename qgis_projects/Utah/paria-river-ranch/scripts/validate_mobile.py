"""Independent file/relocation checks; does not claim iPhone application testing."""
import os,json,zipfile,tempfile,math,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import *
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor
from pypdf import PdfReader
from osgeo import gdal,ogr
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/mobile';checks=[]
def check(ok,label):
 checks.append({'check':label,'passed':bool(ok)})
 if not ok:raise AssertionError(label)
app=QgsApplication([],False);app.initQgis()
records=json.loads((ROOT/'docs/mobile-layouts.json').read_text());info=json.loads((ROOT/'docs/mobile-packages.json').read_text())
for rec in records:
 page=PdfReader(str(ROOT/rec['pdf'])).pages[0];vp=page['/VP'];check(len(vp)==1,rec['name']+' one geographic viewport');view=vp[0].get_object();m=view['/Measure'];gpts=list(map(float,m['/GPTS']));expected=[n for lon,lat in rec['corners_lonlat'] for n in (lat,lon)]
 check(max(abs(a-b) for a,b in zip(gpts,expected))<1e-8,rec['name']+' geographic corners')
 check(int(m['/GCS']['/EPSG'])==26912,rec['name']+' EPSG')
 x,y,w,h=rec['map_mm'];f=72/25.4;expectedbox=[x*f,float(page.mediabox.height)-(y+h)*f,(x+w)*f,float(page.mediabox.height)-y*f]
 check(max(abs(float(a)-b) for a,b in zip(view['/BBox'],expectedbox))<1e-6,rec['name']+' viewport restricted to main map')
 check(view['/BBox'][0]>0 and view['/BBox'][2]<page.mediabox.width,rec['name']+' sidebars excluded')
 check(bool(page.get('/Annots')),rec['name']+' source link retained')
 ds=gdal.Open(str(ROOT/rec['pdf']));check(ds is not None,rec['name']+' GDAL geospatial reader')
 neat=ogr.CreateGeometryFromWkt(ds.GetMetadata()['NEATLINE']);xmin,xmax,ymin,ymax=neat.GetEnvelope();check(max(abs(a-b) for a,b in zip([xmin,ymin,xmax,ymax],rec['bounds']))<0.1,rec['name']+' independent GDAL neatline within 10cm')
allpages=PdfReader(str(OUT/'geopdf/utah-riding-geospatial-atlas.pdf')).pages
check(len(allpages)==19,'full atlas page count')
for i,page in enumerate(allpages,1):check(bool(page.get('/VP'))==(i not in [6,12,18]),f'full atlas page {i} geospatial status')
for slug,data in info.items():
 pages=PdfReader(str(OUT/'geopdf'/(slug+'-five-maps.pdf'))).pages;check(len(pages)==5 and all(p.get('/VP') for p in pages),slug+' five map pages')
 archive=OUT/'qfield'/(slug+'-qfield.zip')
 with tempfile.TemporaryDirectory(prefix='utah-mobile-relocation-') as tmp:
  folder=Path(tmp)
  with zipfile.ZipFile(archive) as z:check(z.testzip() is None,slug+' archive integrity');z.extractall(folder)
  project=QgsProject();check(project.read(str(folder/(slug+'.qgz'))),slug+' relocated project read')
  check(len(project.mapLayers())==data['layer_count'],slug+' layer count')
  check(not project.layoutManager().layouts(),slug+' no external print pictures')
  for layer in project.mapLayers().values():
   check(layer.isValid(),slug+' valid '+layer.name());path=Path(layer.source().split('|')[0]);check(path.is_file() and folder in path.parents,slug+' local dependency '+layer.name())
   if isinstance(layer,QgsVectorLayer):check(layer.readOnly(),slug+' read-only evidence '+layer.name())
  with zipfile.ZipFile(folder/(slug+'.qgz')) as z:
   xml=ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.qgs'))))
   for source in xml.findall('.//projectlayers/maplayer/datasource'):check(source.text.startswith('./'),slug+' stored relative path '+source.text)
  themes=project.mapThemeCollection();check(set(themes.mapThemes())==set(data['themes']),slug+' all themes')
  for name in themes.mapThemes():
   visible=themes.mapThemeVisibleLayers(name);check(len(visible)==len(data['themes'][name]),slug+' theme layer count '+name)
   basemaps=[i for i,l in enumerate(visible) if 'USGS topographic context' in l.name()]
   if basemaps:check(all(i<basemaps[0] for i,l in enumerate(visible) if 'annual fire likelihood' in l.name() or 'Snow context' in l.name() or 'terrain slopes within' in l.name() or isinstance(l,QgsVectorLayer)),slug+' overlays above topo '+name)
  # Render after relocation from persisted theme data, not live exporter memory.
  for name in ['Access','Terrain - cell slopes, not trail grade','Snow - October exploratory context','Camping - ownership, verify permission','Fire - historical incidents and perimeters']:
   s=QgsMapSettings();s.setDestinationCrs(project.crs());s.setTransformContext(project.transformContext());s.setLayers(themes.mapThemeVisibleLayers(name));s.setLayerStyleOverrides(themes.mapThemeStyleOverrides(name));s.setExtent(project.viewSettings().defaultViewExtent());s.setOutputSize(QSize(1200,814));s.setBackgroundColor(QColor('white'));job=QgsMapRendererParallelJob(s);job.start();job.waitForFinished();check(not job.errors(),slug+' relocated render '+name)
   out=OUT/'previews'/(slug+'-relocated-'+name.split(' - ')[0].lower()+'.png');check(job.renderedImage().save(str(out)),slug+' saved preview '+name)
  check(any((folder/'reference').glob('*-profiles.pdf')),slug+' profile reference')
  project.clear()
 ns={'g':'http://www.topografix.com/GPX/1/1'};g=ET.parse(OUT/'gaia'/(slug+'-trails-and-points.gpx')).getroot();tracks=g.findall('g:trk',ns);wps=g.findall('g:wpt',ns)
 check(len(tracks)==data['track_count'],slug+' GPX track count');check(len(wps)==data['waypoint_count'],slug+' GPX waypoint count')
 source=json.loads((ROOT/'sources/profiles'/(data['area']+'-routes.geojson')).read_text())['features']
 for track,ft in zip(tracks,source):
  segs=track.findall('g:trkseg',ns);check(len(segs)==1,slug+' disconnected component retained');pts=segs[0].findall('g:trkpt',ns);coords=ft['geometry']['coordinates'];check(len(pts)==len(coords),slug+' all track vertices retained')
  check(all(abs(float(pt.attrib['lon'])-c[0])<1e-8 and abs(float(pt.attrib['lat'])-c[1])<1e-8 for pt,c in zip(pts,coords)),slug+' track coordinates preserved')
  check(not track.findall('.//g:ele',ns),slug+' no invented GPX elevations');check(ft['properties']['published_horse_status'] in track.find('g:desc',ns).text,slug+' permission caveat retained')
 for wp in wps:check('location_uncertainty_m' in wp.find('g:desc',ns).text,slug+' waypoint uncertainty retained')
 for tif in (OUT/'gaia'/(slug+'-custom-map-sources')).glob('*.tif'):
  ds=gdal.Open(str(tif));check(ds is not None,tif.name+' opens');check(ds.GetSpatialRef().GetAuthorityCode(None)=='26912',tif.name+' CRS');gt=ds.GetGeoTransform();rec=next(r for r in records if r['name']==tif.stem);bbox=[gt[0],gt[3]+gt[5]*ds.RasterYSize,gt[0]+gt[1]*ds.RasterXSize,gt[3]]
  check(max(abs(a-b) for a,b in zip(bbox,rec['bounds']))<max(abs(gt[1]),abs(gt[5])),tif.name+' extent within one pixel');check(ds.RasterXSize==3000,tif.name+' image resolution')
for f in OUT.rglob('*.zip'):
 with zipfile.ZipFile(f) as z:check(z.testzip() is None,str(f.relative_to(OUT))+' ZIP CRC')
# Verify finite XYZ grids and actual imagery against their TileJSON bounds.
from PIL import Image
for specpath in (OUT/'gaia').glob('*.tilejson.json'):
 spec=json.loads(specpath.read_text());name=specpath.name.replace('.tilejson.json','');folder=OUT/'gaia/tiles'/name
 check(spec['scheme']=='xyz' and spec['minzoom']==8 and spec['maxzoom']==13,name+' XYZ definition')
 check(spec['tiles'][0].endswith('/'+name+'/{z}/{x}/{y}.png'),name+' URL template')
 west,south,east,north=spec['bounds']
 def tilexy(lon,lat,z):return (int((lon+180)/360*(1<<z)),int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*(1<<z)))
 for z in range(8,14):
  x0,y0=tilexy(west,north,z);x1,y1=tilexy(east,south,z)
  for x in range(x0,x1+1):
   for y in range(y0,y1+1):
    tile=folder/str(z)/str(x)/(str(y)+'.png');check(tile.is_file(),name+f' tile coverage {z}/{x}/{y}')
    with Image.open(tile) as im:check(im.size==(256,256),name+' tile dimensions')
 x,y=tilexy((west+east)/2,(south+north)/2,13)
 with Image.open(folder/'13'/str(x)/(str(y)+'.png')) as im:check(im.convert('RGBA').getextrema()[3][1]>0,name+' center tile has imagery')
check(len(list((OUT/'gaia').glob('*.tilejson.json')))==15,'fifteen Gaia map definitions')
for name,entry in json.loads((ROOT/'docs/mobile-manifest.json').read_text()).items():check(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==entry['sha256'],name+' hash')
result={'status':'passed','checks':len(checks),'device_tested':False,'qgis_version':Qgis.QGIS_VERSION,'geographic_pages':16,'profile_pages':3,'qfield_packages':3,'gaia_tracks':sum(x['track_count'] for x in info.values()),'details':checks}
(ROOT/'docs/mobile-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
