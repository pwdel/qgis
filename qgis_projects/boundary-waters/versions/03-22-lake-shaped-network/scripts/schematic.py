"""Source-shaped, time-emphasized drawing in explicit local diagram units."""
import json,math,itertools
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from shapely.geometry import Point,Polygon,LineString,mapping,shape,box
from shapely.ops import transform,nearest_points,unary_union
from shapely.affinity import translate
R=Path(__file__).resolve().parents[1];D=R/'data';net=json.load(open(D/'network.json'))
water={f['properties']['name']:shape(f['geometry']) for f in json.load(open(D/'geographic-lakes.geojson'))['features']}
geo_lands={(f['properties']['lake'],f['properties']['point_id']):shape(f['geometry']) for f in json.load(open(D/'geographic-landings.geojson'))['features']}
geo_lines={f['properties']['id']:shape(f['geometry']) for f in json.load(open(D/'geographic-modeled-connections.geojson'))['features']}
names=net['lakes'];index={n:i for i,n in enumerate(names)}
def feat(g,**p):return {'type':'Feature','geometry':mapping(g),'properties':p}
def label(x,y,s,**p):return feat(Point(x,y),x=x,y=y,label=s,**p)
def save(n,fs):(D/('schematic-'+n+'.json')).write_text(json.dumps({'coordinate_system':'LOCAL SCHEMATIC UNITS - internal drawing records, not GeoJSON','features':fs}))
# Preserve large-scale arms and orientation; omit islands and minor shoreline detail.
local={};xf={};durations={}
for n in names:
 g=water[n].buffer(3).buffer(-3)
 if g.geom_type=='MultiPolygon':g=max(g.geoms,key=lambda p:p.area)
 span=max(g.bounds[2]-g.bounds[0],g.bounds[3]-g.bounds[1]);g=Polygon(g.exterior).simplify(span*.009,preserve_topology=True)
 rows=[r for r in net['legs'] if r['mode']=='paddle' and r['from_lake']==n]
 duration=max((r['low_h']+r['high_h'])/2 for r in rows);durations[n]=duration
 target=18+18*math.sqrt(duration)
 xmin,ymin,xmax,ymax=g.bounds;cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
 sx=target/(xmax-xmin);sy=max(8,min(19,target*((ymax-ymin)/(xmax-xmin))**.7))/(ymax-ymin)
 xf[n]=(cx,cy,sx,sy)
 local[n]=transform(lambda x,y,z=None:((np.asarray(x)-cx)*sx,(np.asarray(y)-cy)*sy),g)
def lp(n,p):
 cx,cy,sx,sy=xf[n];v=Point((p.x-cx)*sx,(p.y-cy)*sy)
 return nearest_points(v,local[n].boundary)[1]
# Begin in approximately real geographic order, then allocate space by travel effort.
cent=np.array([[water[n].centroid.x,water[n].centroid.y] for n in names]);anchor=(cent-cent.min(axis=0))/np.ptp(cent,axis=0)*np.array([470.,155.])
links=[]
for c in net['connections']:
 i,j=index[c['from_lake']],index[c['to_lake']];a=np.array(lp(c['from_lake'],geo_lands[(c['from_lake'],c['id'])]).coords[0]);b=np.array(lp(c['to_lake'],geo_lands[(c['to_lake'],c['id'])]).coords[0])
 time=(c['low_h']+c['high_h'])/2
 target=7+18*math.sqrt(time)
 source=geo_lines[c['id']];chord=Point(source.coords[0]).distance(Point(source.coords[-1]));sinuosity=source.length/max(chord,.01)
 target/=min(1.5,sinuosity)
 direction=anchor[j]-anchor[i];direction/=np.linalg.norm(direction)
 links.append((i,j,a,b,target,direction))
width={n:max(local[n].bounds[2]-local[n].bounds[0]+9,57 if len([r for r in net['legs'] if r['mode']=='paddle' and r['from_lake']==n])>3 else 40) for n in names}
def objective(flat):
 xy=flat.reshape(-1,2);res=list(((xy-anchor)*.085).ravel())
 for i,j,a,b,target,di in links:
  d=xy[j]+b-xy[i]-a;res.append((np.linalg.norm(d)-target)*1.1)
  between=xy[j]-xy[i];res.extend([.35*(between[0]*di[1]-between[1]*di[0]),max(0,-np.dot(between,di))])
 for i,j in itertools.combinations(range(len(names)),2):
  delta=np.abs(xy[i]-xy[j]);reqx=(width[names[i]]+width[names[j]])/2;reqy=40
  res.append(max(0,min(reqx-delta[0],reqy-delta[1]))*2)
 return res
