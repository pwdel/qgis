#!/usr/bin/env python3
"""Fetch checked authoritative fire records and WRC annual likelihood visualization."""
import json, datetime, math, collections, html
from pathlib import Path
import requests
from osgeo import gdal, ogr, osr
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'sources/fire-data'; OUT=ROOT/'derived/fire-data'
SRC.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
FOD='https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrenceCurrentEdition_01/MapServer'
MTBS='https://apps.fs.usda.gov/ArcX/rest/services/EDW/EDW_MTBS_01/MapServer'
BP='https://imagery.geoplatform.gov/iipp/rest/services/Fire_Aviation/USFS_EDW_RMRS_WRC_BurnProbability/ImageServer'
def save(path,obj): path.write_text(json.dumps(obj,indent=2)+'\n')
def get(url,p=None):
    r=requests.get(url,params=p or {'f':'json'},timeout=180);r.raise_for_status();j=r.json()
    if 'error' in j: raise RuntimeError(j)
    return j

def records(base,layer,area,label):
    name=area['id']+'-'+label; url=base+'/'+str(layer)+'/query'
    p={'f':'json','where':'1=1','geometry':','.join(map(str,area['bbox_utm12'])),'geometryType':'esriGeometryEnvelope','inSR':26912,'spatialRel':'esriSpatialRelIntersects'}
    ids=get(url,{**p,'returnIdsOnly':'true'}); count=get(url,{**p,'returnCountOnly':'true'})
    save(SRC/(name+'-ids.json'),ids);save(SRC/(name+'-count.json'),count)
    oid=ids.get('objectIdFieldName','objectid'); wanted=sorted(ids.get('objectIds') or [])
    assert len(wanted)==len(set(wanted))==count['count']
    features=[]
    for i in range(0,len(wanted),100):
        batch=get(url,{'f':'geojson','objectIds':','.join(map(str,wanted[i:i+100])),'outFields':'*','outSR':4326,'returnGeometry':'true'})
        assert not batch.get('exceededTransferLimit')
        features.extend(batch['features'])
    actual=sorted(f['properties'].get(oid,f.get('id')) for f in features)
    assert actual==wanted,(name,len(actual),len(wanted))
    save(SRC/(name+'-request.json'),{'url':url,'parameters':p,'retrieved_utc':NOW,'count':count['count'],'id_count':len(wanted),'downloaded_count':len(features),'complete_ids_match':True,'batch_size':100})
    # Independently verify returned geographic geometries intersect the requested UTM map box.
    wgs=osr.SpatialReference();wgs.ImportFromEPSG(4326);wgs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    utm=osr.SpatialReference();utm.ImportFromEPSG(26912);utm.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    transform=osr.CoordinateTransformation(wgs,utm);b=area['bbox_utm12']
    ring=ogr.Geometry(ogr.wkbLinearRing)
    for x,y in [(b[0],b[1]),(b[2],b[1]),(b[2],b[3]),(b[0],b[3]),(b[0],b[1])]:ring.AddPoint(x,y)
    box=ogr.Geometry(ogr.wkbPolygon);box.AddGeometry(ring)
    save(SRC/(name+'-candidates.geojson'),{'type':'FeatureCollection','features':features})
    selected=[];excluded=[]
    for feature in features:
        geometry=ogr.CreateGeometryFromJson(json.dumps(feature['geometry']));geometry.Transform(transform)
        if geometry.Intersects(box):selected.append(feature)
        else:excluded.append(feature.get('id'))
    save(SRC/(name+'-geographic-check.json'),{'checked_count':len(features),'selected_count':len(selected),'excluded_candidate_ids':excluded,'all_selected_intersect_exact_utm_extent':True,'crs':'EPSG:26912','bbox':b})
    fc={'type':'FeatureCollection','features':selected};save(OUT/(name+'.geojson'),fc)
    return selected

