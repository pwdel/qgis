"""Build real-world evidence and timing records, independently of the drawing."""
import json,csv,math,itertools,shutil
from pathlib import Path
import shapely
from shapely.geometry import shape,mapping,Point,LineString
from shapely.ops import transform,unary_union,nearest_points
from pyproj.transformer import TransformerGroup
from timing import ASSUMPTIONS,paddle,carry,hours
from waterpath import waterpath
R=Path(__file__).resolve().parents[1];P=R.parent;D=R/'data';S=R/'sources'
for f in ['hydrography.geojson','usfs-trails.json','acquisition.json','published-loop.gpx']:

 if not (S/f).exists():shutil.copy2(P/'sources'/f,S/f)
for f in ['map-data.json','passages-approximate.geojson','portages-recorded.geojson','high-points.geojson','start.geojson']:

 if not (S/f).exists():shutil.copy2(P/'derived'/f,S/f)
t=next(x for x in TransformerGroup(4326,26915,always_xy=True).transformers if '(1)' in x.description)
names=['Clearwater','West Pike','East Pike','John','Little John','McFarland','Pine','Little Caribou','Caribou','Mountain','Watap','Rove','Rose','Deer','Canoe','Alder','Crystal','Duncan','Bearskin','Fan','Vaseux','Moose']
w={}
hydro=json.load(open(S/'hydrography.geojson'))['features']
hydro += [f for f in json.load(open(S/'western-hydrography.geojson'))['features'] if f['properties'].get('pw_basin_name') in ['Duncan','Bearskin']]
for f in hydro:
 n=(f['properties'].get('pw_basin_name') or '').replace(' (Canada)','')
 if n in names:
  g=shapely.make_valid(transform(t.transform,shape(f['geometry'])))
  w[n]=unary_union([w[n],g]) if n in w else g
assert set(w)==set(names)
original_names=names.copy()
# Explicit object IDs prevent accidental merging of separate lakes sharing names.
selection=json.load(open(S/'expanded-selection.json'))
expanded_hydro={f['properties']['objectid']:f for f in json.load(open(S/'expanded-hydrography.geojson'))['features']}
for item in selection:
 n=item['name'];assert n not in w,n
 w[n]=unary_union([shapely.make_valid(transform(t.transform,shape(expanded_hydro[oid]['geometry']))) for oid in item['objectids']])
 names.append(n)
