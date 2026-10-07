"""Create the curated location/evidence overlay; no guessed route lines."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'sources'

def source(id,title,publisher,url,claim,limits,medium='Website',authority='WebsiteGuidance',date=None,status='Retrieved'):
    return dict(id=id,title=title,publisher=publisher,url=url,supported_claim=claim,
      limitations=limits,medium=medium,authority_type=authority,retrieved_at='2026-10-07',
      observed_at=None,published_at=date,retrieval_status=status)

e=[
 source('E01','Horse camping','Paria River Ranch','https://pariariverranch.com/horse-camping-1',
  'Ranch advertises horse camping, potable water for people and horses, and rides/haul-outs.',
  'Owner advertising; no live flow test or exact-rig turning assessment. Route names do not confer public-land permission.',authority='OwnerStatement'),
 source('E02','Paria River Ranch location','AAA / Roverpass','https://www.aaa.com/tripcanvas/campground/paria-river-ranch-31872',
  'Ranch reference coordinate 37.106604, -111.912501 and address.',
  'Third-party facility reference; not a surveyed gate, hydrant or parking stall.'),
 source('E03','Coyote Hollow','Recreation.gov','https://www.recreation.gov/camping/campgrounds/10381898',
  'Four seasonal nonpotable horse-water hydrants may be available; supply can be exhausted late summer/fall. Equestrian camping; fallback water described at Red Canyon Campground.',
  'Campground supply differs from trail water. No present flow or refill capacity verification.'),
 source('E04','White House Campground','Bureau of Land Management','https://www.blm.gov/visit/white-house-campground',
  'Drinking water is described at Paria Contact Station, not at White House campsites.',
  'Does not establish horse-trailer turnaround, bulk-water fill permission, or current operating hours.'),
 source('E05','Backcountry Rides in the Kanab Area','Back Country Horsemen of Utah','https://www.bchutah.org/High%20Desert/2022-2-4-Backcountry-Rides-Kanab-Area.pdf',
  'Page 1 describes Barracks corrals staging and warns that farther down the road trailer parking/turning is poor; Bay Bill is a riding lead. Page 2 warns about hauling up the Old Paria access grade.',
  'Historical community riding report, not current owner permission or measured rig fit. Do not reuse its broad claims about riding anywhere on BLM land.',medium='PDF',date='2022-02-04'),
 source('E06','Thunder Mountain trail sheet 33098','USDA Forest Service','https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/stelprdb5436859.pdf',
  'Indexed USFS description reports narrow exposed terrain, drop-offs and no water on the trail.',
  'Original URL returned HTTP 404 on retrieval; claim retained as a search-index lead needing current manager confirmation. Not field-verified.',medium='PDF',status='SearchIndexOnly_Original404'),
 source('E07','Belly of the Dragon','Kane County tourism','https://www.visitsouthernutah.com/11-breathtaking-things-to-do-in-kanab-utah/',
  'Hiking tunnel reference coordinate and drainage/flash-flood warning.',
  'Hiking attraction, not verified horse passage. Newer tourism location record differs; coordinate is approximate and disputed.'),
 source('E08','Utah trailheads','UGRC','https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/UtahTrailheads/FeatureServer/0',
  'Published trailhead reference coordinates, retaining source IDs.',
  'Dataset records here derive from OrbitalView; LastUpdate and access facilities may be null. No evidence of trailer fit.'),
 source('E09','Utah roads','UGRC / local stewards / UDOT','https://gis.utah.gov/products/sgid/transportation/road-centerlines/',
  'Road geometry and CARTOCODE including high-clearance code 16.',
  'Road line/class does not establish public passage, current surface, road grade or trailer compatibility.'),
 source('E10','Utah trails and pathways','UGRC','https://gis.utah.gov/products/sgid/recreation/trails-pathways/',
  'Trail geometry and explicit HorseAllowed attributes.',
  'Incomplete network, mixed-source mapping; original observation dates generally unresolved. Does not supersede closures.'),
 source('E11','National Forest System trails','USDA Forest Service','https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublishWithDataStatus_01/MapServer/0',
  'Trail centerlines, IDs, named segments, tread-width categories and use attributes.',
  'Blank pack/saddle fields are unknown. Tread width is a published category, not a current measurement; typical_trail_grade contains a code, not a numeric grade.'),
 source('E12','Utah lidar coverage','UGRC','https://gis.utah.gov/products/sgid/elevation/lidar/',
  'Completed 2018 Southern Utah and 2019 Kane County projects include sampled locations.',
  'Coverage index is not a terrain raster or present-condition survey; exact per-pixel coverage must be checked.'),
 source('E13','USGS Topo','USGS','https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer',
  'Topographic reference context with roads, place names, hydrography and terrain.',
  'Mixed-date compilation; blue streams are mapped hydrography, not verified drinking supplies.'),
 source('E14','3DEP elevation service','USGS','https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer',
  'Bare-earth elevation mosaic used for regional hillshade and slope context.',
  'Resampled service mosaic. Output pixel size does not establish native resolution, acquisition date or vertical accuracy.'),
 source('E15','Encouraging your horse to drink','University of Minnesota Extension','https://extension.umn.edu/agriculture/animals-and-livestock/horse/encouraging-your-horse-to-drink',
  'Typical 1000-pound horse drinks about 8-10 gallons daily; exercise and heat increase needs.',
  'General husbandry information; five gallons is not a daily upper limit or a sufficient trip-specific allocation.'),
 source('E16','Tom Best camping order 0407-21-19','USDA Forest Service','https://www.fs.usda.gov/sites/nfs/files/r04/dixie/publication/alerts/0407-21-19-Powell-TomBestAreaCampingRestrct-ORIGINAL.pdf',
  'Historic order describes restricted roadside camping areas and ends May 15, 2026 by its terms.',
  'Indexed text; original retrieval failed. Expired document is not current permission or closure. Replacement/order search inconclusive.',medium='PDF',authority='SiteOrder',date='2021-05-11',status='SearchIndexOnly_OriginalUnavailable'),
 source('E17','Mount Carmel US Topo quadrangle','USGS','https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/Current/PDF/UT/UT_Mount_Carmel.pdf',
  'Bay Bill Canyon geographic name and topographic context.',
  'Approximate canyon reference, not a trailhead or recommended turnaround.',medium='PDF'),
 source('E18','Native 1-meter DEM catalog','USGS The National Map','https://tnmaccess.nationalmap.gov/api/v1/products',
  'USGS_1M_12_x38y418_UT_StatewideKane_2020_A20 terrain product around Thunder Mountain.',
  'Project title does not establish flight date. Bare-earth grid cannot resolve overhangs, unstable footing or guarantee cliff-edge accuracy.'),
 source('E19','User destination leads','Map requester',None,
  'Tom Best Spring Road, Red Mountain and dispersed-camping areas were requested as leads.',
  'Unverified personal planning leads; no current snow report, approved campsite boundary or public permission.',medium='Conversation',authority='Unknown'),
]

features=[]
def point(id,name,xy,type,ev,coord,water='Unknown',trailer='Unknown',horse='Unknown',note='',uncertainty=250):
    props=dict(id=id,name=name,label=id+' '+name,feature_type=type,evidence_ids=ev,
      coordinate_evidence_id=coord,water_status=water,trailer_status=trailer,horse_status=horse,
      criticality='Critical',verification_status='PublisherStatement' if ev!=['E19'] else 'Unknown',
      observed_at=None,retrieved_at='2026-10-07',coordinate_precision='ApproximateFacilityOrAreaReference',
      location_uncertainty_m=uncertainty,uncertainty_basis='Editorial caution radius, not measured positional accuracy',
      rig_length_m=None,turnaround_diameter_m=None,entrance_width_m=None,road_grade_percent=None,
      water_flow_lpm=None,water_refill_permission='Unknown',current_conditions='Unknown',notes=note,
      recheck='Confirm with manager/owner for trip date, actual rig and intended activity before relying on this feature.')
    features.append(dict(type='Feature',id=id,geometry=dict(type='Point',coordinates=xy),properties=props))

point('R1','Paria River Ranch',[-111.912501,37.106604],'Ranch',['E01','E02'],'E02',
 'AdvertisedPotable','FacilityAdvertisesRigs','PublishedYes',
 'Primary base. Water advertised for horses and people. Ask about exact rig, stalls, tank fill and supply. Marker is not a hydrant.',150)
point('M1','Barracks staging lead',[-112.6868,37.222],'Trailhead',['E05'],'E05',
 'SurfaceWaterUnverified','HistoricalStagingLead','Unknown',
 'Approximate area inferred from 2022 written directions, not a confirmed entrance. Guide warns against hauling farther downroad. Verify landowner permission.',650)
point('M2','Belly of the Dragon',[-112.687328,37.2117092],'Landmark',['E07'],'E07',
 note='Hiking/drainage tunnel; not a verified horse route. Conflicting tourism coordinates. Do not infer a trailer staging area.',uncertainty=500)
point('M3','Bay Bill Canyon',[-112.7433,37.1803],'CanyonReference',['E05','E17'],'E17',
 'SurfaceWaterUnverified','Unknown','Unknown',
 'Approximate canyon reference. Historical riding lead via the East Fork Virgin River; flash-flood and narrow-turning hazards. No traced route is invented.',500)
heads=json.loads((S/'trailheads.geojson').read_text())['features']
for id,search in [('D1','Losee'),('D2','Casto'),('D3','Thunder Mountain')]:
    f=next(f for f in heads if f['properties']['PrimaryName']==search)
    ev=['E08','E10']+(['E06','E11'] if id=='D3' else [])
    point(id,search+' trailhead',f['geometry']['coordinates'],'Trailhead',ev,'E08',
      horse='PublishedYes',note='UGRC trailhead reference; HorseAllowed comes from separate state trail records. Parking capacity, turning and campsite permission are unverified.',uncertainty=150)
    features[-1]['properties']['source_feature_id']=f['properties']['OBJECTID']
point('D4','Coyote Hollow camp',[-112.269271,37.716588],'Campground',['E03'],'E03',
 'SeasonalStockOnly','Unknown','PublishedYes',
 'Recreation.gov facility coordinate, not hydrant position. Seasonal horse-only water may be exhausted. Camp site lengths and actual rig fit still need checking.',200)
# The requested road area is located from a named source road, rather than an invented campsite.
roads=json.loads((S/'roads.geojson').read_text())['features']
candidates=[f for f in roads if 'TOM' in str(f['properties'].get('FULLNAME','')).upper() and 'BEST' in str(f['properties'].get('FULLNAME','')).upper()]
if candidates:
    def coordinates(f):
        c=f['geometry']['coordinates'];return c if f['geometry']['type']=='LineString' else [p for line in c for p in line]
    # Locate the major unpaved road's junction with HWY 12, not similarly named spurs.
    highway=[p for f in roads if f['properties'].get('FULLNAME')=='HWY 12' for p in coordinates(f)]
    choices=[(p,f) for f in candidates if f['properties'].get('CARTOCODE')=='9' for p in coordinates(f)]
    xy,f=min(choices,key=lambda x:min((x[0][0]-p[0])**2*.63+(x[0][1]-p[1])**2 for p in highway))
    xy=xy[:2]
    point('D5','Tom Best road lead',xy,'RoadReference',['E09','E16','E19'],'E09',
       note='Road reference only, not an approved campsite. User-reported 7700 ft/snow is unverified. Historic 2021 camping order expired; current restrictions unresolved.',uncertainty=200)
    features[-1]['properties']['source_feature_id']=f['properties'].get('OBJECTID')

(S/'evidence.json').write_text(json.dumps({'profile_version':'1.0','records':e},indent=2)+'\n')
for f in features:
    if f['id'] in ['M1','M3']:f['properties']['verification_status']='HistoricalReport'
    if f['id']=='M2':f['properties']['verification_status']='Conflict'
(S/'planning-points.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2)+'\n')
assert all(p['properties']['coordinate_evidence_id'] in {x['id'] for x in e} for p in features)
print('evidence',len(e),'points',len(features))
