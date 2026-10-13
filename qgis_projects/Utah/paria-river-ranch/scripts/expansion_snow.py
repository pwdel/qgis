"""Build auditable station snow climatology for the Utah riding atlas.
Run from anywhere; inputs are archived NOAA 1991-2020 by-station CSVs.
No spatial interpolation or forecast probabilities are generated.
"""
import csv, json, calendar, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sources/expansion-snow'
MONTH_LENGTH=[31,28+8/30,31,30,31,30,31,31,30,31,30,31]
def quantity(row,key):
    raw=row.get(key,'').strip()
    flag=row.get('meas_flag_'+key,'').strip()
    value=float(raw) if raw and flag not in ('M','Y','Z') else None
    if value is not None and value <= -999: value=None
    return dict(value=value,measurement_flag=flag or None,completeness_flag=row.get('comp_flag_'+key,'').strip() or None,years=int(row['years_'+key]) if row.get('years_'+key,'').strip() else None,missing=value is None,nonzero_rounded_to_zero=flag=='X')
stations=[]
for f in sorted(OUT.glob('monthly-*.csv')):
    sid=f.stem.split('-',1)[1]
    rows=list(csv.DictReader(f.open()))
    daily=list(csv.DictReader((OUT/f'daily-{sid}.csv').open()))
    r=rows[0]
    s=dict(id=sid,name=r['NAME'],latitude=float(r['LATITUDE']),longitude=float(r['LONGITUDE']),elevation_m=float(r['ELEVATION']),elevation_ft=round(float(r['ELEVATION'])/0.3048),normal_period='1991-2020',source_urls={k:f'https://www.ncei.noaa.gov/data/normals-{k}/1991-2020/access/{sid}.csv' for k in ['monthly','daily']},months=[])
    for row in rows:
        month=int(row['DATE']); d=next(x for x in daily if x['DATE']==f'{month:02d}-15')
        q=quantity(row,'MLY-SNWD-AVGNDS-GE001WI')
        s['months'].append(dict(month=month,month_name=calendar.month_name[month],snowfall_inches=quantity(row,'MLY-SNOW-NORMAL'),snowfall_days_ge_0_1_inches=quantity(row,'MLY-SNOW-AVGNDS-GE001TI'),snow_depth_days_ge_1_inch=q,snow_depth_day_frequency_pct=None if q['value'] is None else round(q['value']/MONTH_LENGTH[month-1]*100,3),midmonth_snow_depth_ge_1_inch_pct=quantity(d,'DLY-SNWD-PCTALL-GE001WI')))
    s['monthly_snowfall_inches']=[m['snowfall_inches']['value'] for m in s['months']]
    s['monthly_snow_depth_day_frequency_pct']=[m['snow_depth_day_frequency_pct'] for m in s['months']]
    s['monthly_midmonth_snow_depth_probability_pct']=[m['midmonth_snow_depth_ge_1_inch_pct']['value'] for m in s['months']]
    s['annual_snowfall_inches_sum_of_monthly_normals']=round(sum(s['monthly_snowfall_inches']),1) if all(v is not None for v in s['monthly_snowfall_inches']) else None
    stations.append(s)
metadata=dict(title='Nearby station snow climatology; point observations, no interpolated surface',normal_period='1991-2020',month_order='January through December',retrieved='2026-10-08',snowfall_definition='Normal monthly sum of new snowfall; inches. This is not standing snow depth.',snow_depth_frequency_definition='100 * NOAA normal monthly days with observed snow depth >=1 inch / average calendar days in that month over 1991-2020; station day frequency, not probability that a trip or entire month has snow.',midmonth_probability_definition='NOAA DLY-SNWD-PCTALL-GE001WI for the 15th: smoothed historical probability (%) of snow depth >=1 inch in 29-day windows centered on that calendar day. Not probability of at least one snow day during a 29-day visit.',missing_definition='null means NOAA does not supply the variable or marks it missing/insufficient/inconsistent. A rounded zero does not imply impossibility. All source measurement and completeness flags and contributing year counts retained per quantity.',completeness_flags={'S':'Standard: WMO data availability for 24 or more years','R':'Representative: 10 or more years; gaps estimated from surrounding stations','P':'Provisional: 10 or more years; gaps cannot be filled','E':'Estimated: 2 or more years plus nearby standard stations'},limitations=['Station values apply at station elevations and exposure, not route segments. No lapse-rate interpolation is defensible from these sparse snow statistics.','Do not multiply daily probabilities into trip probabilities: snow persistence and weather days are dependent.','Snowfall and standing snow differ because of melting, settling, wind, exposure and timing.','1991-2020 product does not guarantee 30 valid years for every variable; use per-month years and completeness flags.','A separate exploratory satellite ensemble is available: see gridded-snow-metadata.json. It differs from station snow-depth frequency and is not locally validated.'],enso_footnote='El Niño/La Niña can alter broad seasonal precipitation patterns, but Utah impacts are inconsistent; neither phase reliably predicts October snow on an individual route. These normals combine all ENSO phases and are not a seasonal forecast.',enso_sources=['https://statesummaries.ncics.org/chapter/ut/','https://www.weather.gov/twc/enso'],documentation_urls=['https://www.ncei.noaa.gov/data/normals-monthly/1991-2020/doc/Readme_By-Variable_By-Station_Normals_Files.txt','https://www.ncei.noaa.gov/data/normals-monthly/1991-2020/doc/Normals_MLY_Documentation_1991-2020.pdf','https://www.ncei.noaa.gov/data/normals-daily/1991-2020/doc/Normals_DLY_Documentation_1991-2020.pdf'])
(OUT/'snow-climatology.json').write_text(json.dumps(dict(metadata=metadata,stations=stations),indent=2)+'\n')
features=[]
for s in stations:
    props={k:s[k] for k in ['id','name','elevation_m','elevation_ft','normal_period']}
    props.update(oct_snowfall_in=s['monthly_snowfall_inches'][9],oct_snow_depth_day_frequency_pct=s['monthly_snow_depth_day_frequency_pct'][9],oct15_snow_depth_ge_1_inch_pct=s['monthly_midmonth_snow_depth_probability_pct'][9])
    for m in s['months']:
        i=m['month'];props[f'm{i:02d}_snowfall_in']=m['snowfall_inches']['value'];props[f'm{i:02d}_snwd_day_pct']=m['snow_depth_day_frequency_pct'];props[f'm{i:02d}_snwd_years']=m['snow_depth_days_ge_1_inch']['years'];props[f'm{i:02d}_snwd_flag']=m['snow_depth_days_ge_1_inch']['completeness_flag']
    features.append(dict(type='Feature',geometry=dict(type='Point',coordinates=[s['longitude'],s['latitude']]),properties=props))
(OUT/'snow-stations.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),indent=2)+'\n')
assert len(stations)==9
for s in stations:
    assert len(s['months'])==12
    for v in s['monthly_snow_depth_day_frequency_pct']+s['monthly_midmonth_snow_depth_probability_pct']:
        assert v is None or 0 <= v <= 100
manifest=[dict(file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(OUT.glob('*')) if f.is_file() and f.name!='manifest.json']
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Verified 9 stations x 12 months; probabilities bounded; nulls retained.')
for s in stations: print(s['name'],s['monthly_snowfall_inches'],s['monthly_snow_depth_day_frequency_pct'])
