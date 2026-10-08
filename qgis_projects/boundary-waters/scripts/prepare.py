"""Normalize historical KML and create offline terrain relief and sheet geometry."""
import json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from osgeo import gdal,ogr,osr
from matplotlib.colors import LightSource
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources';D=ROOT/'derived'
D.mkdir(exist_ok=True)
def save(n,features):
 (D/(n+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2))
def feature(g,p):return {'type':'Feature','geometry':g,'properties':p}
n={'k':'http://www.opengis.net/kml/2.2'};tree=ET.parse(S/'2008-boundary-waters.kml');routes=[];points=[]
for el in tree.findall('.//k:Placemark',n):
 name=el.findtext('k:name',namespaces=n);desc=el.findtext('k:description',default='',namespaces=n)
 ls=el.find('.//k:LineString/k:coordinates',n);pt=el.find('.//k:Point/k:coordinates',n)
 if ls is not None:
  coords=[list(map(float,x.split(',')[:2])) for x in ls.text.split()]
  routes.append(feature({'type':'LineString','coordinates':coords},{'name':name,'segment':len(routes)+1,'source':'KML2008','status':'Historical supplied line; not a surveyed navigation track'}))
 elif pt is not None:
  c=list(map(float,pt.text.strip().split(',')[:2]));idx={'Hungry Jack Lake Entry Point':'ENTRY','First Night Campsite':'C1','Second Night Campsite':'C2','Third & Fourth Night Campsite':'C3/4','Fifth Night Campsite':'C5','Exit':'EXIT','Big Bass':'F1','Tons of Bass':'F2','Berries':'B1'}
  kind='fish' if name in ['Big Bass','Tons of Bass'] else ('camp' if 'Campsite' in name else 'other')
  points.append(feature({'type':'Point','coordinates':c},{'name':name,'label':idx[name],'kind':kind,'description':desc,'source':'KML2008'}))
save('route',routes);save('trip-points',points)
# Route lakes: labels at source lake reference points, not survey stations.
fishes=json.loads((S/'fisheries.json').read_text());fs=[]
for i,f in enumerate(fishes,1):
 fs.append(feature({'type':'Point','coordinates':f['metadata_point']},{'lake':f['lake'],'label':f['lake']+('  [S]' if f['stocking_records'] else ''),'id':f['id'],'fish_ref':f'L{i:02d}','survey_year':f['survey_year'],'stocked':bool(f['stocking_records']),'source':f['source_url']}))
save('lake-labels',fs)
geo=osr.SpatialReference();geo.ImportFromEPSG(4326);geo.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
utm=osr.SpatialReference();utm.ImportFromEPSG(26915);utm.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
tx=osr.CoordinateTransformation(geo,utm);back=osr.CoordinateTransformation(utm,geo)
# Map body 296 x 143mm, then independent scan panels below it.
sheets=[('01-overview','The 2008 canoe journey',-90.289,48.080,31500),('02-west','Hungry Jack to Rose',-90.436,48.081,13000),('03-border','Rose, Rove & Mountain',-90.310,48.098,16000),('04-east','The Pike lakes',-90.179,48.083,15700),('05-return','Pine, Caribou & Clearwater',-90.282,48.076,17700)]
records=[];frames=[]
for i,(id,title,lon,lat,w) in enumerate(sheets):
 x,y,_=tx.TransformPoint(lon,lat);h=w/(396/185 if i==0 else 296/143)
 b=[x-w/2,y-h/2,x+w/2,y+h/2];records.append({'id':id,'title':title,'bbox':b,'width_m':w})
 if i:
  corners=[back.TransformPoint(a,c)[:2] for a,c in [(b[0],b[1]),(b[2],b[1]),(b[2],b[3]),(b[0],b[3]),(b[0],b[1])]]
  frames.append(feature({'type':'Polygon','coordinates':[corners]},{'sheet':id[:2]}))
(D/'sheets.json').write_text(json.dumps(records,indent=2));save('sheet-frames',frames)
# Zero-valued pixels are outside lidar coverage (no explicit nodata in server TIFF).
gdal.UseExceptions();ds=gdal.Open(str(S/'lidar-route-8m.tif'));z=ds.ReadAsArray();valid=np.isfinite(z)&(z>100)&(z<1000)
clean=gdal.GetDriverByName('GTiff').CreateCopy(str(D/'lidar-valid-8m.tif'),ds,options=['COMPRESS=DEFLATE','PREDICTOR=3','TILED=YES']);clean.GetRasterBand(1).SetNoDataValue(-9999);clean.GetRasterBand(1).WriteArray(np.where(valid,z,-9999));clean=None
# Relief is terrain only. No bathymetry is inferred from lidar water pixels.
gdal.DEMProcessing(str(D/'hillshade.tif'),str(D/'lidar-valid-8m.tif'),'hillshade',computeEdges=True,creationOptions=['COMPRESS=DEFLATE'])
hill=gdal.Open(str(D/'hillshade.tif')).ReadAsArray()/255.
base=np.array([227,230,213]);rgb=np.clip(base[None,None,:]*(.72+.28*hill[:,:,None]),0,255).astype('uint8')
r=gdal.GetDriverByName('GTiff').Create(str(D/'terrain-relief.tif'),ds.RasterXSize,ds.RasterYSize,4,gdal.GDT_Byte,options=['COMPRESS=DEFLATE','TILED=YES']);r.SetGeoTransform(ds.GetGeoTransform());r.SetProjection(ds.GetProjection())
for i in range(3):r.GetRasterBand(i+1).WriteArray(rgb[:,:,i])
r.GetRasterBand(4).WriteArray((valid*255).astype('uint8'));r.GetRasterBand(4).SetColorInterpretation(gdal.GCI_AlphaBand);r=None
(D/'terrain-validation.json').write_text(json.dumps({'valid_fraction':float(valid.mean()),'nodata_rule':'source zero or nonfinite; valid elevation 100..1000m in this local crop','source_native_pixel_m':.5,'output_pixel_m':8,'valid_min_m':float(z[valid].min()),'valid_max_m':float(z[valid].max()),'coverage_note':'Minnesota crop only; Canada and other missing cells transparent'},indent=2))
print('Prepared',len(routes),'route segments',len(points),'trip points and',len(fs),'lake records')
