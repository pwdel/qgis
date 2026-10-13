"""Prepare evidence-backed teaching geometry; never invent a surveyed carry."""
import json,math,heapq,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import shape,mapping,Point,LineString,Polygon,box
from shapely.ops import transform,unary_union,nearest_points,substring
from shapely.affinity import scale,translate,rotate
from scipy.ndimage import gaussian_filter,maximum_filter,minimum_filter
from pyproj import Transformer,Proj
from pyproj.transformer import TransformerGroup
from osgeo import gdal
R=Path(__file__).resolve().parents[1];S=R/'sources';D=R/'derived'
gdal.UseExceptions()
t=next(x for x in TransformerGroup(4326,26915,always_xy=True).transformers if '(1)' in x.description)
inv=next(x for x in TransformerGroup(26915,4326,always_xy=True).transformers if '(1)' in x.description)
names=['Clearwater','West Pike','East Pike','John','Little John','McFarland','Pine','Little Caribou','Caribou']
water={};allwater=[]
for f in json.load(open(S/'hydrography.geojson'))['features']:
 g=shapely.make_valid(transform(t.transform,shape(f['geometry'])));allwater.append(g)
 n=f['properties'].get('pw_basin_name')
 if n in names:water[n]=unary_union([water[n],g]) if n in water else g
assert set(names)==set(water)
W=unary_union(allwater);core=unary_union(list(water.values()));extent=box(*core.bounds).buffer(900).envelope

