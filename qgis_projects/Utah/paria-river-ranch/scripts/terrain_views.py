"""Two explanatory views of the native terrain crop; no safety classification."""
import json
from pathlib import Path
import numpy as np
from osgeo import gdal,ogr,osr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

ROOT=Path(__file__).resolve().parents[1]
ds=gdal.Open(str(ROOT/'sources'/'thunder-native-1m.tif'))
z=ds.ReadAsArray().astype(float);gt=ds.GetGeoTransform();nd=ds.GetRasterBand(1).GetNoDataValue()
z[z==nd]=np.nan
step=8;view=z[::step,::step]
x=(np.arange(view.shape[1])*step+.5)*gt[1]
y=(np.arange(view.shape[0])*step+.5)*-gt[5]
X,Y=np.meshgrid(x,y)
colors=LightSource(azdeg=315,altdeg=45).shade(np.nan_to_num(view,nan=np.nanmedian(view)),cmap=plt.get_cmap('gist_earth'),vert_exag=1,dx=8,dy=8,blend_mode='soft')

src=osr.SpatialReference();src.ImportFromEPSG(4326);src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
dst=osr.SpatialReference();dst.ImportFromEPSG(26912);dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
tx=osr.CoordinateTransformation(src,dst)
data=json.loads((ROOT/'sources'/'usfs-trails.geojson').read_text())
f=next(f for f in data['features'] if f['properties']['trail_name']=='THUNDER MOUNTAIN TRAIL')
g=ogr.CreateGeometryFromJson(json.dumps(f['geometry']));g.Transform(tx)
lines=[g] if g.GetGeometryType()==ogr.wkbLineString else [g.GetGeometryRef(i) for i in range(g.GetGeometryCount())]
routes=[]
for line in lines:
    xx=np.array([p[0]-gt[0] for p in line.GetPoints()]);yy=np.array([gt[3]-p[1] for p in line.GetPoints()])
    zi=np.full(len(xx),np.nan);valid=(xx>=0)&(xx<z.shape[1])&(yy>=0)&(yy<z.shape[0])
    zi[valid]=z[yy[valid].astype(int),xx[valid].astype(int)]+3
    routes.append((xx,yy,zi))
fig=plt.figure(figsize=(16,8),facecolor='#fcfaf4')
for j,angle in enumerate([-55,125],1):
    ax=fig.add_subplot(1,2,j,projection='3d',facecolor='#fcfaf4')
    ax.plot_surface(X,Y,view,facecolors=colors,rstride=3,cstride=3,linewidth=0,antialiased=False,shade=False)
    for xx,yy,zz in routes:ax.plot(xx,yy,zz,color='#df4136',lw=1.4,zorder=20)
    ax.view_init(elev=36,azim=angle)
    ax.set_xlim(0,3200);ax.set_ylim(0,3200);ax.set_zlim(np.nanmin(view),np.nanmax(view))
    from matplotlib.ticker import MaxNLocator
    ax.zaxis.set_major_locator(MaxNLocator(3))
    ax.set_box_aspect((3200,3200,np.nanmax(view)-np.nanmin(view)))
    ax.set_xlabel('East from crop edge (m)',fontsize=9);ax.set_ylabel('South from crop edge (m)',fontsize=9)
    ax.set_zlabel('Elevation (m)',fontsize=9);ax.tick_params(labelsize=8)
    ax.set_title(f'View {j} / azimuth {angle%360} degrees',fontsize=12,color='#273d39')
fig.suptitle('Thunder Mountain / two views of the same terrain sample',fontsize=20,x=.05,ha='left',color='#273d39')
fig.text(.05,.90,'USGS 1m DEM source • 8m samples / 24m display mesh • equal physical axis scales • no vertical exaggeration',fontsize=11,color='#9c5433')
fig.text(.05,.08,'Red line: USFS mapped Thunder Mountain trail, draped on the DEM and lifted 3m for visibility. This is not a surveyed trail tread.',fontsize=10)
fig.text(.05,.05,'Blank areas are missing terrain data. Crop edges are not cliffs. Grid terrain cannot establish footing, overhangs or exact cliff-edge clearance.',fontsize=10)
fig.text(.05,.02,'Sources E11 / E18 • full URLs and limitations: docs/SOURCES.md • 2026-10-07 planning draft',fontsize=9,color='#9c5433')
fig.subplots_adjust(top=.85,bottom=.13,left=.025,right=.975,wspace=.02)
fig.savefig(ROOT/'previews'/'thunder-terrain-two-views.png',dpi=140)
print('saved terrain companion')