assert len(names)==80 and len(set(names))==80
def feat(g,**p):return {'type':'Feature','geometry':mapping(g),'properties':p}
def save(name,features):
 (D/(name+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::26915'}},'features':features}))
meta=json.load(open(S/'map-data.json'));print(type(meta['transitions']),flush=True)
old={f['properties']['id']:shape(f['geometry']) for f in json.load(open(S/'portages-recorded.geojson'))['features']}
approx={f['properties']['id']:shape(f['geometry']) for f in json.load(open(S/'passages-approximate.geojson'))['features']}
connections=[];geoc=[];modeled=[];endpoints={n:{} for n in names};records=[]
def add(cid,a,b,g,p,q,evidence,source,approximate=False,mode='carry'):
 p=nearest_points(p,w[a])[1];q=nearest_points(q,w[b])[1]
 # Include shoreline gaps in the length model, while retaining their provenance.
 gap=Point(g.coords[0]).distance(p)+Point(g.coords[-1]).distance(q)
 length=g.length+gap
 if mode=='carry':lo,hi=carry(length/1000)
 else:lo,hi=paddle(length/1000)
 rods=round(length/ASSUMPTIONS['rod_metres']) if mode=='carry' else None
 row=dict(id=cid,mode=mode,from_lake=a,to_lake=b,from_point=cid,to_point=cid,distance_m=length,rod_count=rods,rod_provenance='calculated from geometry; not official published count' if rods is not None else '',approximate=approximate,evidence=evidence,source=source,shore_extension_m=gap,low_h=lo,high_h=hi,display=hours(lo,hi),detour_low=.15 if mode!='carry' else 0,detour_high=.35 if mode!='carry' else 0)
 connections.append(row);records.append(row);geoc.append(feat(g,**row));modeled.append(feat(LineString([p.coords[0]]+list(g.coords)+[q.coords[0]]),**row));endpoints[a][cid]=p;endpoints[b][cid]=q
for e in meta['transitions']:
 cid=e['id'];a=e['from_lake'];b=e['to_lake'];g=approx.get(cid,old.get(cid))
 p,q=map(Point,e['landing_xy'])
 if Point(g.coords[0]).distance(p)>Point(g.coords[-1]).distance(p):g=LineString(list(g.coords)[::-1])
 add(cid,a,b,g,p,q,e['evidence'],'USFS + published digitized GPX' if cid=='a' else e.get('source','Friends of BWCA digitized GPX'),cid in approx,'river' if cid=='f' else 'carry')
trails={f['attributes']['objectid']:f for f in json.load(open(S/'usfs-trails.json'))['features']}
trails.update({f['attributes']['objectid']:f for f in json.load(open(S/'western-usfs.json'))['features']})
for cid,a,b,oid in [('k','Clearwater','Mountain',9720610),('l','Mountain','Watap',9720794),('n','Rove','Rose',9720865),('o','Caribou','Deer',9720666),('p','Pine','Canoe',9720821),('q','Canoe','Alder',9720785),('r','Canoe','Crystal',9721319),('s','Rose','Duncan',9634578),('t','Duncan','Bearskin',9634447),('u','Mountain','Fan',9720972),('v','Fan','Vaseux',9720360),('w','Vaseux','Moose',9720609)]:
 g=transform(t.transform,LineString(trails[oid]['geometry']['paths'][0]));p,q=Point(g.coords[0]),Point(g.coords[-1])
 if p.distance(w[a])+q.distance(w[b])>q.distance(w[a])+p.distance(w[b]):g=LineString(list(g.coords)[::-1]);p,q=q,p
 assert max(p.distance(w[a]),q.distance(w[b]))<30,(cid,p.distance(w[a]),q.distance(w[b]))
 add(cid,a,b,g,p,q,'Complete USFS geometry; shoreline-derived landings',f'USFS objectid {oid}')
p,q=nearest_points(w['Watap'],w['Rove']);add('m','Watap','Rove',LineString([p,q]),p,q,'Narrow water connection; DNR polygons separated by 3.6 m; not a portage','DNR hydrography + Parks Canada Morse canoe-route history',True,'narrows')
# Reviewed manifest requires agreement with the USFS trail name, not proximity alone.
expanded_trails={f['attributes']['objectid']:f for f in json.load(open(S/'expanded-usfs.json'))['features']}
for item in json.load(open(S/'expanded-portages.json')):
 oid=item['objectid'];a=item['from_lake'];b=item['to_lake'];f=expanded_trails[oid]
 assert f['attributes']['trail_name']==item['trail_name']
 assert len(f['geometry']['paths'])==1
 g=transform(t.transform,LineString(f['geometry']['paths'][0]));p,q=Point(g.coords[0]),Point(g.coords[-1])
 assert max(p.distance(w[a]),q.distance(w[b]))<=30,(oid,a,b)
 add(item['id'],a,b,g,p,q,'Complete named USFS portage geometry; shoreline-derived landings',f"USFS objectid {oid}: {item['trail_name']}")
start=shape(json.load(open(S/'start.geojson'))['features'][0]['geometry']);endpoints['Clearwater']['S']=start
for n in names:
 if len(endpoints[n])==1 or n=='Rose':endpoints[n]['T']=w[n].representative_point()
paths=[];pairs={};omitted_pairs=[];failed_pairs=[]
for n in names:
 all_pairs=list(itertools.combinations(sorted(endpoints[n]),2))
 # A star plus adjacent landing pairs gives useful examples without a quadratic panel.
 chosen=all_pairs
 if n not in original_names and len(endpoints[n])>4:
  points=sorted(endpoints[n]);chosen=list(dict.fromkeys([(points[0],p) for p in points[1:]]+list(zip(points[1:],points[2:]))))
  omitted_pairs.extend(dict(lake=n,from_point=a,to_point=b,reason='Representative landing-pair selection') for a,b in all_pairs if (a,b) not in chosen)
 for a,b in chosen:
  try:line=waterpath(w[n],endpoints[n][a],endpoints[n][b])
  except (ValueError,AssertionError) as exc:
   if n in original_names and not (a.startswith('A') or b.startswith('A')):raise
   failed_pairs.append(dict(lake=n,from_point=a,to_point=b,reason=str(exc)));continue
  length=line.length
  # Larger allowance for shoreline complexity measured along a feasible base path.
  direct=endpoints[n][a].distance(endpoints[n][b]);ratio=length/max(direct,1)
  low,high=(.20,.35) if ratio>1.1 else (.15,.30)
  lo,hi=paddle(length/1000,low,high);rid=f'W{len(paths)+1:02}'
  bearing=(math.degrees(math.atan2(line.coords[-1][0]-line.coords[0][0],line.coords[-1][1]-line.coords[0][1]))+360)%360
  row=dict(id=rid,mode='paddle',from_lake=n,to_lake=n,from_point=a,to_point=b,distance_m=length,rod_count=None,rod_provenance='',approximate=True,evidence='Hypothetical water-contained base path; indirect travel modeled separately',source='MN DNR hydrography',shore_extension_m=0,low_h=lo,high_h=hi,display=hours(lo,hi),detour_low=low,detour_high=high,axis_grid_deg=round(bearing,1),exposure='Direction of adverse wind varies; same broad envelope either way, not a forecast',water_valid=w[n].buffer(2).covers(line))
  paths.append(feat(line,**row));records.append(row);pairs[(n,*sorted([a,b]))]=row
 print(n,'paths',len(endpoints[n])*(len(endpoints[n])-1)//2,flush=True)
# Match supported circuit transitions by ID; include the departure paddle and closing leg.
byid={x['id']:x for x in connections};routes=[]
for name,ids in [('A - Inner circuit',['a','b','h','i','j']),('B - Eastern circuit',['a','c','d','e','f','g','h','i','j'])]:
 n='Clearwater';entry='S';legs=[]
 for cid in ids:
  legs.append(pairs[(n,*sorted([entry,cid]))]['id']);legs.append(cid)
  c=byid[cid];assert c['from_lake']==n;n=c['to_lake'];entry=cid
 legs.append(pairs[(n,*sorted([entry,'S']))]['id'])
 lookup={x['id']:x for x in records};lo=sum(lookup[x]['low_h'] for x in legs);hi=sum(lookup[x]['high_h'] for x in legs)
 routes.append(dict(name=name,legs=legs,low_h=lo,high_h=hi,display=hours(lo,hi)))
# One northward out-and-back itinerary, with a hypothetical Rose turn point.
legs=[];n='Clearwater';entry='S'
for cid in ['k','l','m','n']:
 legs.extend([pairs[(n,*sorted([entry,cid]))]['id'],cid]);c=byid[cid];n=c['to_lake'];entry=cid
legs.append(pairs[('Rose',*sorted(['n','T']))]['id']);legs=legs+list(reversed(legs));lookup={x['id']:x for x in records}
lo=sum(lookup[x]['low_h'] for x in legs);hi=sum(lookup[x]['high_h'] for x in legs)
routes.append(dict(name='C - Rose out and back',legs=legs,low_h=lo,high_h=hi,display=hours(lo,hi)))
save('geographic-lakes',[feat(g,name=n,area_km2=g.area/1e6,connection_count=sum(n in [c['from_lake'],c['to_lake']] for c in connections),context_only=not bool(endpoints[n])) for n,g in w.items()]);save('geographic-connections',geoc);save('geographic-paddles',paths)
save('geographic-modeled-connections',modeled)
save('geographic-landings',[feat(p,lake=n,point_id=k,kind='Hypothetical turn point' if k=='T' else 'Departure' if k=='S' else 'Source-derived landing') for n,pts in endpoints.items() for k,p in pts.items()])
shutil.copy2(S/'high-points.geojson',D/'geographic-high-points.geojson')
(D/'network.json').write_text(json.dumps(dict(lakes=names,connections=connections,legs=records,routes=routes,coverage=dict(source_extent_wgs84=[-90.95,47.85,-90.28,48.2],context_only_lakes=[n for n in names if not endpoints[n]],omitted_paddle_pairs=omitted_pairs,failed_paddle_pairs=failed_pairs,portage_acceptance='Reviewed named USFS trail; both ends within 30 metres of corresponding DNR water polygon',paddle_selection='All original lake pairs; star plus adjacent landing pairs for added lakes with more than four landings')),indent=2));(D/'assumptions.json').write_text(json.dumps(ASSUMPTIONS,indent=2))
keys=list(dict.fromkeys(k for r in records for k in r))
with (D/'leg-times.csv').open('w') as f:
 out=csv.DictWriter(f,keys,lineterminator="\n");out.writeheader();out.writerows(records)
print('RESULT',len(names),'lakes',len(connections),'connections',len(paths),'paddle pairs',[(r['name'],r['display']) for r in routes],flush=True)