def feat(g,**props):return {'type':'Feature','geometry':mapping(g),'properties':props}
def save(name,features):
 (D/(name+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::26915'}},'features':features},separators=(',',':')))

save('lakes',[feat(g,name=n,label=n+' Lake') for n,g in water.items()])
context=[]
for f,g in zip(json.load(open(S/'hydrography.geojson'))['features'],allwater):
 n=f['properties'].get('pw_basin_name')
 if n not in names and g.intersects(extent):context.append(feat(g.intersection(extent),name=n or 'Unnamed'))
save('context-water',context)
echo=[]
for n,g in water.items():
 for d in [24,58]:
  b=g.buffer(-d)
  if not b.is_empty:echo.append(feat(b.boundary,name=n,inset_m=d))
save('shore-echo',echo)
# The publisher explicitly labels this GPX as digitized; it is not a GPS survey.
published=LineString([t.transform(float(p.attrib['lon']),float(p.attrib['lat'])) for p in ET.parse(S/'published-loop.gpx').findall('.//trkpt')])
intervals={}
for n,w in water.items():
 g=published.intersection(w);parts=list(g.geoms) if hasattr(g,'geoms') else [g]
 intervals[n]=sorted((published.project(Point(p.coords[0])),published.project(Point(p.coords[-1]))) for p in parts if p.geom_type=='LineString')
# Official polylines are stored in full, including incomplete segments.
trails=json.load(open(S/'usfs-trails.json'))['features'];byname={}
for f in trails:byname.setdefault(f['attributes'].get('trail_name'),[]).append(f)
specs=[('a','Clearwater','West Pike','CLEARWATER-WEST PIKE'),('b','West Pike','Pine','WEST PIKE-PINE'),('c','West Pike','East Pike','EAST PIKE-WEST PIKE'),('d','East Pike','John','JOHN-EAST PIKE'),('e','John','Little John','LITTLE JOHN-JOHN LAKE'),('f','Little John','McFarland',None),('g','McFarland','Pine','MCFARLAND LAKE-PINE LAKE'),('h','Pine','Little Caribou',None),('i','Little Caribou','Caribou',None),('j','Caribou','Clearwater','CLEARWATER LAKE-CARIBOU LAKE')]
landings=[];exact=[];sketch=[];clues=[];transitions={};evidence=[]
for cid,a,b,trailname in specs:
 record={'id':cid,'from_lake':a,'to_lake':b,'field_verified':False}
 if cid=='b':p0=p1=None;pub=None
 else:
  end=intervals[a][0][1] if a=='Clearwater' else intervals[a][-1][1]
  start=intervals[b][-1][0] if b=='Clearwater' else intervals[b][0][0]
  pub=substring(published,end,start);p0,p1=Point(pub.coords[0]),Point(pub.coords[-1])
 chosen=None
 if trailname:
  candidates=[]
  for f in byname[trailname]:
   for path in f['geometry']['paths']:
    g=transform(t.transform,LineString(path));p,q=Point(g.coords[0]),Point(g.coords[-1])
    if p.distance(water[a])+q.distance(water[b])>q.distance(water[a])+p.distance(water[b]):g=LineString(list(g.coords)[::-1]);p,q=q,p
    score=(p.distance(p0)+q.distance(p1)) if p0 is not None else p.distance(water[a])+q.distance(water[b])
    candidates.append((score,g,f))
  _,g,f=min(candidates,key=lambda x:x[0]);chosen=g
  gaps=[Point(g.coords[0]).distance(water[a]),Point(g.coords[-1]).distance(water[b])]
  record.update(usfs_objectid=f['attributes']['objectid'],shore_gaps_m=[round(x,1) for x in gaps],source='USFS 2026-10-12')
  exact.append(feat(g,**record,kind='recorded trail',trail_name=trailname))
  if max(gaps)<=50:
   p0=nearest_points(Point(g.coords[0]),water[a].boundary)[1];p1=nearest_points(Point(g.coords[-1]),water[b].boundary)[1]
   record['evidence']='USFS geometry with shoreline-derived landings'
  else:
   record['evidence']='Incomplete USFS geometry; digitized GPX supports approximate passage'
   sketch.append(feat(pub,**record,kind='published sketch; not surveyed'))
 else:
  record['evidence']='Published digitized GPX; no matching USFS trail geometry'
  if cid=='f':record['evidence']='Short river connection, generalized GPX; water polygons have a gap'
  sketch.append(feat(pub,**record,kind='river connection' if cid=='f' else 'published sketch; not surveyed'))
 record['kind']='river connection' if cid=='f' else 'portage'
 assert p0 is not None and p1 is not None
 transitions[cid]=(a,b,p0,p1)
 record['landing_xy']=[list(p0.coords[0]),list(p1.coords[0])]
 evidence.append(record)
 for k,(n,p) in enumerate([(a,p0),(b,p1)]):
  landings.append(feat(p,**record,lake=n,end=k))
  # Offset irregular ellipses: an exercise search area, never a trail corridor.
  center=Point(p.x+(75 if k else -95),p.y+(35 if k else -45))
  xy=[]
  for j in range(49):
   ang=j*2*math.pi/48;rad=1+.075*math.sin(3*ang+ord(cid))+.04*math.cos(5*ang)
   xy.append((center.x+340*rad*math.cos(ang),center.y+230*rad*math.sin(ang)))
  poly=Polygon(xy)
  clues.append(feat(poly,id=cid,lake=n,label=cid,kind='broad passage clue',teaching_generalization=True))
# Merge overlapping end clues only where they already form a single broad area.
merged=[]
for cid,_,_,_ in specs:
 gs=[shape(f['geometry']) for f in clues if f['properties']['id']==cid]
 u=unary_union(gs)
 parts=list(u.geoms) if u.geom_type=='MultiPolygon' else [u]
 for k,g in enumerate(parts):merged.append(feat(g,id=cid,label=cid,kind='broad passage clue',teaching_generalization=True))
# Two choices share the same West Pike shore: give the shared area both letters.
coalesced=[]
for f in merged:
 g=shape(f['geometry']);match=None
 for prior in coalesced:
  h=shape(prior['geometry'])
  if g.intersection(h).area/min(g.area,h.area)>.75:match=prior;break
 if match is None:coalesced.append(f)
 else:
  match['geometry']=mapping(unary_union([g,shape(match['geometry'])]))
  match['properties']['label']+=' / '+f['properties']['label']
merged=coalesced
save('clues',merged);save('portages-recorded',exact);save('passages-approximate',sketch);save('landings-instructor',landings)

# Find water-contained teaching legs on a 25 m lattice. Check every shortcut.
def waterpath(w,start,end,step=25):
 allowed=w.buffer(2)
 if allowed.covers(LineString([start,end])):return LineString([start,end])
 xmin,ymin,xmax,ymax=w.bounds
 xs=np.arange(xmin+step/2,xmax,step);ys=np.arange(ymin+step/2,ymax,step)
 xx,yy=np.meshgrid(xs,ys);mask=shapely.contains_xy(w,xx,yy);rr,cc=np.where(mask)
 centers=np.column_stack([xs[cc],ys[rr]])
 def endpoint(p):
  ids=np.argsort(np.sum((centers-np.array(p.coords[0]))**2,axis=1))[:160]
  for idx in ids:
   q=Point(centers[idx])
   if allowed.covers(LineString([p,q])):return int(rr[idx]),int(cc[idx])
  raise ValueError('No water access from '+p.wkt)
 s=endpoint(start);goal=endpoint(end);heap=[(0,0,s)];dist={s:0};prev={};done=set()
 while heap:
  _,cost,u=heapq.heappop(heap)
  if u in done:continue
  if u==goal:break
  done.add(u);r,c=u
  for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   v=(r+dr,c+dc);nr,nc=v
   if not (0<=nr<len(ys) and 0<=nc<len(xs) and mask[nr,nc]):continue
   new=cost+math.hypot(dr,dc)*step
   if new>=dist.get(v,float('inf')):continue
   if not allowed.covers(LineString([(xs[c],ys[r]),(xs[nc],ys[nr])])):continue
   dist[v]=new;prev[v]=u;h=math.hypot(nr-goal[0],nc-goal[1])*step;heapq.heappush(heap,(new+h,new,v))
 assert goal in dist,'No water route'
 nodes=[goal]
 while nodes[-1]!=s:nodes.append(prev[nodes[-1]])
 nodes.reverse();pts=[start]+[Point(xs[c],ys[r]) for r,c in nodes]+[end]
 # Greedy visible shortcuts preserve islands and peninsulas.
 out=[pts[0]];i=0
 while i<len(pts)-1:
  j=len(pts)-1
  while j>i+1 and not allowed.covers(LineString([pts[i],pts[j]])):j-=1
  out.append(pts[j]);i=j
 line=LineString(out);assert allowed.covers(line)
 return line
start=Point(published.coords[0]);start=nearest_points(start,water['Clearwater'])[1]
save('start',[feat(start,label='Departure',kind='hypothetical start / finish')])
routes={};checks=[]
for key,ids in [('a',['a','b','h','i','j']),('b',['a','c','d','e','f','g','h','i','j'])]:
 features=[];cur=start;lake='Clearwater'
 for seq,cid in enumerate(ids+['finish']):
  if cid=='finish':dest=start
  else:
   a,b,p,q=transitions[cid];assert lake==a;dest=p
  line=waterpath(water[lake],cur,dest)
  features.append(feat(line,route=key.upper(),sequence=seq+1,lake=lake,kind='hypothetical paddle',length_m=round(line.length),next_clue=cid))
  checks.append({'route':key,'lake':lake,'length_m':round(line.length),'water_covered_2m_tolerance':water[lake].buffer(2).covers(line)})
  if cid!='finish':cur=q;lake=b
 save('route-'+key,features);routes[key]={'sequence':ids,'paddling_km':round(sum(f['properties']['length_m'] for f in features)/1000,1),'closed_lake_sequence':True}
 print('Route',key,routes[key],flush=True)

# DEM-derived hill shading drawn as ink hachures, with no raster in student map.
ds=gdal.Open(str(S/'lidar-route-8m.tif'));gt=ds.GetGeoTransform();z=ds.ReadAsArray().astype(float)
valid=np.isfinite(z)&(z>250)&(z<900);z[~valid]=0
smooth=gaussian_filter(z,3);dy,dx=np.gradient(smooth,8,8);slope=np.hypot(dx,dy)
near=core.buffer(1100);terrain=[]; water20=W.buffer(20); water45=W.buffer(45)
for r in range(8,z.shape[0]-8,12):
 for c in range(8,z.shape[1]-8,12):
  if not valid[r-5:r+6,c-5:c+6].all() or slope[r,c]<.13:continue
  x=gt[0]+(c+.5)*8;y=gt[3]-(r+.5)*8;p=Point(x,y)
  if not extent.contains(p) or not near.contains(p) or water20.contains(p):continue
  length=min(100,32+slope[r,c]*115);norm=max(slope[r,c],.001)
  vx=dx[r,c]/norm;vy=-dy[r,c]/norm
  g=LineString([(x-vx*length*.5,y-vy*length*.5),(x+vx*length*.5,y+vy*length*.5)])
  if not W.intersects(g):terrain.append(feat(g,slope=round(float(slope[r,c]),2)))
save('hachures',terrain)
# Regional local maxima, spaced apart, close enough to a route lake to be useful.
mx=maximum_filter(smooth,size=101);mn=minimum_filter(smooth,size=151)
rr,cc=np.where(valid&(smooth==mx)&(smooth-mn>35));candidates=[]
for r,c in zip(rr,cc):
 p=Point(gt[0]+(c+.5)*8,gt[3]-(r+.5)*8)
 if extent.contains(p) and near.contains(p) and not water45.contains(p):candidates.append((float(z[r,c]),p,int(r),int(c)))
selected=[]
for elev,p,r,c in sorted(candidates,key=lambda x:-x[0]):
 if all(p.distance(s[1])>1700 for s in selected):selected.append((elev,p,r,c))
 if len(selected)>=12:break
selected.sort(key=lambda x:x[1].x)
high=[];sights=[]
def height(p):
 c=int((p.x-gt[0])/8);r=int((gt[3]-p.y)/8)
 return z[r,c] if 0<=r<z.shape[0] and 0<=c<z.shape[1] and valid[r,c] else None
for i,(elev,p,r,c) in enumerate(selected,1):
 n=min(water,key=lambda n:p.distance(water[n]));w=water[n];view=None
 # Find at least one canoe-eye terrain sightline, not a claim of canopy visibility.
 shore=nearest_points(p,w)[1]
 for f in sorted([f for f in json.load(open(D/'route-b.geojson'))['features'] if f['properties']['lake']==n],key=lambda f:shape(f['geometry']).distance(p)):
  line=shape(f['geometry'])
  for d in np.linspace(0,line.length,60):
   q=line.interpolate(d);base=height(q)
   if base is None or not w.contains(q):continue
   ray=LineString([q,p]);ok=True
   for a in np.linspace(.01,.99,max(30,int(ray.length/16))):
    h=height(ray.interpolate(a,normalized=True))
    if h is None or h>base+.8+(elev-base-.8)*a+2:ok=False;break
   if ok:view=q;break
  if view is not None:break
 hid=f'H{i:02}';lon,lat=inv.transform(p.x,p.y)
 high.append(feat(p,id=hid,label=f'{hid}  {round(elev/5)*5:.0f}m',elevation_m=round(elev,1),longitude=lon,latitude=lat,near_lake=n,terrain_sightline_found=view is not None,visibility='Bare-earth candidate; forest and field recognition unverified',source='MnGeo 8 m resampled DEM'))
 if view is not None:sights.append(feat(LineString([view,p]),id=hid,lake=n,kind='terrain-only sightline; canopy unverified'))
save('high-points',high);save('terrain-sightlines',sights)
# Label points placed at a broad part of each lake, labels may be adjusted in QGIS.
labels=[]
for n,w in water.items():
 p=w.representative_point();labels.append(feat(p,label=n+' Lake',name=n))
save('lake-labels',labels)
meta={'crs':'EPSG:26915','extent':list(extent.bounds),'core_bounds':list(core.bounds),'routes':routes,'transitions':evidence,'high_points':len(high),'terrain_sightlines':len(sights),'hachures':len(terrain),'grid_convergence_deg':Proj(26915).get_factors(-90.2,48.07).meridian_convergence,'transform':t.description,'transform_accuracy_m':t.accuracy}
(D/'map-data.json').write_text(json.dumps(meta,indent=2))
(R/'docs/geometry-validation.json').write_text(json.dumps({'paddle_checks':checks,'route_closure':routes,'transitions':evidence,'terrain_note':'Bare-earth sightlines omit canopy; not field verification','high_points':len(high),'sightlines_found':len(sights)},indent=2))
print('Prepared',len(merged),'clues,',len(high),'high points,',len(terrain),'hachures',flush=True)
