"""Run with GDAL Python. Fetch UTM topo/terrain subsets; preserve exact requests."""
import concurrent.futures
import json
from pathlib import Path
from osgeo import gdal, osr
from fetch_sources import get, js, save, OUT

gdal.UseExceptions()
SHEETS = [
    ('01-region', -112.25, 37.43, 140000),
    ('02-ranch', -111.987, 37.16, 33000),
    ('03-mount-carmel', -112.73, 37.211, 16000),
    ('04-red-canyon', -112.29, 37.771, 22000),
]
TOPO = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer'
DEM = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer'
ASPECT = 298 / 202
geo, utm = osr.SpatialReference(), osr.SpatialReference()
geo.ImportFromEPSG(4326); utm.ImportFromEPSG(26912)
geo.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
utm.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
transform = osr.CoordinateTransformation(geo, utm)

def fetch_sheet(s):
    name, lon, lat, width = s
    x, y, _ = transform.TransformPoint(lon, lat)
    height = width / ASPECT
    bbox = [x-width/2, y-height/2, x+width/2, y+height/2]
    info = {'id': name, 'center_wgs84': [lon, lat], 'bbox_utm12': bbox,
            'crs': 'EPSG:26912', 'width_m': width, 'height_m': height,
            'extent_basis': 'provisional editorial extent; Peter extent not supplied'}
    save(OUT / (name+'-extent.json'), info)
    common = {'bbox': ','.join(map(str, bbox)), 'bboxSR': 26912, 'imageSR': 26912,
              'size': '3600,2440', 'f': 'json'}
    for kind, base, endpoint, extra in [
        ('topo', TOPO, '/export', {'format': 'png32','dpi': 300}),
        ('dem', DEM, '/exportImage', {'format':'tiff', 'pixelType':'F32',
         'size':'1600,1085', 'interpolation':'RSP_BilinearInterpolation',
         'renderingRule': json.dumps({'rasterFunction':'None'})})]:
        dest=OUT/(name+'-'+kind+('.png' if kind=='topo' else '.tif'))
        if dest.exists() or (kind=='topo' and (OUT/(name+'-topo.tif')).exists()): continue
        params={**common, **extra}
        if kind=='dem':params['interpolation']='RSP_BilinearInterpolation'
        response, url=js(base+endpoint,params)
        save(OUT/(name+'-'+kind+'-request.json'),{'url':url,'parameters':params,'response':response})
        data, _=get(response['href']);dest.write_bytes(data)
        if kind=='topo':
            e=response['extent'];bounds=[e['xmin'],e['ymax'],e['xmax'],e['ymin']]
            gdal.Translate(str(OUT/(name+'-topo.tif')),str(dest),outputSRS='EPSG:26912',
                           outputBounds=bounds,creationOptions=['COMPRESS=DEFLATE'])
            dest.unlink()
        print(name,kind,len(data),flush=True)
    # Catalog identifies contributing candidates; not exact per-pixel source attribution.
    q={'f':'json','where':'1=1','geometry':','.join(map(str,bbox)), 'inSR':26912,
       'spatialRel':'esriSpatialRelIntersects','geometryType':'esriGeometryEnvelope',
       'outFields':'OBJECTID,Name,LowPS,HighPS,DEM_Type,VerticalDatum,AcquisitionDate,URL,title,StartDate,EndDate',
       'returnGeometry':'false'}
    d,u=js(DEM+'/query',q)
    save(OUT/(name+'-dem-catalog.json'),{'url':u,'response':d,
       'complete':not d.get('exceededTransferLimit',False),
       'interpretation':'Candidate catalog query only; exact contributing DEM per pixel unresolved.'})
    return info

if __name__=='__main__':
    for name,u in [('topo',TOPO),('dem',DEM)]:
        d,_=js(u,{'f':'json'});save(OUT/(name+'-service.json'),d)
    # Transformation object is used sequentially (GDAL transform thread safety).
    for s in SHEETS: fetch_sheet(s)
    d,u=js('https://www.recreation.gov/api/camps/campgrounds/10381898')
    save(OUT/'coyote-hollow-facility.json',{'url':u,'response':d})
    q={'datasets':'Digital Elevation Model (DEM) 1 meter','bbox':'-112.34,37.72,-112.29,37.75','max':20}
    d,u=js('https://tnmaccess.nationalmap.gov/api/v1/products',q)
    save(OUT/'native-lidar-catalog.json',{'url':u,'response':d})
    # Fetch a small native-resolution area with HTTP range reads, not entire 10 km tile.
    item=next(x for x in d['items'] if 'UT_StatewideKane_2020_A20' in x['title'])
    src=gdal.Open('/vsicurl/'+item['downloadURL'])
    p=transform.TransformPoint(-112.319,37.735)
    gdal.Warp(str(OUT/'thunder-native-1m.tif'),src,dstSRS='EPSG:26912',
       outputBounds=[p[0]-1600,p[1]-1600,p[0]+1600,p[1]+1600],xRes=1,yRes=1,
       resampleAlg='bilinear',creationOptions=['COMPRESS=DEFLATE','PREDICTOR=3'])
    save(OUT/'thunder-native-request.json',{'source':item,'crop_center_wgs84':[-112.319,37.735],
       'crop_width_m':3200,'output_crs':'EPSG:26912','resampling':'bilinear',
       'note':'Native 1m source DEM reprojected to atlas CRS; project title is not acquisition date.'})
    print('native terrain subset downloaded',flush=True)
