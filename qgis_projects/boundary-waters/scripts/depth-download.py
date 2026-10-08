from pathlib import Path
import urllib.request,re,json,concurrent.futures,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sources/depth-scans'; OUT.mkdir(exist_ok=True)
lakes={'hungry-jack':'16022700','moss':'16023400','duncan':'16023200','rose':'16023000','rove':'16013700','watap':'16013800','mountain':'16009300','clearwater':'16013900','west-pike':'16008600','east-pike':'16004200','pine':'16004100','caribou':'16014100','little-caribou':'16014200'}
def fetch(pair):
 name,id=pair; url=f'https://www.dnr.state.mn.us/lakefind/showmap.html?downum={id}'
 html=subprocess.check_output(['curl','-L','--fail','--silent',url]); (OUT/f'{name}-index.html').write_bytes(html)
 urls=sorted(set(re.findall(r'https://files.dnr.state.mn.us/lakefind/data/lakemaps/[^\"<> ]+\.pdf',html.decode())))
 files=[]
 for u in urls:
  dest=OUT/f'{name}-{u.rsplit("/",1)[1]}'; data=subprocess.check_output(['curl','-L','--fail','--silent',u]); dest.write_bytes(data)
  files.append({'url':u,'file':str(dest.relative_to(ROOT)),'bytes':len(data)})
 return {'lake':name,'lake_id':id,'index_url':url,'files':files,'georeferenced':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: result=list(pool.map(fetch,lakes.items()))
(ROOT/'sources/depth-manifest.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