fit=least_squares(objective,anchor.ravel(),max_nfev=450,ftol=1e-6);xy=fit.x.reshape(-1,2)
# Positive margins for headings/callouts; preserve the solved distances.
xy-=xy.min(axis=0);xy+=np.array([45,35]);pos={n:tuple(xy[index[n]]) for n in names}
polys={n:translate(local[n],*pos[n]) for n in names}
lakes=[];hatch=[];lake_names=[];times=[];ends=[]
for n in names:
 x,y=pos[n];g=polys[n];xmin,ymin,xmax,ymax=g.bounds
 lakes.append(feat(g,name=n,source='simplified DNR footprint',crossing_mid_hours=durations[n],width_rule='18 + 18 sqrt(representative hours)',area_km2=water[n].area/1e6))
 yy=ymin+.5
 while yy<ymax:
  clip=LineString([(xmin-1,yy),(xmax+1,yy)]).intersection(g.buffer(-.25))
  for gg in list(clip.geoms) if hasattr(clip,'geoms') else [clip]:
   if gg.geom_type=='LineString' and not gg.is_empty:hatch.append(feat(gg,lake=n))
  yy+=.8
 lake_names.append(label(x,ymax+5,('West Bearskin' if n=='Bearskin' else n)+' Lake'))
 rows=[r for r in net['legs'] if r['mode']=='paddle' and r['from_lake']==n]
 for j,r in enumerate(rows):
  col=j//3 if len(rows)>3 else 0;row=j%3 if len(rows)>3 else j
  tx=x+(-17 if col==0 else 17) if len(rows)>3 else x;ty=ymin-5-row*3.9
  display='same landing' if r['distance_m']<1 else r['display']
  times.append(label(tx,ty,f"{r['from_point']}-{r['to_point']}  {display}",leg_id=r['id']))
 for eid in ['S','T']:
  if (n,eid) in geo_lands:ends.append(label(xmin-3,y,eid))
carry=[];rivers=[];linklabels=[];diagram_landings=[];geometry_checks=[]
for c in net['connections']:
 na,nb=c['from_lake'],c['to_lake'];pa=lp(na,geo_lands[(na,c['id'])]);pb=lp(nb,geo_lands[(nb,c['id'])]);a=np.array(pa.coords[0])+np.array(pos[na]);b=np.array(pb.coords[0])+np.array(pos[nb]);d=b-a;L=np.linalg.norm(d);unit=d/max(L,.01);normal=np.array([-unit[1],unit[0]])
 src=geo_lines[c['id']].simplify(12);coords=np.array(src.coords);delta=coords[-1]-coords[0];length=np.linalg.norm(delta);u=delta/max(length,.01);v=np.array([-u[1],u[0]]);offset=coords-coords[0];along=offset@u/max(length,.01);across=offset@v
 # Echo recorded turns, limiting enlargement of wiggles on short carries.
 perp=min(L/max(length,.01),min(9,L*.28)/max(np.abs(across).max(),.01))
 mapped=a+along[:,None]*d+across[:,None]*perp*normal;g=LineString(mapped)
 cut=g.difference(polys[na].union(polys[nb]))
 if cut.geom_type=='MultiLineString':cut=max(cut.geoms,key=lambda part:part.length)
 if cut.geom_type=='LineString' and cut.length>0:
  g=cut
  if Point(g.coords[0]).distance(Point(a))>Point(g.coords[-1]).distance(Point(a)):g=LineString(list(g.coords)[::-1])
 a=np.array(g.coords[0]);b=np.array(g.coords[-1])
 (carry if c['mode']=='carry' else rivers).append(feat(g,**c,diagram_length=g.length,shape_source='geographic-modeled-connections',spacing_target=7+18*math.sqrt((c['low_h']+c['high_h'])/2)))
 for n,p in [(na,a),(nb,b)]:diagram_landings.append(feat(Point(p),lake=n,id=c['id']))
 geometry_checks.append({'id':c['id'],'source_vertices':len(coords),'diagram_vertices':len(g.coords),'start_boundary_gap':Point(a).distance(polys[na].boundary),'end_boundary_gap':Point(b).distance(polys[nb].boundary)})
 mid=g.interpolate(.5,normalized=True);tx,ty=mid.x+normal[0]*7,mid.y+normal[1]*7
 suffix='*' if c['approximate'] else '';s=f"{c['id']}{suffix}  ~{c['rod_count']} rd\n{c['display']}" if c['mode']=='carry' else f"{c['id']}  {c['mode']}\n{c['display']}"
 linklabels.append(label(tx,ty,s,connection_id=c['id']))
# Reserve actual footprint and label spaces before placing passage annotations.
obstacles=unary_union(list(polys.values()));paths=unary_union([shape(f['geometry']) for f in carry+rivers]);occupied=[]
def text_box(f,size=8):
 p=f['properties'];lines=p['label'].split('\n');width=max(map(len,lines))*size*.135+2;height=len(lines)*size*.43+1
 return box(p['x']-width/2,p['y']-height/2,p['x']+width/2,p['y']+height/2)
