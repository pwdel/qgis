#!/usr/bin/env python3
"""Conservative terrain profiles of published horse-use trail geometries."""
import csv, json, math, os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
AREAS=['02-ranch','03-mount-carmel','04-red-canyon']
FT=3.280839895; MI=1609.344

def runs(z):
    valid=np.isfinite(z);starts=np.flatnonzero(valid & ~np.r_[False,valid[:-1]])
    ends=np.flatnonzero(valid & ~np.r_[valid[1:],False])+1
    return zip(starts,ends)

def smooth_segments(z):
    """3-sample median then 3-sample mean; never cross nodata; fix endpoints."""
    result=np.array(z,dtype=float).copy()
    for lo,hi in runs(result):
        x=result[lo:hi].copy()
        if len(x)<3:continue
        med=np.array([np.median(x[max(0,i-1):min(len(x),i+2)]) for i in range(len(x))])
        out=np.convolve(np.pad(med,1,mode='edge'),np.ones(3)/3,mode='valid')
        out[0]=x[0];out[-1]=x[-1];result[lo:hi]=out
    return result

def elevation_metrics(z,threshold=3.):
    """Cumulative turning points with 3m reversal threshold; gaps split totals."""
    ascent=descent=0.
    for lo,hi in runs(np.asarray(z)):
        x=np.asarray(z)[lo:hi]
        if len(x)<2:continue
        anchor=peak=float(x[0]);direction=0;points=[anchor]
        for v in x[1:]:
            v=float(v)
            if direction==0:
                if abs(v-anchor)>=threshold:direction=1 if v>anchor else -1;peak=v
            elif direction>0:
                if v>peak:peak=v
                elif peak-v>=threshold:points.append(peak);direction=-1;peak=v
            else:
                if v<peak:peak=v
                elif v-peak>=threshold:points.append(peak);direction=1;peak=v
        if direction:points.append(peak)
        dif=np.diff(points);ascent+=sum(dif[dif>0]);descent-=sum(dif[dif<0])
    return float(ascent),float(descent)

