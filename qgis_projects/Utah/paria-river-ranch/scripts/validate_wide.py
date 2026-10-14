"""Independent PDF extent, GeoJSON geometry and archive checks."""
import json,zipfile,hashlib,subprocess
from pathlib import Path
from pypdf import PdfReader
from osgeo import gdal,ogr,osr
ROOT=Path(__file__).resolve().parents[1];m=json.loads((ROOT/'docs/wide-manifest.json').read_text());checks=[]
def check(ok,desc):
 checks.append({'passed':bool(ok),'check':desc})
 if not ok:raise AssertionError(desc)
check(len(m['pdfs'])==15,'15 theme PDFs')
for rec in m['pdfs']:
 path=ROOT/rec['file'];r=PdfReader(str(path));check(len(r.pages)==1,'one page '+path.name);vp=r.pages[0]['/VP'];check(len(vp)==1,'single GPS frame '+path.name)
 ds=gdal.Open(str(path));check(ds is not None,'GDAL reads '+path.name);neat=ogr.CreateGeometryFromWkt(ds.GetMetadata()['NEATLINE']);bounds=neat.GetEnvelope();b=rec['bounds'];check(max(abs(x-y) for x,y in zip(bounds,[b[0],b[2],b[1],b[3]]))<.2,'GPS extent within 20cm '+path.name)
 key={'ranch':'02-ranch','mount-carmel':'03-mount-carmel','red-canyon':'04-red-canyon'}[rec['area']];old=json.loads((ROOT/'sources'/(key+'-extent.json')).read_text())['bbox_utm12'];check(abs((b[2]-b[0])/(old[2]-old[0])-1.5)<1e-8,'1.5x width '+path.name);check(abs((b[3]-b[1])/(old[3]-old[1])-1.5)<1e-8,'1.5x height '+path.name)
for rec in m['geojson']:
 j=json.loads((ROOT/rec['file']).read_text());check(len(j['features'])==rec['features'],'feature count '+rec['file'])
 for ft in j['features']:
  g=ogr.CreateGeometryFromJson(json.dumps(ft['geometry']));check(g is not None and g.IsValid(),'valid geometry '+rec['file']);b=g.GetEnvelope();check(-180<=b[0]<=b[1]<=180 and -90<=b[2]<=b[3]<=90,'WGS84 coordinate bounds');check(bool(ft['properties']['atlas_source']),'citation preserved')
for slug in ['ranch','mount-carmel','red-canyon']:
 f=ROOT/'output/pdf/wide'/(slug+'-share.zip')
 with zipfile.ZipFile(f) as z:check(z.testzip() is None,'ZIP integrity '+slug);check(len([n for n in z.namelist() if n.endswith('-wide.pdf')])==5,'five maps in '+slug)
 check(f.stat().st_size<100*1024*1024,'GitHub file limit '+slug)
for rec in m['raster_coverage']:
 if rec['covers_map_bbox'] or 'Native 1m' in rec['layer']:continue
 ds=gdal.Open(str(ROOT/rec['source']));gt=ds.GetGeoTransform();b=next(x['bounds'] for x in m['pdfs'] if x['area']==rec['area']);r=[gt[0],gt[3]+gt[5]*ds.RasterYSize,gt[0]+gt[1]*ds.RasterXSize,gt[3]]
 check(r[0]<=b[0]+1e-6 and r[1]<=b[1]+1e-6 and r[2]>=b[2]-1e-6 and r[3]>=b[3]-1e-6,'coverage rounding tolerance '+rec['layer']);rec['coverage_note']='Full coverage within one micrometre coordinate rounding tolerance.'
summary={'passed':len(checks),'failed':0,'device_tested':False,'raster_coverage_exceptions':[x for x in m['raster_coverage'] if not x['covers_map_bbox']]};(ROOT/'docs/wide-validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
