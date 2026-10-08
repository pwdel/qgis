import json,urllib.request,concurrent.futures,pathlib
root=pathlib.Path(__file__).parent/'fisheries-raw'
ids=['16022700','16023400','16023200','16023000','16013700','16013800','16009300','16013900','16008600','16004200','16004100','16014100','16014200']
def get(t):
 id,kind,url=t
 try:
  b=urllib.request.urlopen(url,timeout=45).read(); (root/(id+'-'+kind)).write_bytes(b);return id,kind,len(b)
 except Exception as e:return id,kind,str(e)
tasks=[]
for id in ids:
 tasks.extend([(id,'survey.json','https://maps.dnr.state.mn.us/cgi-bin/lakefinder/detail.cgi?type=lake_survey&id='+id),(id,'stocking.html','https://www.dnr.state.mn.us/lakefind/showstocking.html?downum='+id)])
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for r in ex.map(get,tasks):print(r)