def main():
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from qgis.core import (QgsApplication,QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsProject,QgsGeometry,QgsRectangle,QgsJsonUtils,QgsPointXY)
    from osgeo import gdal
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    app=QgsApplication([],False);app.initQgis()
    src=ROOT/'sources';dst=ROOT/'derived/profiles';out=src/'profiles';dst.mkdir(parents=True,exist_ok=True);out.mkdir(exist_ok=True)
    tx=QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),QgsCoordinateReferenceSystem('EPSG:26912'),QgsProject.instance())
    back=QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:26912'),QgsCoordinateReferenceSystem('EPSG:4326'),QgsProject.instance())
    datasets={s:json.loads((src/(s+'-trails.geojson')).read_text())['features'] for s in ['state','usfs']}
    aliases={'Rich':'Rich Trail','Casto':'Casto Canyon','Cassidy Trail':'Cassidy'}
    priority=['Thunder Mountain','Losee Canyon','Casto Canyon','Cassidy','Pines Horse Trail','Rich Trail']
    allmeta={'schema_version':'1.0','method':'Terrain model along published lines; no trail-tread survey. State HorseAllowed=Yes is published use, not current authorization.','areas':{}}
    for area in AREAS:
        bbox=json.loads((src/(area+'-extent.json')).read_text())['bbox_utm12'];box=QgsGeometry.fromRect(QgsRectangle(*bbox))
        inventory=[];groups={}
        for source,features in datasets.items():
            for feat in features:
                prop=feat['properties'];name=prop.get('PrimaryName') if source=='state' else prop.get('trail_name')
                if not name:continue
                geom=QgsJsonUtils.stringToFeatureList(json.dumps(feat))[0].geometry();geom.transform(tx)
                if not geom.intersects(box):continue
                horse=prop.get('HorseAllowed') if source=='state' else prop.get('pack_saddle_managed') or prop.get('pack_saddle_accpt')
                allowed=source=='state' and horse=='Yes'
                oid=prop.get('OBJECTID',prop.get('objectid'))
                record={'source':source,'source_id':oid,'name':name,'published_horse_attribute':horse,'restriction':prop.get('OtherRestrictions') if source=='state' else prop.get('pack_saddle_restricted'),'cartocode':prop.get('CartoCode'),'selected':allowed,'reason':'State published HorseAllowed=Yes' if allowed else ('USFS context / duplicate geometry; state horse-use lines used' if source=='usfs' else 'Horse use not explicitly supported')}
                inventory.append(record)
                if not allowed:continue
                key=aliases.get(name,name);g=geom.intersection(box)
                groups.setdefault(key,[]).append((g,record,not box.contains(geom)))
        ds=gdal.Open(str(src/(area+'-dem.tif')));band=ds.GetRasterBand(1);arr=band.ReadAsArray();gt=ds.GetGeoTransform();nd=band.GetNoDataValue();res=abs(gt[1]);step=max(30.,res*2)
        def sample(point):
            x=(point.x()-gt[0])/gt[1]-.5;y=(point.y()-gt[3])/gt[5]-.5;i=int(math.floor(x));j=int(math.floor(y))
            if i<0 or j<0 or i+1>=arr.shape[1] or j+1>=arr.shape[0]:return np.nan
            v=arr[j:j+2,i:i+2].astype(float)
            if not np.all(np.isfinite(v)) or (nd is not None and np.any(v==nd)):return np.nan
            fx=x-i;fy=y-j
            return float(v[0,0]*(1-fx)*(1-fy)+v[0,1]*fx*(1-fy)+v[1,0]*(1-fx)*fy+v[1,1]*fx*fy)
        profiles=[];geo=[]
        for name,items in sorted(groups.items()):
            # unary union nodes intersections, mergeLines only degree-2 endpoint continuity.
            union=QgsGeometry.unaryUnion([i[0] for i in items]);merged=union.mergeLines() if union.isMultipart() else union
            parts=merged.asGeometryCollection() if merged.isMultipart() else [merged]
            parts=sorted([p for p in parts if p.length()>1],key=lambda p:-p.length())
            for k,g in enumerate(parts):
                pts=g.asPolyline()
                if not pts:continue
                # Deterministic westmost (then southmost) start; independent components never joined.
                if (pts[0].x(),pts[0].y())>(pts[-1].x(),pts[-1].y()):pts=list(reversed(pts));g=QgsGeometry.fromPolylineXY(pts)
                length=g.length();dist=np.linspace(0,length,max(2,math.ceil(length/step)+1));raw=np.array([sample(g.interpolate(float(d)).asPoint()) for d in dist]);sm=smooth_segments(raw);a,d=elevation_metrics(sm);valid=np.flatnonzero(np.isfinite(sm));base=sm[valid[0]] if len(valid) else np.nan
                slug=area+'-'+''.join(c.lower() if c.isalnum() else '-' for c in name).strip('-')+f'-{k+1:02d}'
                clipped=any(min(abs(pt.x()-bbox[0]),abs(pt.x()-bbox[2]),abs(pt.y()-bbox[1]),abs(pt.y()-bbox[3]))<0.02 for pt in (pts[0],pts[-1]));label=name+(f' · part {k+1}/{len(parts)}' if len(parts)>1 else '')+(' [map section]' if clipped else '')
                source_ids=[i[1]['source_id'] for i in items if i[0].intersection(g).length()>0.01]
                rec={'id':slug,'name':name,'label':label,'component':k+1,'component_count':len(parts),'map_clipped':clipped,'source':'state-trails.geojson','source_ids':source_ids,'published_horse_status':('Conflicting: HorseAllowed=Yes / Hiking Only category' if name=='Arches Trail' else 'HorseAllowed=Yes; current permission unverified'),'direction':'Start at westernmost endpoint (southwest if equal longitude), follow source geometry','start_wgs84':list(back.transform(pts[0])),'end_wgs84':list(back.transform(pts[-1])),'distance_miles':length/MI,'ascent_ft':a*FT,'descent_ft':d*FT,'sample_spacing_m':length/(len(dist)-1),'valid_samples':len(valid),'sample_count':len(dist),'shorter_than_two_output_pixels':length<2*res,'gap_samples':len(dist)-len(valid),'gap_count':len(list(runs(np.where(np.isfinite(raw),np.nan,0.)))),'relative_zero':'first valid sample' if len(valid) and valid[0]>0 else 'chosen start','dem_file':area+'-dem.tif','dem_source':'USGS 3DEP ImageServer mosaic; native sources unresolved; not verified lidar','dem_output_pixel_m':res,'smoothing':'3-sample median then 3-sample moving mean, segment endpoints retained; 3m reversal threshold for totals','csv':'sources/profiles/'+slug+'.csv'}
                profiles.append(rec)
                with (out/(slug+'.csv')).open('w') as fp:
                    w=csv.writer(fp);w.writerow(['distance_miles','raw_elevation_m','smoothed_elevation_m','relative_elevation_ft','valid'])
                    for distance,r,s in zip(dist,raw,sm):w.writerow([round(distance/MI,6),round(r,3) if np.isfinite(r) else '',round(s,3) if np.isfinite(s) else '',round((s-base)*FT,2) if np.isfinite(s) else '',int(np.isfinite(s))])
                wg=QgsGeometry(g);wg.transform(back);geo.append({'type':'Feature','properties':rec,'geometry':json.loads(wg.asJson())})
                rec['_x']=dist/MI;rec['_y']=(sm-base)*FT;rec['_map']=np.array([[p.x(),p.y()] for p in pts])
        names=list(dict.fromkeys(p['name'] for p in profiles))
        import matplotlib.gridspec as gridspec
        plt.rcParams['svg.fonttype']='path'
        def chart(groups_to_plot,path):
            large=len(groups_to_plot)<=3
            cols=3 if len(groups_to_plot)>6 else 1
            rows=math.ceil(len(groups_to_plot)/cols)
            fig=plt.figure(figsize=(16.3,8.23),facecolor='white')
            grid=gridspec.GridSpec(rows,cols,figure=fig,left=.018,right=.99,bottom=.07,top=.965,hspace=1.6 if rows>3 else .5,wspace=.20)
            colors=['#1b646b','#b75028','#72468f','#5b791f','#176ba0','#9a343d','#7c6326','#424852']
            for idx,(name,ps) in enumerate(groups_to_plot):
                cell=grid[idx//cols,idx%cols].get_position(fig)
                x,y,w,h=cell.x0,cell.y0,cell.width,cell.height
                mx=fig.add_axes([x,y,w*.18,h]);ax=fig.add_axes([x+w*.29,y,w*.71,h])
                conflict=any(i['selected'] and i['name'] in [name,'Arches Trail'] and 'Hiking Only' in str(i['cartocode']) for i in inventory) if name=='Arches Trail' else False
                title=name+(' *' if any(p['map_clipped'] for p in ps) else '')+(' †' if any(p['gap_samples'] for p in ps) else '')+(' — USE CONFLICT' if conflict else '')
                fig.text(x,y+h+.013,title,fontsize=12 if large else 8,fontweight='bold',color='#8a3c24' if conflict else '#202d30')
                for j,p in enumerate(ps):
                    color=colors[j%len(colors)];ax.plot(p['_x'],p['_y'],color=color,lw=1.1)
                    xy=p['_map'];mx.plot(xy[:,0],xy[:,1],color=color,lw=1.2);mx.scatter(xy[0,0],xy[0,1],s=8,color=color)
                    if len(ps)>1:mx.text(xy[0,0],xy[0,1],str(j+1),fontsize=7,color=color)
                ax.axhline(0,color='#aab0ac',lw=.5);ax.grid(alpha=.15);ax.tick_params(labelsize=10 if large else 7,pad=1);ax.spines[['top','right']].set_visible(False)
                mx.set_aspect('equal',adjustable='datalim');mx.set_xticks([]);mx.set_yticks([])
                for spine in mx.spines.values():spine.set_color('#d6ddda')
                mx.text(.02,.98,'N ↑',transform=mx.transAxes,fontsize=9 if large else 7,va='top')
                # Each component retains its own ascent/descent; no disconnected-route total.
                metrics=[f"{j+1}: {p['distance_miles']:.2f} +{p['ascent_ft']:.0f}/−{p['descent_ft']:.0f}" for j,p in enumerate(ps)]
                lines=['  |  '.join(metrics[k:k+4]) for k in range(0,len(metrics),4)]
                fig.text(x,y-.023,'\n'.join(lines),fontsize=10 if large else 7,va='top',linespacing=1.05)
            legend=fig.text(.018,.005,'X: miles from start. Y: ft relative to first valid sample. Cutouts: N up; dot=start; color/number=part. Metrics: part: miles +ascent/−descent (ft). * Map section. † DEM gap; see data.',fontsize=9 if large else 7)
            fig.canvas.draw()
            legend_box=legend.get_window_extent(fig.canvas.get_renderer())
            assert legend_box.x1 <= fig.bbox.x1, 'Legend exceeds page width'
            print(area, 'legend right edge',round(legend_box.x1/fig.dpi,2),'of',fig.get_figwidth(),'inches')
            fig.savefig(path,format='svg');fig.savefig(path.with_suffix('.png'),dpi=120);plt.close(fig)
        chart([(n,[p for p in profiles if p['name']==n]) for n in names],dst/(area+'-profiles.svg'))
        # Full component data and printed chart share every route; no hidden priority selection.
        selected=profiles
        for p in profiles:p.pop('_x');p.pop('_y');p.pop('_map');p['shown_on_page']=p in selected
        (out/(area+'-routes.geojson')).write_text(json.dumps({'type':'FeatureCollection','features':geo},indent=2))
        meta={'area':area,'dem_source':'USGS 3DEP service mosaic fallback','dem_output_pixel_m':res,'native_resolution_verified':False,'profiles':profiles,'inventory':inventory,'page_profile_ids':[p['id'] for p in selected],'omitted_page_components':0,'plot_svg':'derived/profiles/'+area+'-profiles.svg','named_route_count':len(names),'summary':f'{len(names)} named routes; {len(profiles)} continuous sections; all shown. Terrain-model estimates; current horse authorization unverified.'}
        (out/(area+'-profiles.json')).write_text(json.dumps(meta,indent=2));allmeta['areas'][area]=meta
        print(area,len(profiles),'components;',len(groups),'named routes;',len(selected),'printed charts')
    (out/'profiles.json').write_text(json.dumps(allmeta,indent=2))
if __name__=='__main__':main()
