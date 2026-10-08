"""Download a route-wide lidar service crop at 8m output; native service is 0.5m."""
import json,urllib.request,urllib.parse
from pathlib import Path
from osgeo import osr,gdal
S=Path(__file__).resolve().parents[1]/'sources'
base='https://enterprise.gisdata.mn.gov/agsimg/rest/services/MnTopo/2nd_Generation_Seamless_Lidar_DEM/ImageServer'
src=osr.SpatialReference();src.ImportFromEPSG(4326);src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
dst=osr.SpatialReference();dst.ImportFromEPSG(26915);dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
t=osr.CoordinateTransformation(src,dst)
pts=[t.TransformPoint(x,y) for x in [-90.53,-90.04] for y in [48.005,48.15]]
b=[min(x[0] for x in pts),min(x[1] for x in pts),max(x[0] for x in pts),max(x[1] for x in pts)]
b=[int(b[0]//8)*8,int(b[1]//8)*8,int(b[2]//8+1)*8,int(b[3]//8+1)*8]
p={'f':'json','bbox':','.join(map(str,b)),'bboxSR':26915,'imageSR':26915,'size':f'{(b[2]-b[0])//8},{(b[3]-b[1])//8}','format':'tiff','pixelType':'F32','interpolation':'RSP_BilinearInterpolation','renderingRule':json.dumps({'rasterFunction':'None'})}
u=base+'/exportImage?'+urllib.parse.urlencode(p)
if not (S/'lidar-route-8m.tif').exists():
 j=json.load(urllib.request.urlopen(u,timeout=240));assert 'href' in j,j
 (S/'lidar-route-request.json').write_text(json.dumps({'url':u,'parameters':p,'response':j,'native_pixel_m':.5,'output_pixel_m':8},indent=2))
 print('downloading',j['href'],flush=True)
 urllib.request.urlretrieve(j['href'],S/'lidar-route-download.tif')
 gdal.Translate(str(S/'lidar-route-8m.tif'),str(S/'lidar-route-download.tif'),creationOptions=['COMPRESS=DEFLATE','PREDICTOR=3','TILED=YES'])
 (S/'lidar-route-download.tif').unlink()
ds=gdal.Open(str(S/'lidar-route-8m.tif'));print('size',ds.RasterXSize,ds.RasterYSize,ds.GetGeoTransform(),ds.GetRasterBand(1).GetStatistics(False,True),flush=True)