def chart(area,monthly,total,missing):
    maximum=max(monthly+[1]); svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="240" viewBox="0 0 900 240">','<rect width="900" height="240" fill="#fffaf1"/>']
    def text(x,y,t,size=15,color='#26352f',anchor='start'):
        svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans,sans-serif" font-size="{size}" text-anchor="{anchor}">{html.escape(str(t))}</text>')
    text(22,25,'Recorded wildfire discoveries by month | FPA FOD 1992–2024',20)
    for i,(label,n) in enumerate(zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],monthly)):
        x=38+i*71;h=118*n/maximum;color='#b94c25' if i==9 else '#506f61'
        svg.append(f'<rect x="{x}" y="{178-h}" width="47" height="{h}" fill="{color}"/>')
        text(x+23.5,169-h,n,14,color,'middle');text(x+23.5,198,label,15,color,'middle')
    text(22,224,f'n={total}; unknown month={missing}. Counts within map extent; October highlighted. Not monthly burn probability.',13)
    svg.append('</svg>');(OUT/(area['id']+'-monthly.svg')).write_text('\n'.join(svg))

def raster(area):
    key=area['id'];b=area['bbox_utm12'];p={'f':'json','bbox':','.join(map(str,b)),'bboxSR':26912,'imageSR':26912,'size':f'{math.ceil((b[2]-b[0])/30)},{math.ceil((b[3]-b[1])/30)}','format':'tiff','pixelType':'U16','interpolation':'+RSP_NearestNeighbor','renderingRule':json.dumps({'rasterFunction':'None'})}
    result={'status':'unknown_numeric_probability','source':BP,'edition':'WRC 2024, second edition','landscape_vintage':'end of 2020','native_model_resolution_m':270,'published_cell_m':30,'monthly_probability':None,'october_probability':None,'limitation':'ImageServer values altered for visualization; no supported conversion to annual probability. Original Utah archive is 6.39 GB. Raster is relative annual likelihood visualization only, not numeric probability or a forecast.'}
    try:
        j=get(BP+'/exportImage',p);save(SRC/(key+'-annual-likelihood-export.json'),{'request':p,'response':j,'retrieved_utc':NOW})
        r=requests.get(j['href'],timeout=180);r.raise_for_status();path=OUT/(key+'-annual-likelihood-visualization.tif');path.write_bytes(r.content)
        ds=gdal.Open(str(path));assert ds and ds.RasterCount==1
        band=ds.GetRasterBand(1);arr=band.ReadAsArray();nd=band.GetNoDataValue();valid=arr[arr!=nd] if nd is not None else arr.ravel();assert valid.size
        result.update({'raster':str(path.relative_to(ROOT)),'visualization_available':True,'raw_value_min':float(valid.min()),'raw_value_max':float(valid.max()),'nodata':nd,'crs':ds.GetProjection(),'geotransform':ds.GetGeoTransform(),'dimensions':[ds.RasterXSize,ds.RasterYSize]})
    except Exception as e:result.update({'visualization_available':False,'error':str(e)})
    try:
        rp={**p,'format':'png32','renderingRule':json.dumps({'rasterFunction':'BurnProbability2024'})};rp.pop('pixelType',None)
        j=get(BP+'/exportImage',rp);save(SRC/(key+'-annual-likelihood-rendered-export.json'),{'request':rp,'response':j,'retrieved_utc':NOW})
        r=requests.get(j['href'],timeout=180);r.raise_for_status();png=SRC/(key+'-annual-likelihood-rendered.png');png.write_bytes(r.content)
        path=OUT/(key+'-annual-likelihood-rendered.tif');ext=j['extent']
        ds=gdal.Translate(str(path),str(png),outputSRS='EPSG:26912',outputBounds=[ext['xmin'],ext['ymax'],ext['xmax'],ext['ymin']],creationOptions=['COMPRESS=DEFLATE']);assert ds and ds.RasterCount in (3,4)
        result['rendered_raster']=str(path.relative_to(ROOT));result['rendered_bands']=ds.RasterCount
    except Exception as e:result['rendered_error']=str(e)
    save(OUT/(key+'-annual-likelihood-metadata.json'),result);return result

