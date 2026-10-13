"""Source-shaped, time-emphasized drawing in explicit local diagram units."""
import json,math,itertools
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from shapely.geometry import Point,Polygon,LineString,mapping,shape,box
from shapely.ops import transform,nearest_points,unary_union,polylabel
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
 duration=max(((r['low_h']+r['high_h'])/2 for r in rows),default=math.sqrt(g.area)/2500);durations[n]=duration
 target=22+20*math.sqrt(duration)
 xmin,ymin,xmax,ymax=g.bounds;cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
 sx=target/(xmax-xmin);sy=max(22,min(42,target*((ymax-ymin)/(xmax-xmin))**.7))/(ymax-ymin)
 xf[n]=(cx,cy,sx,sy)
 local[n]=transform(lambda x,y,z=None:((np.asarray(x)-cx)*sx,(np.asarray(y)-cy)*sy),g)
def lp(n,p):
 cx,cy,sx,sy=xf[n];v=Point((p.x-cx)*sx,(p.y-cy)*sy)
 return nearest_points(v,local[n].boundary)[1]
# Begin in approximately real geographic order, then allocate space by travel effort.
cent=np.array([[water[n].centroid.x,water[n].centroid.y] for n in names]);anchor=(cent-cent.min(axis=0))/np.ptp(cent,axis=0)*np.array([1050.,650.])
# Compress the empty northern gap while retaining the northward ordering.
cap=np.percentile(anchor[:,1],90)+35
anchor[:,1]=np.where(anchor[:,1]>cap,cap+(anchor[:,1]-cap)*.18,anchor[:,1])
links=[]
for c in net['connections']:
 i,j=index[c['from_lake']],index[c['to_lake']];a=np.array(lp(c['from_lake'],geo_lands[(c['from_lake'],c['id'])]).coords[0]);b=np.array(lp(c['to_lake'],geo_lands[(c['to_lake'],c['id'])]).coords[0])
 time=(c['low_h']+c['high_h'])/2
 target=7+18*math.sqrt(time)
 source=geo_lines[c['id']];chord=Point(source.coords[0]).distance(Point(source.coords[-1]));sinuosity=source.length/max(chord,.01)
 target/=min(1.5,sinuosity)
 direction=anchor[j]-anchor[i];direction/=np.linalg.norm(direction)
 links.append((i,j,a,b,target,direction))
width={n:max(local[n].bounds[2]-local[n].bounds[0]+16,42) for n in names}
pair_i,pair_j=np.triu_indices(len(names),1)
reqx=np.array([(width[names[i]]+width[names[j]])/2 for i,j in zip(pair_i,pair_j)])
reqy=np.array([(local[names[i]].bounds[3]-local[names[i]].bounds[1]+local[names[j]].bounds[3]-local[names[j]].bounds[1])/2+20 for i,j in zip(pair_i,pair_j)])
def objective(flat):
 xy=flat.reshape(-1,2);res=list(((xy-anchor)*.3).ravel())
 for i,j,a,b,target,di in links:
  d=xy[j]+b-xy[i]-a;res.append((np.linalg.norm(d)-target)*.35)
  between=xy[j]-xy[i];res.extend([.35*(between[0]*di[1]-between[1]*di[0]),max(0,-np.dot(between,di))])
 delta=np.abs(xy[pair_i]-xy[pair_j]);res.extend((np.maximum(0,np.minimum(reqx-delta[:,0],reqy-delta[:,1]))*3).tolist())
 return res
fit=least_squares(objective,anchor.ravel(),max_nfev=160,ftol=1e-6);xy=fit.x.reshape(-1,2)
# Positive margins for headings/callouts; preserve the solved distances.
xy-=xy.min(axis=0);xy+=np.array([45,35]);pos={n:tuple(xy[index[n]]) for n in names}
# Small manual layout correction keeps the Horseshoe-Gaskin carry clear of Jump.
if 'Jump' in pos:pos['Jump']=(pos['Jump'][0],pos['Jump'][1]-25)
polys={n:translate(local[n],*pos[n]) for n in names}
lakes=[];hatch=[];lake_names=[];times=[];ends=[];leaders=[];label_checks=[]
# A single range refers to the longest modeled crossing on this lake.
# Other landing-to-landing alternatives remain in the instructor register.
from timing import rounded
def compact(r):
 a,b=rounded(r['low_h'],r['high_h']);return f'{a:g}-{b:g}'
