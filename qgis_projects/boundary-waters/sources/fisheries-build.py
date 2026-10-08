import json,re,html,pathlib,datetime
root=pathlib.Path(__file__).parent
raw=root/'fisheries-raw'
species=json.loads(re.search(r'var fish_species = (.*);', (raw/'lakefinder.js').read_text()).group(1))
metadata={r['id']:r for r in json.load(open(raw/'cook-search.json'))['results']}
ids=['16022700','16023400','16023200','16023000','16013700','16013800','16009300','16013900','16008600','16004200','16004100','16014100','16014200']
rows=[]
for id in ids:
 doc=json.load(open(raw/(id+'-survey.json')));assert doc['status']=='SUCCESS'
 d=doc['result']; m=metadata[id]
 s=max((s for s in d['surveys'] if s['surveyType']=='Standard Survey' and s.get('fishCatchSummaries')),key=lambda s:s['surveyDate'])
 caught=sorted(set(c['species'] for c in s['fishCatchSummaries'] if c['totalCatch']>0))
 stocking=(raw/(id+'-stocking.html')).read_text().split('<h1>Lake Stocking Report</h1>')[1]
 records=[]
 if 'No stocking data exists for the requested lake over the last 10 years.' not in stocking:
  table=stocking.split('</table>')[0]
  for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',table):
   cells=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>',tr)]
   if len(cells)==5:
    records.append(dict(year=int(cells[0]),species=re.sub(r'\d+$','',cells[1]).strip(),size=cells[2],number=int(cells[3].replace(',','')),pounds=float(cells[4].replace(',',''))))
 note='Species are positive catches in the latest returned Standard Survey with fish catches; lake-wide evidence, not fishing locations. Absence from this survey is not proof of species absence.'
 if max(x['surveyDate'] for x in d['surveys'])>s['surveyDate']:note+=' Newer targeted habitat surveys exist and are not substituted for fish-catch evidence.'
 summary='; '.join(f"{x['year']} {x['species']} ({x['number']:,} {x['size']})" for x in records) if records else 'No stocking data in the DNR last-10-years report; historical stocking status unknown.'
 rows.append(dict(lake=d['lakeName'],id=id,survey_year=int(s['surveyDate'][:4]),survey_date=s['surveyDate'],species=[species[c]['common_name'] for c in caught],game_species=[species[c]['common_name'] for c in caught if species[c]['game_fish']],stocking_summary=summary,stocking_records=records,max_depth_ft=d['maxDepthFeet'],source_url='https://www.dnr.state.mn.us/lakefind/showreport.html?downum='+id,survey_api_url='https://maps.dnr.state.mn.us/cgi-bin/lakefinder/detail.cgi?type=lake_survey&id='+id,stocking_source_url='https://www.dnr.state.mn.us/lakefind/showstocking.html?downum='+id,metadata_point=m['point']['epsg:4326'],map_ids=m['mapid'],retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),notes=note))
(root/'fisheries.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r['lake'],r['survey_year'],', '.join(r['game_species']),r['stocking_summary'])
