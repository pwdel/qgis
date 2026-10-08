"""Canoe-eye terrain horizons: angular perspective, equal horizontal/vertical scale."""
import json,math
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from osgeo import gdal,osr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'sources';D=ROOT/'derived';O=D/'portage-views';O.mkdir(exist_ok=True)
ds=gdal.Open(str(D/'lidar-valid-8m.tif'));z=ds.ReadAsArray().astype(float);z[z<100]=np.nan;gt=ds.GetGeoTransform()
g=osr.SpatialReference();g.ImportFromEPSG(4326);g.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
u=osr.SpatialReference();u.ImportFromEPSG(26915);u.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER);tx=osr.CoordinateTransformation(g,u)
def sample(x,y):
 return map_coordinates(z,[(gt[3]-y)/8-.5,(x-gt[0])/8-.5],order=1,mode='constant',cval=np.nan)
records=[];views=[];sightlines=[]
for f in json.loads((S/'portage-landings.geojson').read_text())['features']:
 p=f['properties'];x,y,_=tx.TransformPoint(p['view_lon'],p['view_lat']);lx,ly,_=tx.TransformPoint(*f['geometry']['coordinates']);angle=math.atan2(lx-x,ly-y)
 # Water surface estimate near camera, not hill elevation at landing.
 nearby=sample(x+np.array([0,8,-8,0,0]),y+np.array([0,0,0,8,-8]));water=float(np.nanmedian(nearby));eye=water+.8
 if not np.isfinite(eye):raise ValueError(f"No camera terrain data {p['id']}")
 az=np.linspace(-30,30,721);dist=np.arange(24,3001,8);theta=angle+np.deg2rad(az)
 vals=sample(x+np.sin(theta[:,None])*dist[None,:],y+np.cos(theta[:,None])*dist[None,:])
 elevations=np.degrees(np.arctan2(vals-eye,dist[None,:]));valid=np.isfinite(elevations)
 horizon=np.max(np.where(valid,elevations,-90),axis=1);horizon[horizon==-90]=np.nan
 # Mark any ray with a missing cell after the target distance; its skyline may be incomplete.
 missing=np.any(~valid[:,dist>p['view_distance_m']],axis=1)
 fig=plt.figure(figsize=(3.2,3.2),facecolor='#f6f3e9');ax=fig.add_axes([0.05,.08,.9,.9]);ax.set_facecolor('#e5eff0')
 ax.fill_between(az,-30,0,color='#b5d2d8',linewidth=0)
 ax.fill_between(az,0,horizon,color='#738677',linewidth=0);ax.plot(az,horizon,color='#304d43',lw=.9)
 # Equal angular scaling keeps the terrain unexaggerated.
 ax.set_xlim(-30,30);ax.set_ylim(-30,30);ax.set_aspect('equal');ax.set_xticks([-30,-15,0,15,30]);ax.set_xticklabels(['-30°','-15°','0°','+15°','+30°'],fontsize=6,color='#304d43');ax.set_yticks([])
 for spine in ax.spines.values():spine.set_color('#b1bab0')
 ax.axvline(0,color='#a7512b',lw=.7,ls='--',alpha=.75)
 h=float(horizon[len(az)//2]);ax.annotate('candidate bearing',xy=(0,max(0,h)),xytext=(0,18),ha='center',fontsize=7,color='#8c4327',arrowprops={'arrowstyle':'-|>','color':'#8c4327','lw':.8})
 ax.text(-27,-22,f"{p['view_distance_m']:.0f} m offshore\n{p['view_bearing_deg']:.0f}° true  |  eye +0.8 m",fontsize=7,color='#234c57',va='center')
 if missing.any():
  ax.plot(az[missing],np.full(missing.sum(),-28),'.',color='#b77642',ms=.6)
  ax.text(0,27,'Partial horizon coverage',fontsize=6.5,color='#8c4327',ha='center')
 fig.savefig(O/(p['id']+'.png'),dpi=240);plt.close(fig)
 r={'id':p['id'],'water_elevation_estimate_m':water,'eye_height_m':.8,'horizontal_fov_deg':60,'vertical_fov_deg':60,'ray_distance_max_m':3000,'ray_step_m':8,'azimuth_step_deg':float(az[1]-az[0]),'missing_ray_fraction':float(missing.mean()),'valid_sample_fraction':float(valid.mean()),'view_lon':p['view_lon'],'view_lat':p['view_lat'],'target_lon':f['geometry']['coordinates'][0],'target_lat':f['geometry']['coordinates'][1],'bearing_true_deg':p['view_bearing_deg'],'distance_m':p['view_distance_m'],'confidence':p['confidence'],'canopy':False,'vertical_exaggeration':1,'image':'derived/portage-views/'+p['id']+'.png'};records.append(r)
 views.append({'type':'Feature','geometry':{'type':'Point','coordinates':[p['view_lon'],p['view_lat']]},'properties':{'id':p['id'],'label':p['id']+' view','bearing':p['view_bearing_deg']}})
 sightlines.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[[p['view_lon'],p['view_lat']],f['geometry']['coordinates']]},'properties':{'id':p['id']}})
 print(p['id'],'water',round(water,1),'missing rays',round(r['missing_ray_fraction'],3),flush=True)
(D/'portage-views.json').write_text(json.dumps(records,indent=2))
for n,fs in [('viewpoints',views),('sightlines',sightlines)]:
 (D/(n+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','features':fs},indent=2))