def shifted(f,dx,dy):
 p=f['properties'].copy();p['x']+=dx;p['y']+=dy
 return feat(Point(p['x'],p['y']),**p)
for f in lake_names:occupied.append(text_box(f,12))
for f in ends:occupied.append(text_box(f,9))
def cost(rects,dx=0,dy=0):
 u=unary_union(rects)
 return 60*u.intersection(obstacles).area+15*sum(u.intersection(g).area for g in occupied)+12*u.intersection(paths).length+.5*math.hypot(dx,dy)
# Move crossing groups together, retaining an obvious association with each lake.
placed=[]
for n in names:
 ids={r['id'] for r in net['legs'] if r['mode']=='paddle' and r['from_lake']==n};fs=[f for f in times if f['properties']['leg_id'] in ids]
 candidates=[]
 for dx in [0,-6,6,-12,12,-18,18]:
  for dy in [0,-5,5,-10,10,-16,16]:
   moved=[shifted(f,dx,dy) for f in fs];rects=[text_box(f) for f in moved];candidates.append((cost(rects,dx,dy),moved,rects))
 _,moved,rects=min(candidates,key=lambda t:t[0]);placed.extend(moved);occupied.extend(rects)
times=placed
placed=[]
for f in linklabels:
 c=next(c for c in carry+rivers if c['properties']['id']==f['properties']['connection_id']);g=shape(c['geometry']);pts=np.array(g.coords);direction=pts[-1]-pts[0];direction/=max(np.linalg.norm(direction),.01);normal=np.array([-direction[1],direction[0]]);candidates=[]
 for t in [.5,.35,.65,.2,.8]:
  mid=g.interpolate(t,normalized=True)
  for offset in [7,-7,11,-11,15,-15]:
   x,y=np.array(mid.coords[0])+normal*offset;nf=label(x,y,f['properties']['label'],connection_id=f['properties']['connection_id']);rect=text_box(nf)
   candidates.append((cost([rect])+abs(offset-7)*.2+abs(t-.5)*6,nf,rect))
 _,nf,rect=min(candidates,key=lambda t:t[0]);placed.append(nf);occupied.append(rect)
linklabels=placed
hills=[];hilllabels=[];source={f['properties']['id']:f for f in json.load(open(D/'geographic-high-points.geojson'))['features']}
for id in ['H01','H04','H08','H10','H12']:
 f=source[id];p=f['properties'];n=p['near_lake'];gp=shape(f['geometry']);cx,cy,sx,sy=xf[n];x0=pos[n][0]+(gp.x-cx)*sx;y0=polys[n].bounds[3]+17 if gp.y>cy else polys[n].bounds[1]-26;e=5*round(p['elevation_m']/5);candidates=[]
 for dx in [0,-7,7,-14,14,-21,21]:
  for dy in [0,-7,7,-14,14]:
   x,y=x0+dx,y0+dy;nf=label(x,y-6,f'{id}  ~{e} m',source_id=id,near_lake=n,visibility=p['visibility']);rects=[box(x-5,y-3,x+6,y+4),text_box(nf)];candidates.append((cost(rects,dx,dy),x,y,nf,rects))
 _,x,y,nf,rects=min(candidates,key=lambda t:t[0]);occupied.extend(rects)
 hills.append(feat(LineString([(x-4,y-3),(x,y+3),(x+5,y-3)]),id=id))
 for i in range(9):
  dx=-4+i;top=y+3-abs(dx)*1.2;hills.append(feat(LineString([(x+dx,top),(x+dx+1.6,top-3)]),id=id))
 hilllabels.append(nf)
for n,f in [('lakes',lakes),('hatching',hatch),('names',lake_names),('paddle-times',times),('endpoints',ends),('carries',carry),('rivers',rivers),('carry-times',linklabels),('hills',hills),('hill-labels',hilllabels)]:save(n,f)
bounds=[min(g.bounds[0] for g in polys.values())-20,min(g.bounds[1] for g in polys.values())-35,max(g.bounds[2] for g in polys.values())+20,max(g.bounds[3] for g in polys.values())+30]
(D/'diagram-positions.json').write_text(json.dumps(pos,indent=2));(D/'diagram-layout.json').write_text(json.dumps({'bounds':bounds,'method':'source footprints + sqrt(time) spacing stress with geographic order and legibility constraints','connection_checks':geometry_checks},indent=2))
print('Organic schematic:',len(lakes),'lakes;',len(times),'crossings; bounds',bounds,'size',bounds[2]-bounds[0],bounds[3]-bounds[1],flush=True)
