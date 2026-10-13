"""Verify geometry, arithmetic, local CRS, and relocated native project export."""
import json,math,tempfile,shutil,gc,zipfile
from pathlib import Path
from shapely.geometry import shape,Point
from qgis.core import *
from timing import rounded
R=Path(__file__).resolve().parents[1];D=R/'data';checks=[]
def check(ok,message):
 assert ok,message
 checks.append(message)
A=json.load(open(D/'assumptions.json'))
net=json.load(open(D/'network.json'));lookup={r['id']:r for r in net['legs']}
check(len(net['lakes'])==80,'80 named lakes');check(len(set(net['lakes']))==80,'80 unique lake identities');check(len(net['connections'])>=23,'original connections plus sourced expansion')
water={f['properties']['name']:shape(f['geometry']) for f in json.load(open(D/'geographic-lakes.geojson'))['features']}
lands={(f['properties']['lake'],f['properties']['point_id']):shape(f['geometry']) for f in json.load(open(D/'geographic-landings.geojson'))['features']}
for f in json.load(open(D/'geographic-paddles.geojson'))['features']:
 p=f['properties'];g=shape(f['geometry']);n=p['from_lake'];id=p['id']
 check(water[n].buffer(2).covers(g),id+' stays within lake')
 check(Point(g.coords[0]).distance(lands[(n,p['from_point'])])<.01 and Point(g.coords[-1]).distance(lands[(n,p['to_point'])])<.01,id+' matches named connecting points')
 check(abs(g.length-p['distance_m'])<.001,id+' geographic distance agrees')
for f in json.load(open(D/'geographic-modeled-connections.geojson'))['features']:
 p=f['properties'];g=shape(f['geometry']);check(abs(g.length-p['distance_m'])<.001,p['id']+' length includes modeled shore extensions')
 check(Point(g.coords[0]).distance(lands[(p['from_lake'],p['id'])])<.01 and Point(g.coords[-1]).distance(lands[(p['to_lake'],p['id'])])<.01,p['id']+' modeled endpoints agree')
for r in net['legs']:
 d=r['distance_m']/1000
 if r['mode']=='carry':
  nl,nr=A['carry_traversals'];lf,ls=A['loaded_walk_kmh'];rf,rs=A['return_walk_kmh'];hl,hh=A['handling_minutes']
  lo=nl*d/lf+nr*d/rf+hl/60;hi=nl*d/ls+nr*d/rs+hh/60
 else:lo=d*(1+r['detour_low'])/A['paddle_kmh'][0];hi=d*(1+r['detour_high'])/A['paddle_kmh'][1]
 check(abs(lo-r['low_h'])<1e-9 and abs(hi-r['high_h'])<1e-9,r['id']+' independent timing arithmetic')
 a,b=rounded(lo,hi);check(a<=lo+1e-9 and b>=hi-1e-9,r['id']+' outward rounded bounds')
 check(bool(r['source']) and bool(r['evidence']),r['id']+' evidence recorded')
for route in net['routes']:
 cur=('Clearwater','S')
 for id in route['legs']:
  r=lookup[id];ends=[(r['from_lake'],r['from_point']),(r['to_lake'],r['to_point'])];check(cur in ends,route['name']+' contiguous '+id);cur=ends[1] if cur==ends[0] else ends[0]
 check(cur==('Clearwater','S'),route['name']+' closes at departure')
 check(abs(sum(lookup[id]['low_h'] for id in route['legs'])-route['low_h'])<1e-9 and abs(sum(lookup[id]['high_h'] for id in route['legs'])-route['high_h'])<1e-9,route['name']+' totals sum raw leg times')
for c in json.load(open(D/'diagram-layout.json'))['connection_checks']:
 check(c['start_boundary_gap']<1e-6 and c['end_boundary_gap']<1e-6,c['id']+' distorted carry attaches to source-corresponding shores')
 check(c['source_vertices']>=2 and c['diagram_vertices']>=2,c['id']+' source-shaped curve retained with shoreline clipping')

labels=json.load(open(D/'schematic-names.json'))['features']
check({f['properties']['lake'] for f in labels}==set(net['lakes']),'one explicitly associated name per lake')
times=json.load(open(D/'schematic-paddle-times.json'))['features']
check(len({f['properties']['lake'] for f in times})==len(times),'at most one time range per lake')
for f in times:
 p=f['properties'];r=lookup[p['leg_id']]
 check(p['lake']==r['from_lake'],'time range belongs to '+p['lake'])
 check(not any(t in p['label'] for t in [' h',' rd','landing']),'compact time label '+p['lake'])
diagram_water={f['properties']['name']:shape(f['geometry']) for f in json.load(open(D/'schematic-lakes.json'))['features']}
leaders=json.load(open(D/'schematic-leaders.json'))['features']
for f in json.load(open(D/'schematic-carries.json'))['features']+json.load(open(D/'schematic-rivers.json'))['features']:
 props=f['properties'];line=shape(f['geometry'])
 wrong=[n for n,g in diagram_water.items() if n not in [props['from_lake'],props['to_lake']] and line.intersection(g).length>.01]
 check(not wrong,'carry avoids unrelated lakes: '+props['id'])

