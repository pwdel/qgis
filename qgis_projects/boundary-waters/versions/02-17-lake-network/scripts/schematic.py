"""Local diagram coordinates only. Geographic measurements live in separate files."""
import json,math
from pathlib import Path
from shapely.geometry import Point,Polygon,LineString,mapping,shape
R=Path(__file__).resolve().parents[1];D=R/'data';net=json.load(open(D/'network.json'))
pos={'Rose':(26,180),'Rove':(100,180),'Watap':(177,184),'Mountain':(245,180),'Clearwater':(50,122),'West Pike':(184,124),'East Pike':(280,130),'John':(373,132),'Caribou':(85,78),'Little Caribou':(154,73),'Pine':(242,78),'McFarland':(325,71),'Little John':(380,91),'Deer':(25,53),'Canoe':(224,28),'Alder':(157,27),'Crystal':(292,27)}
areas={f['properties']['name']:f['properties']['area_km2'] for f in json.load(open(D/'geographic-lakes.geojson'))['features']}
def feat(g,**p):return {'type':'Feature','geometry':mapping(g),'properties':p}
def label(x,y,s,**p):return feat(Point(x,y),x=x,y=y,label=s,**p)
def save(n,fs):(D/('schematic-'+n+'.json')).write_text(json.dumps({'coordinate_system':'LOCAL SCHEMATIC UNITS - internal drawing records, not GeoJSON','features':fs}))
lakes=[];hatch=[];names=[];times=[];ends=[];polys={}
for i,(n,(x,y)) in enumerate(pos.items()):
 area=areas[n];rx=14 if area>3 else 10 if area>1 else 7;ry=5.4 if area>3 else 4.5 if area>1 else 3.7
 pts=[]
 for j in range(97):
  a=j*2*math.pi/96;r=1+.10*math.sin(3*a+i)+.055*math.cos(7*a-i)
  pts.append((x+rx*r*math.cos(a),y+ry*r*math.sin(a)))
 g=Polygon(pts);polys[n]=g;lakes.append(feat(g,name=n,area_km2=area,size_class='large' if area>3 else 'medium' if area>1 else 'small'))
 yy=y-ry
 while yy<y+ry:
  clip=LineString([(x-rx*1.2,yy),(x+rx*1.2,yy)]).intersection(g.buffer(-.35))
  if not clip.is_empty:
   for gg in list(clip.geoms) if hasattr(clip,'geoms') else [clip]:
    if gg.geom_type=='LineString':hatch.append(feat(gg,lake=n))
  yy+=.85
 names.append(label(x,y+9,n+' Lake'))
 rows=[r for r in net['legs'] if r['mode']=='paddle' and r['from_lake']==n]
 for j,r in enumerate(rows):
  col=j//3 if len(rows)>3 else 0;row=j%3 if len(rows)>3 else j
  tx=x+(-16 if col==0 else 16) if len(rows)>3 else x
  ty=y-9-row*3.9
  if n=='Clearwater':tx=x+(-32 if col==0 else -5);ty=y-14-row*3.9
  display='same landing' if r['distance_m']<1 else r['display']
  times.append(label(tx,ty,f"{r['from_point']}-{r['to_point']}  {display}",leg_id=r['id']))
 if n=='Clearwater':ends.append(label(x-20,y,'S'))
 elif len(rows)==1 and 'T' in [rows[0]['from_point'],rows[0]['to_point']]:ends.append(label(x-11,y,'T'))
carry=[];rivers=[];linklabels=[]
# Manual offset controls retain straight links while making their lettering readable.
offsets={'a':(0,5),'b':(15,0),'c':(0,5),'d':(0,5),'e':(-16,0),'f':(8,-4),'g':(0,-6),'h':(0,6),'i':(0,5),'j':(16,0),'k':(0,7),'l':(0,-8),'m':(0,7),'n':(0,7),'o':(-5,1),'p':(15,0),'q':(0,6),'r':(0,6)}
for c in net['connections']:
 a=Point(pos[c['from_lake']]);b=Point(pos[c['to_lake']]);line=LineString([a,b]);g=line.difference(polys[c['from_lake']].union(polys[c['to_lake']]))
 assert g.geom_type=='LineString'
 (carry if c['mode']=='carry' else rivers).append(feat(g,**c))
 x,y=line.interpolate(.5,normalized=True).coords[0];dx,dy=offsets[c['id']]
 suffix='*' if c['approximate'] else ''
 s=f"{c['id']}{suffix}  ~{c['rod_count']} rd\n{c['display']}" if c['mode']=='carry' else f"{c['id']}  {c['mode']}\n{c['display']}"
 linklabels.append(label(x+dx,y+dy,s,connection_id=c['id']))
# Draw supported existing terrain candidates schematically near their associated lake.
hills=[];hilllabels=[]
source={f['properties']['id']:f for f in json.load(open(D/'geographic-high-points.geojson'))['features']}
for id,x,y in [('H01',22,146),('H04',113,98),('H08',185,153),('H10',282,51),('H12',310,157)]:
 f=source[id];p=f['properties'];e=5*round(p['elevation_m']/5)
 hills.append(feat(LineString([(x-5,y-3),(x,y+4),(x+6,y-3)]),id=id))
 for i in range(11):
  dx=-5+i;top=y+4-abs(dx)*1.25
  hills.append(feat(LineString([(x+dx,top),(x+dx+2,top-3.5)]),id=id))
 hilllabels.append(label(x,y-7,f'{id}  ~{e} m',source_id=id,near_lake=p['near_lake'],visibility=p['visibility']))
for n,f in [('lakes',lakes),('hatching',hatch),('names',names),('paddle-times',times),('endpoints',ends),('carries',carry),('rivers',rivers),('carry-times',linklabels),('hills',hills),('hill-labels',hilllabels)]:save(n,f)
(D/'diagram-positions.json').write_text(json.dumps(pos,indent=2))
print('Schematic:',len(lakes),'lake symbols;',len(times),'crossing labels')
