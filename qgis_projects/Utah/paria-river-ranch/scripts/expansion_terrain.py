"""Terrain screening: percent cell slope and nearby lower ground, never trail grade."""
import json,math
from pathlib import Path
import numpy as np
from scipy.ndimage import minimum_filter
from osgeo import gdal,ogr,osr
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'derived'/'expansion';D.mkdir(exist_ok=True)
S=ROOT/'sources'
AREAS=['02-ranch','03-mount-carmel','04-red-canyon']
COLORS=[(30,45,(239,193,70,175)),(45,60,(235,134,49,190)),(60,90,(193,70,49,200)),(90,150,(135,58,115,210)),(150,1e6,(58,31,66,225))]
def percent(deg):return 100*np.tan(np.deg2rad(deg))
def nearby_lower(z,valid,pixel,radius=100):
    n=int(math.ceil(radius/pixel));a=np.arange(-n,n+1)*pixel
    foot=a[:,None]**2+a[None,:]**2<=radius**2
    low=minimum_filter(np.where(valid,z,np.inf),footprint=foot,mode='constant',cval=np.inf)
    # Require complete valid support; a missing cell is never treated as a deep drop.
    full=minimum_filter(valid.astype('uint8'),footprint=foot,mode='constant',cval=0).astype(bool)
    return np.where(full&valid,z-low,np.nan)
def write(ds,path,a,typ=gdal.GDT_Float32,nd=-9999):
    out=gdal.GetDriverByName('GTiff').Create(str(path),ds.RasterXSize,ds.RasterYSize,1,typ,options=['COMPRESS=DEFLATE'])
    out.SetGeoTransform(ds.GetGeoTransform());out.SetProjection(ds.GetProjection())
    out.GetRasterBand(1).WriteArray(np.where(np.isfinite(a),a,nd));out.GetRasterBand(1).SetNoDataValue(nd);out=None

def run():
    src=osr.SpatialReference();src.ImportFromEPSG(4326);src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    dst=osr.SpatialReference();dst.ImportFromEPSG(26912);dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    tx=osr.CoordinateTransformation(src,dst);back=osr.CoordinateTransformation(dst,src)
    data=json.loads((S/'state-trails.geojson').read_text());lines=[]
    for f in data['features']:
        if not f.get('geometry'):continue
        g=ogr.CreateGeometryFromJson(json.dumps(f['geometry']));g.Transform(tx);lines.append(g)
    all_points=[];stats={}
    for name in AREAS:
        ds=gdal.Open(str(S/(name+'-dem.tif')));z=ds.ReadAsArray().astype(float);gt=ds.GetGeoTransform();pixel=gt[1]
        valid=np.isfinite(z)&(z!=ds.GetRasterBand(1).GetNoDataValue())
        sd=gdal.Open(str(ROOT/'derived'/(name+'-slope-degrees.tif')));ang=sd.ReadAsArray();sv=(ang>=0)&(ang<90)&valid
        grade=np.where(sv,percent(np.where(sv,ang,0)),np.nan);drop=nearby_lower(z,valid,pixel)
        write(ds,D/(name+'-slope-percent.tif'),grade);write(ds,D/(name+'-lower-ground-100m.tif'),drop)
        mem=ogr.GetDriverByName('Memory').CreateDataSource('');lyr=mem.CreateLayer('trails',dst,ogr.wkbMultiLineString)
        bounds=ogr.CreateGeometryFromWkt(f'POLYGON (({gt[0]} {gt[3]}, {gt[0]+pixel*z.shape[1]} {gt[3]}, {gt[0]+pixel*z.shape[1]} {gt[3]+gt[5]*z.shape[0]}, {gt[0]} {gt[3]+gt[5]*z.shape[0]}, {gt[0]} {gt[3]}))')
        for g in lines:
            if g.Intersects(bounds):
                f=ogr.Feature(lyr.GetLayerDefn());f.SetGeometry(g);lyr.CreateFeature(f)
        mask=gdal.GetDriverByName('MEM').Create('',ds.RasterXSize,ds.RasterYSize,1,gdal.GDT_Byte);mask.SetGeoTransform(gt);mask.SetProjection(ds.GetProjection())
        gdal.RasterizeLayer(mask,[1],lyr,burn_values=[1]);ontrail=mask.ReadAsArray()>0
        from scipy.ndimage import distance_transform_edt
        corridor=distance_transform_edt(~ontrail,sampling=(abs(gt[5]),pixel))<=150
        write(ds,D/(name+'-trail-corridor.tif'),corridor.astype('uint8'),gdal.GDT_Byte,255)
        rgba=np.zeros((4,*z.shape),dtype='uint8')
        for lo,hi,col in COLORS:
            m=sv&corridor&(grade>=lo)&(grade<hi)
            for b,c in enumerate(col):rgba[b][m]=c
        missing=corridor&~sv
        for b,c in enumerate((100,100,100,160)):rgba[b][missing]=c
        out=gdal.GetDriverByName('GTiff').Create(str(D/(name+'-slope-overlay.tif')),ds.RasterXSize,ds.RasterYSize,4,gdal.GDT_Byte,options=['COMPRESS=DEFLATE']);out.SetGeoTransform(gt);out.SetProjection(ds.GetProjection())
        for b in range(4):out.GetRasterBand(b+1).WriteArray(rgba[b])
        out.GetRasterBand(4).SetColorInterpretation(gdal.GCI_AlphaBand);out=None
        # Select three separated review locations on rasterized source trail lines, not safe/unsafe routes.
        candidates=np.where(ontrail&np.isfinite(drop),drop,-np.inf);chosen=[]
        margin=int(math.ceil(1000/pixel));candidates[:margin,:]=-np.inf;candidates[-margin:,:]=-np.inf;candidates[:,:margin]=-np.inf;candidates[:,-margin:]=-np.inf
        for k in range(3):
            row,col=np.unravel_index(np.argmax(candidates),z.shape)
            if not np.isfinite(candidates[row,col]):break
            x=gt[0]+(col+.5)*pixel;y=gt[3]+(row+.5)*gt[5]
            lon,lat,_=back.TransformPoint(x,y);value=round(float(drop[row,col])/5)*5
            props={'area':name,'id':chr(65+k),'label':f'{chr(65+k)} / ~{value}m lower ground','drop_m_rounded_5':value,'radius_m':100,'cell_m':pixel,'cell_slope_percent':round(float(grade[row,col]),1) if sv[row,col] else None,'interpretation':'Trail raster-cell elevation minus lowest modeled ground within 100m; not cliff height or trail grade.'}
            chosen.append({'x':x,'y':y,**props});all_points.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':props})
            yy,xx=np.ogrid[:z.shape[0],:z.shape[1]];candidates[(xx-col)**2+(yy-row)**2<(1500/pixel)**2]=-np.inf
        stats[name]={'cell_m':pixel,'corridor_distance_m':150,'drop_search_radius_m':100,'trail_corridor_valid_slope_fraction':float((sv&corridor).sum()/corridor.sum()),'review_points':chosen,'source':str((S/(name+'-dem-request.json')).relative_to(ROOT))}
        print(name,'terrain',chosen,flush=True)
    (D/'review-points.geojson').write_text(json.dumps({'type':'FeatureCollection','features':all_points})+'\n')
    (ROOT/'docs'/'expansion-terrain.json').write_text(json.dumps(stats,indent=2)+'\n')
if __name__=='__main__':run()