for f in times:
 n=f['properties']['lake'];inside=diagram_water[n].covers(shape(f['geometry']))
 has_leader=any(l['properties'].get('lake')==n and l['properties']['kind'] in ['time-label','lake-label'] for l in leaders)
 check(inside or has_leader,'time inside lake or linked explicitly: '+n)
landmarks=json.load(open(D/'schematic-hill-labels.json'))['features']
check(len(landmarks)==8,'eight researched landmarks rendered')
check(sum(f['properties']['visibility']=='water-visible' for f in landmarks)==5,'five documented water-visible landmarks')
for f in json.load(open(D/'schematic-leaders.json'))['features']:
 p=f['properties']
 if p['kind'] in ['lake-label','time-label']:
  lake=next(shape(x['geometry']) for x in json.load(open(D/'schematic-lakes.json'))['features'] if x['properties']['name']==p['lake'])
  check(Point(shape(f['geometry']).coords[-1]).distance(lake)<1e-6,'leader touches intended lake '+p['lake'])

# Independently check the actual editable ink areas and low/high pair order.
bases=json.load(open(D/'schematic-pie-bases.json'))['features'];ink=json.load(open(D/'schematic-pie-ink.json'))['features']
ink_by={(f['properties']['leg_id'],f['properties']['estimate']):f for f in ink}
check(len(bases)==2*(len(times)+len(net['connections'])),'two daylight discs for each displayed estimate range')
for f in bases:
 p=f['properties'];g=shape(f['geometry']);r=lookup[p['leg_id']];expected=rounded(r['low_h'],r['high_h'])[0 if p['estimate']=='low' else 1]
 check(p['period_hours']==15 and abs(p['hours']-expected)<1e-10,'disc represents rounded hours: '+p['leg_id']+' '+p['estimate'])
 sector=ink_by.get((p['leg_id'],p['estimate']));area=shape(sector['geometry']).area if sector else 0
 check(abs(area/g.area-expected/15)<1e-4,'black area equals hours divided by 15: '+p['leg_id']+' '+p['estimate'])
 if sector:check(g.buffer(1e-8).covers(shape(sector['geometry'])),'black sector stays within white disc: '+p['leg_id'])
for id in {f['properties']['leg_id'] for f in bases}:
 pair={f['properties']['estimate']:shape(f['geometry']).centroid for f in bases if f['properties']['leg_id']==id}
 check(pair['low'].x<pair['high'].x and abs(pair['low'].y-pair['high'].y)<1e-8,'shorter estimate is left disc: '+id)

app=QgsApplication([],False);app.initQgis()
def project(root,fn):
 p=QgsProject();check(p.read(str(root/fn)),fn+' reopens')
 for l in p.mapLayers().values():
  check(l.isValid(),fn+' valid '+l.name())
  path=Path(l.source().split('|')[0]).resolve();check(path.is_relative_to(root.resolve()),fn+' local path '+l.name())
  check(l.crs()==p.crs(),fn+' layer CRS matches project '+l.name())
 if fn.startswith('journey'):
  check(not p.crs().isGeographic() and 'GEOGCRS' not in p.crs().toWkt(),fn+' engineering CRS, not geographic')
  check(len(p.layoutManager().layouts())==2+math.ceil(len(net['legs'])/26),fn+' all native editable layouts')
  check(all('diagram.gpkg' in l.source() for l in p.mapLayers().values()),fn+' all diagram layers use local-CRS GeoPackage')
 else:check(p.crs().authid()=='EPSG:26915',fn+' real UTM geographic evidence')
 return p
for fn in ['journey-network.qgz','journey-network.qgs','geographic-evidence.qgz']:
 p=project(R,fn);p.clear();del p
with tempfile.TemporaryDirectory(prefix='journey-portable-') as temp:
 dest=Path(temp)/'bundle';shutil.copytree(R,dest,ignore=shutil.ignore_patterns('*.zip','__pycache__','*.qgs~'))
 p=project(dest,'journey-network.qgz');lay=p.layoutManager().layoutByName('01 | The journey chart');ex=QgsLayoutExporter(lay);settings=QgsLayoutExporter.PdfExportSettings();settings.appendGeoreference=False
 check(ex.exportToPdf(str(Path(temp)/'relocated.pdf'),settings)==QgsLayoutExporter.ExportResult.Success,'relocated project exports PDF offline')
 del ex,lay;p.clear();del p
 p=project(dest,'geographic-evidence.qgz');p.clear();del p
for fn in ['journey-network.qgs']:
 check(str(R) not in (R/fn).read_text(),fn+' no absolute build paths')
for f in (R/'layouts').glob('*.qpt'):check(str(R) not in f.read_text(),f.name+' relative template paths')
result={'passed':len(checks),'failed':0,'checks':checks,'note':'Native QGIS offscreen reopen/export; rendered PDF visual review is separate.'};(R/'docs/validation.json').write_text(json.dumps(result,indent=2));print(len(checks),'checks passed',flush=True)
gc.collect();app.exitQgis()