for n in names:
 x,y=pos[n];g=polys[n];xmin,ymin,xmax,ymax=g.bounds
 lakes.append(feat(g,name=n,source='simplified DNR footprint',crossing_mid_hours=durations[n],width_rule='22 + 20 sqrt(representative hours)',area_km2=water[n].area/1e6))
 yy=ymin+.5
 while yy<ymax:
  clip=LineString([(xmin-1,yy),(xmax+1,yy)]).intersection(g.buffer(-.25))
  for gg in list(clip.geoms) if hasattr(clip,'geoms') else [clip]:
   if gg.geom_type=='LineString' and not gg.is_empty:hatch.append(feat(gg,lake=n))
  yy+=1.7
 rows=[r for r in net['legs'] if r['mode']=='paddle' and r['from_lake']==n and r['distance_m']>=1]
 r=max(rows,key=lambda r:r['distance_m']) if rows else None
 text=('West Bearskin' if n=='Bearskin' else n)
 c=polylabel(g,tolerance=.5)
 # A name and range travel together. If the name cannot fit inside, the
 # complete block gets a leader to this specific lake in the placement pass.
 lake_names.append(label(c.x,c.y+2.8,text,lake=n))
 if r:times.append(label(c.x,c.y-3.1,compact(r),lake=n,leg_id=r['id'],from_point=r['from_point'],to_point=r['to_point']))
 for eid in ['S']:
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
 suffix='*' if c['approximate'] else '';s=f"{c['id']}{suffix}  {compact(c)}"
 linklabels.append(label(tx,ty,s,connection_id=c['id']))
# Reserve actual footprint and label spaces before placing passage annotations.
obstacles=unary_union(list(polys.values()));paths=unary_union([shape(f['geometry']) for f in carry+rivers]);occupied=[]
def text_box(f,size=8):
 p=f['properties'];lines=p['label'].split('\n');width=max(map(len,lines))*size*.135+2;height=len(lines)*size*.43+1
 return box(p['x']-width/2,p['y']-height/2,p['x']+width/2,p['y']+height/2)
def shifted(f,dx,dy):
 p=f['properties'].copy();p['x']+=dx;p['y']+=dy
 return feat(Point(p['x'],p['y']),**p)
for f in ends:occupied.append(text_box(f,9))
def cost(rects,dx=0,dy=0,own=None):
 u=unary_union(rects);obs=obstacles if own is None else obstacles.difference(polys[own])
 return 60*u.intersection(obs).area+30*sum(u.intersection(g).area for g in occupied)+12*u.intersection(paths).length+.5*math.hypot(dx,dy)
new_names=[];new_times=[]
for nf in sorted(lake_names,key=lambda f:-len(f['properties']['label'])):
 n=nf['properties']['lake'];g=polys[n];tf=next((t for t in times if t['properties']['lake']==n),None);fs=[nf]+([tf] if tf else [])
 # Time alone fits many irregular arms even when the lake name does not.
 if tf:
  c=polylabel(g,tolerance=.2);inside=label(c.x,c.y,tf['properties']['label'],**{k:v for k,v in tf['properties'].items() if k not in ['x','y','label']})
  if g.buffer(-.3).covers(text_box(inside,9)):
   new_times.append(inside);occupied.append(text_box(inside,9));tf=None;fs=[nf]
 rects=[text_box(nf,11)]+([text_box(tf,9)] if tf else [])
 if g.buffer(-.5).covers(unary_union(rects)) and cost(rects,own=n)<1:
  moved=fs;chosen=rects;external=False
 else:
  candidates=[]
  # Prefer just above or below the shoreline, then nearby sides.
  for x,y in [(g.centroid.x,g.bounds[3]+8),(g.centroid.x,g.bounds[1]-8),(g.bounds[0]-15,g.centroid.y),(g.bounds[2]+15,g.centroid.y)]:
   for dx in [0,-10,10,-20,20]:
    for dy in [0,-8,8]:
     sx=x+dx-nf['properties']['x'];sy=y+dy-nf['properties']['y'];m=[shifted(f,sx,sy) for f in fs];rr=[text_box(m[0],11)]+([text_box(m[1],9)] if tf else [])
     candidates.append((cost(rr,sx,sy)+50*max(0,3-g.distance(unary_union(rr))),m,rr))
  _,moved,chosen=min(candidates,key=lambda z:z[0]);external=True
 new_names.append(moved[0]);new_times.extend(moved[1:]);occupied.extend(chosen)
 if external:
  # Use the actual name rectangle, never the blank envelope between lines.
  block=chosen[0];start,end=nearest_points(block,g)
  if start.distance(end)>.1:leaders.append(feat(LineString([start,end]),lake=n,kind='lake-label'))
  if tf:
   start,end=nearest_points(chosen[1],g)
   if start.distance(end)<=.1:start=shape(moved[1]['geometry']);end=nearest_points(start,g)[1]
   if start.distance(end)>.1:leaders.append(feat(LineString([start,end]),lake=n,kind='time-label'))
 label_checks.append({'lake':n,'external':external,'label_x':moved[0]['properties']['x'],'label_y':moved[0]['properties']['y'],'representative_leg':next((t['properties']['leg_id'] for t in new_times if t['properties']['lake']==n),None)})
