"""Derive map candidates, not field-verified landings. Requires shapely. Coordinates WGS84."""
import json,math,xml.etree.ElementTree as ET
from pathlib import Path
from shapely.geometry import shape,LineString,Point,mapping
from shapely.ops import unary_union,nearest_points
from shapely.affinity import affine_transform
P=Path(__file__).parent;sx=74400.;sy=111200.
proj=lambda g:affine_transform(g,[sx,0,0,sy,90.3*sx,-48.08*sy])
ll=lambda p:[round(p.x/sx-90.3,8),round(p.y/sy+48.08,8)]
water={}
for f in json.load(open(P/'hydrography.geojson'))['features']:
 n=f['properties'].get('pw_basin_name');n=n.replace(' (Canada)','') if n else '?';water.setdefault(n,[]).append(proj(shape(f['geometry'])))
water={n:unary_union(v) for n,v in water.items()}
ns={'k':'http://www.opengis.net/kml/2.2'};routes={}
for pm in ET.parse(P/'2008-boundary-waters.kml').findall('.//k:Placemark',ns):
 c=pm.find('k:LineString/k:coordinates',ns)
 if c is not None:routes[pm.find('k:name',ns).text]=proj(LineString([[float(v) for v in x.split(',')[:2]] for x in c.text.split()]))
trails=json.load(open(P/'portage-usfs-query.json'))['features']
spec=[(77,'Hungry Jack','Moss',True,'Day 1'),(26,'Moss','Duncan',False,'Day 1'),(48,'Duncan','Rose',True,'Day 1'),(46,'Rose','Rove',False,'Day 2'),(42,'Watap','Mountain',False,'Day 2'),(33,'Mountain','Clearwater',False,'Day 3'),(39,'Clearwater','West Pike',False,'Day 3'),(34,'West Pike','East Pike',False,'Day 3'),(34,'East Pike','Pine via West Pike junction',True,'Fourth Day'),(None,'Pine','Little Caribou',False,'Fourth Day'),(None,'Little Caribou','Caribou',False,'Fourth Day'),(28,'Caribou','Clearwater',True,'Fourth Day')]
landings=[];selected={}
for num,(ix,fr,to,rev,day) in enumerate(spec,1):
 r=routes[day];w=water[fr];note='USFS trail endpoint snapped to nearest shore of named approach lake; route coordinate order establishes direction.'
 if ix is not None:
  f=trails[ix];c=f['geometry']['paths'][0];raw=proj(Point(c[-1] if rev else c[0]));landing=nearest_points(raw,w.boundary)[1];offset=raw.distance(landing);oid=f['attributes']['objectid'];method='USFS endpoint + DNR shoreline';confidence='medium' if offset<50 else 'low';selected[ix]=f
 else:
  # Known historical line exits these lakes in this approximate route interval.
  lo,hi=(11000,11600) if fr=='Pine' else (12580,13000)
  cross=r.intersection(w.boundary);pts=list(cross.geoms) if hasattr(cross,'geoms') else [cross]
  choices=[p for p in pts if p.geom_type=='Point' and lo<r.project(p)<hi]
  landing=min(choices,key=lambda p:r.project(p));raw=landing;offset=None;oid=None;method='historical route crossing DNR shoreline only';confidence='low';note='No corresponding trail in complete USFS query. Approximate historical route/shoreline candidate; trail and landing unresolved.'
 if num==1:note+=' USFS endpoint is about 383m inland from mapped Hungry Jack shore; this substantial gap lowers confidence and may reflect source mismatch or incomplete trail geometry.'
 if num==9:selected[24]=trails[24];note+=' East Pike-West Pike and West Pike-Pine trail features meet at a junction near West Pike shore. KML turns south there; no separate West Pike water approach is depicted.'
 s=r.project(landing);up=r.interpolate(max(0,s-400));angle=math.atan2(up.y-landing.y,up.x-landing.x)
 choices=[]
 # Search actual incoming route first, then fan around its incoming bearing.
 for back in range(150,1301,25):
  v=r.interpolate(max(0,s-back));dist=v.distance(landing)
  if w.contains(v) and w.buffer(2).covers(LineString([v,landing])):choices.append((abs(dist-400),v,'incoming historical route'))
 for dist in [400,350,300,250,200,150,100,75,50,25]:
  for a in range(-180,181,1):
   theta=angle+math.radians(a);v=Point(landing.x+dist*math.cos(theta),landing.y+dist*math.sin(theta))
   if w.contains(v) and w.buffer(2).covers(LineString([v,landing])):choices.append((abs(dist-400)+abs(a)*1.5+20,v,'adjusted within approach lake'))
 if choices:_,view,vm=min(choices,key=lambda x:x[0])
 else:view=nearest_points(up,w)[1];vm='fallback nearest water; sightline not validated'
 bearing=(math.degrees(math.atan2(landing.x-view.x,landing.y-view.y))+360)%360
 props={'id':f'P{num:02}','label':fr+' → '+to,'from_lake':fr,'to_lake':to,'day':day,'source':'USFS National Forest System Trails; Minnesota DNR hydrography; historical user KML','usfs_objectid':oid,'evidence_method':method,'confidence':confidence,'field_verified':False,'landing_lon':ll(landing)[0],'landing_lat':ll(landing)[1],'raw_endpoint_lon':ll(raw)[0],'raw_endpoint_lat':ll(raw)[1],'shore_snap_distance_m':round(offset,1) if offset is not None else None,'view_lon':ll(view)[0],'view_lat':ll(view)[1],'view_distance_m':round(view.distance(landing),1),'view_bearing_deg':round(bearing,1),'view_method':vm,'view_in_named_lake':w.contains(view),'sightline_in_water_2m_tolerance':w.buffer(2).covers(LineString([view,landing])),'notes':note}
 landings.append({'type':'Feature','properties':props,'geometry':{'type':'Point','coordinates':ll(landing)}})
 print(props['id'],props['label'],confidence,'snap',props['shore_snap_distance_m'],'view',props['view_distance_m'],vm)
trailout=[]
for ix,f in selected.items():
 trailout.append({'type':'Feature','properties':f['attributes']|{'source':'USFS National Forest System Trails','field_verified':False},'geometry':{'type':'MultiLineString','coordinates':f['geometry']['paths']}})
for filename,features in [('portages.geojson',trailout),('portage-landings.geojson',landings)]:
 (P/filename).write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2)+'\n')