def main():
    for label,u in [('fpa-fod',FOD),('mtbs',MTBS),('wrc-burn-probability',BP)]:save(SRC/(label+'-service.json'),get(u))
    save(SRC/'fpa-fod-layer.json',get(FOD+'/0'));save(SRC/'mtbs-layer.json',get(MTBS+'/63'));save(SRC/'wrc-iteminfo.json',get(BP+'/info/iteminfo'));save(SRC/'wrc-legend.json',get(BP+'/legend'))
    for label,url in [('wrc-archive','https://www.fs.usda.gov/rds/archive/catalog/RDS-2020-0016-2'),('wrc-archive-metadata','https://www.fs.usda.gov/rds/archive/products/RDS-2020-0016-2/_metadata_RDS-2020-0016-2.html')]:
        r=requests.get(url,timeout=180);r.raise_for_status();(SRC/(label+'.html')).write_text(r.text)
    save(SRC/'wrc-official-viewer.json',get('https://www.arcgis.com/sharing/rest/content/items/78e7e78bcef64dfc98cf13e2e0eae156/data'))
    save(SRC/'wrc-official-webmap.json',get('https://www.arcgis.com/sharing/rest/content/items/43fc7ec110b0401c8218502512e43045/data'))
    stats=[{'statisticType':s,'onStatisticField':'year','outStatisticFieldName':s+'_year'} for s in ['min','max']]
    period=get(MTBS+'/63/query',{'f':'json','where':'1=1','outStatistics':json.dumps(stats),'returnGeometry':'false'});save(SRC/'mtbs-period.json',period)
    summary={'schema_version':1,'retrieved_utc':NOW,'occurrence_edition':'FPA FOD seventh edition FPA_FOD_20260615','sample_period':[1992,2024],'mtbs_period_evidence':period,'areas':{}}
    for key in ['02-ranch','03-mount-carmel','04-red-canyon']:
        a=json.loads((ROOT/'sources'/(key+'-extent.json')).read_text());print('Fetching',key,flush=True)
        occ=records(FOD,0,a,'occurrences');per=records(MTBS,63,a,'perimeters');monthly=[0]*12;missing=0;years=[]
        for f in occ:
            p=f['properties'];years.append(p['fire_year']);date=p.get('discovery_date')
            if date is None:missing+=1;continue
            dt=datetime.datetime.fromtimestamp(date/1000,datetime.timezone.utc) if isinstance(date,(int,float)) else datetime.datetime.fromisoformat(date.replace('Z','+00:00'))
            monthly[dt.month-1]+=1
        assert sum(monthly)+missing==len(occ)
        chart(a,monthly,len(occ),missing)
        summary['areas'][key]={'extent':a,'occurrence_count':len(occ),'sample_period':[1992,2024],'observed_year_range':[min(years),max(years)] if years else None,'monthly_counts':monthly,'unknown_month_count':missing,'october_count':monthly[9],'october_share_of_known_months':monthly[9]/sum(monthly) if sum(monthly) else None,'perimeter_count':len(per),'perimeter_type_counts':dict(collections.Counter(f['properties']['fire_type'] for f in per)),'perimeter_years':sorted(set(f['properties']['year'] for f in per)),'occurrences':f'derived/fire-data/{key}-occurrences.geojson','perimeters':f'derived/fire-data/{key}-perimeters.geojson','monthly_chart':f'derived/fire-data/{key}-monthly.svg','annual_burn_probability':raster(a)}
        save(OUT/'fire-summary.json',summary)
    print(json.dumps({k:{x:v[x] for x in ['occurrence_count','monthly_counts','perimeter_type_counts']} for k,v in summary['areas'].items()},indent=2))
if __name__=='__main__':main()