lake_names=new_names;times=new_times
placed=[]
for f in linklabels:
 c=next(c for c in carry+rivers if c['properties']['id']==f['properties']['connection_id']);g=shape(c['geometry']);pts=np.array(g.coords);direction=pts[-1]-pts[0];direction/=max(np.linalg.norm(direction),.01);normal=np.array([-direction[1],direction[0]]);candidates=[]
 for t in [.5,.35,.65,.2,.8]:
  mid=g.interpolate(t,normalized=True)
  for offset in [4,-4,7,-7,11,-11]:
   x,y=np.array(mid.coords[0])+normal*offset;nf=label(x,y,f['properties']['label'],connection_id=f['properties']['connection_id']);rect=text_box(nf)
   candidates.append((cost([rect])+abs(offset-7)*.2+abs(t-.5)*6,nf,rect))
 _,nf,rect=min(candidates,key=lambda t:t[0]);placed.append(nf);occupied.append(rect)
 start,end=nearest_points(rect,g)
 if start.distance(end)>2:leaders.append(feat(LineString([start,end]),connection_id=f['properties']['connection_id'],kind='carry-label'))
linklabels=placed
hills=[];hilllabels=[]
# Only researched landmarks enter the student diagram. Generic DEM summits stay
# in the geographic evidence project, hidden by default.
from pyproj.transformer import TransformerGroup
ll_to_utm=next(t for t in TransformerGroup(4326,26915,always_xy=True).transformers if '(1)' in t.description)
research=R/'sources/landmarks-research.json'
if research.exists():
 records=json.load(open(research));records=records.get('landmarks',[]) if isinstance(records,dict) else records
 for p in records:
  n=p['lake']
  if n not in polys:continue
  g=polys[n];gx,gy=ll_to_utm.transform(p['lon'],p['lat']);cx,cy,sx,sy=xf[n];shore=lp(n,Point(gx,gy));x0=pos[n][0]+shore.x;y0=pos[n][1]+shore.y;direction=np.array([x0-g.centroid.x,y0-g.centroid.y]);direction/=max(np.linalg.norm(direction),.1);x0+=direction[0]*16;y0+=direction[1]*16;candidates=[]
  caption=('Rose Falls' if p['id']=='rose-falls' else p['name'])+(' (walk)' if p['visibility']!='water-visible' else '')
  for dx in [0,-16,16,-32,32]:
   for dy in [0,12,24,-45,-57]:
    x,y=x0+dx,y0+dy;nf=label(x,y-6,caption,source_id=p['id'],near_lake=n,visibility=p['visibility']);rr=[box(x-5,y-3,x+6,y+4),text_box(nf,9)];candidates.append((cost(rr,dx,dy),x,y,nf,rr))
  _,x,y,nf,rr=min(candidates,key=lambda t:t[0]);occupied.extend(rr)
  if 'fall' in p['kind'].lower() or 'fall' in p['name'].lower():
   for dy in [-2,0,2]:hills.append(feat(LineString([(x-4,y+dy),(x,y+dy),(x+1,y+dy-3),(x+4,y+dy-3)]),id=p['id']))
  else:
   hills.append(feat(LineString([(x-4,y-3),(x,y+3),(x+5,y-3)]),id=p['id']))
   for i in range(7):
    dx=-3+i;top=y+3-abs(dx)*1.2;hills.append(feat(LineString([(x+dx,top),(x+dx+1.4,top-3)]),id=p['id']))
  hilllabels.append(nf)
  a,b=nearest_points(unary_union(rr).envelope,g);leaders.append(feat(LineString([a,b]),lake=n,landmark_id=p['id'],kind='landmark-association'))
for n,f in [('lakes',lakes),('hatching',hatch),('names',lake_names),('paddle-times',times),('endpoints',ends),('carries',carry),('rivers',rivers),('carry-times',linklabels),('hills',hills),('hill-labels',hilllabels),('leaders',leaders)]:save(n,f)
all_bounds=list(polys.values())+occupied
bounds=[min(g.bounds[0] for g in all_bounds)-15,min(g.bounds[1] for g in all_bounds)-15,max(g.bounds[2] for g in all_bounds)+15,max(g.bounds[3] for g in all_bounds)+15]
(D/'diagram-positions.json').write_text(json.dumps(pos,indent=2));(D/'diagram-layout.json').write_text(json.dumps({'bounds':bounds,'method':'source footprints + sqrt(time) spacing stress with geographic order and legibility constraints','connection_checks':geometry_checks,'label_checks':label_checks},indent=2))
print('Organic schematic:',len(lakes),'lakes;',len(times),'crossings; bounds',bounds,'size',bounds[2]-bounds[0],bounds[3]-bounds[1],flush=True)
