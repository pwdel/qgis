"""Acceptance checks for saved GIS artifacts, geometry and student answer isolation."""
import json,tempfile,shutil,datetime,platform,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from qgis.core import QgsApplication,QgsProject,QgsLayoutItemMap,QgsLayoutItemPicture,QgsLayoutExporter,Qgis
from shapely.geometry import shape,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
app=QgsApplication([],False);app.initQgis();checks=[]
def check(ok,detail):
 assert ok,detail
 checks.append(detail)
def inspect(root,suffix):
 p=root/f'clearwater-navigation.{suffix}';check(p.is_file(),f'{suffix}: file exists')
 pr=QgsProject();check(pr.read(str(p)),f'{suffix}: read succeeds')
 check(len(pr.layoutManager().layouts())==7,f'{suffix}: seven native layouts')
 for layer in pr.mapLayers().values():
  check(layer.isValid(),f'{suffix}: valid {layer.name()}')
  check(Path(layer.source().split('|')[0]).resolve().is_relative_to(root.resolve()),f'{suffix}: local {layer.name()}')
 for layout in pr.layoutManager().layouts():
  maps=[x for x in layout.items() if isinstance(x,QgsLayoutItemMap)]
  check(bool(maps),layout.name()+': native map')
  for x in layout.items():
   if isinstance(x,QgsLayoutItemPicture):
    check(Path(x.picturePath()).resolve().is_relative_to(root.resolve()),layout.name()+': local compass')
    check(not x.isMissingImage(),layout.name()+': compass available')
  if layout.name().startswith('Student'):
   for m in maps:
    check(m.keepLayerSet(),layout.name()+': layer set locked')
    check(all(x.customProperty('teaching/role')=='student' for x in m.layers()),layout.name()+': no instructor layers')
  else:
   for m in maps:
    routes=[x for x in m.layers() if x.customProperty('teaching/file') in ['route-a','route-b']]
    check(len(routes)==1,layout.name()+': exactly one answer route')
 for node in pr.layerTreeRoot().findLayers():
  if node.layer().customProperty('teaching/role') in ['instructor','reference']:check(not node.isVisible(),f'{suffix}: hidden {node.name()}')
 return pr
for suffix in ['qgz','qgs']:pr=inspect(ROOT,suffix)
water={f['properties']['name']:shape(f['geometry']) for f in json.loads((ROOT/'derived/lakes.geojson').read_text())['features']}
meta=json.loads((ROOT/'derived/map-data.json').read_text());trans={x['id']:x for x in meta['transitions']}
for route in ['a','b']:
 fs=json.loads((ROOT/'derived'/f'route-{route}.geojson').read_text())['features'];check(len(fs)==(6 if route=='a' else 10),f'{route}: expected number of water legs')
 check(Point(fs[0]['geometry']['coordinates'][0]).distance(Point(fs[-1]['geometry']['coordinates'][-1]))<.001,f'{route}: closes at same Clearwater position')
 for i,f in enumerate(fs):
  g=shape(f['geometry']);lake=f['properties']['lake'];check(water[lake].buffer(2).covers(g),f'{route}/{lake}: stays in mapped water within 2 m tolerance')
  if i<len(fs)-1:
   tr=trans[f['properties']['next_clue']];check(tr['from_lake']==lake and tr['to_lake']==fs[i+1]['properties']['lake'],f'{route}/{lake}: supported lake transition')
   check(Point(g.coords[-1]).distance(Point(tr['landing_xy'][0]))<.001,f'{route}/{lake}: ends at candidate')
   check(Point(fs[i+1]['geometry']['coordinates'][0]).distance(Point(tr['landing_xy'][1]))<.001,f'{route}/{lake}: next leg starts at candidate')
for fn,count in [('clues',14),('high-points',12),('portages-recorded',7)]:
 fs=json.loads((ROOT/'derived'/f'{fn}.geojson').read_text())['features'];check(len(fs)==count,f'{fn}: {count} features')
check(all(shape(f['geometry']).area>100000 for f in json.loads((ROOT/'derived/clues.geojson').read_text())['features']),'Clues are broad areas, not thin trail corridors')
for p in (ROOT/'layouts').glob('*.qpt'):
 check('/Users/' not in p.read_text(),p.name+': no author-machine absolute paths')
check('/Users/' not in (ROOT/'clearwater-navigation.qgs').read_text(),'QGS contains no author-machine absolute paths')
# Move a real copy away from the repository and export from the saved project.
with tempfile.TemporaryDirectory(prefix='clearwater-relocation-') as tmp:
 dest=Path(tmp)/'chart';dest.mkdir()
 for d in ['derived','sources','styles','layouts']:shutil.copytree(ROOT/d,dest/d)
 for ext in ['qgs','qgz']:shutil.copy2(ROOT/f'clearwater-navigation.{ext}',dest/f'clearwater-navigation.{ext}')
 relocated=inspect(dest,'qgz')
 layout=next(x for x in relocated.layoutManager().layouts() if x.name().startswith('Student 01'))
 exporter=QgsLayoutExporter(layout);settings=QgsLayoutExporter.PdfExportSettings();settings.dpi=150
 check(exporter.exportToPdf(str(Path(tmp)/'relocated.pdf'),settings)==QgsLayoutExporter.ExportResult.Success,'Relocated saved QGZ exports a student PDF')
 check((Path(tmp)/'relocated.pdf').stat().st_size>10000,'Relocated export has content')
 del exporter,layout
 relocated.clear()
 del relocated
report={'status':'pass','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qgis':Qgis.QGIS_VERSION,'python':platform.python_version(),'platform':platform.platform(),'checks':checks,'check_count':len(checks),'scope':'Saved .qgz/.qgs, seven editable layouts, all local assets, hidden instructor group, water-leg geometry, closure and relocated QGZ export. Visual PDF checks recorded separately.'}
(ROOT/'docs/validation.json').write_text(json.dumps(report,indent=2))
print(f'PASS: {len(checks)} checks; both project formats, geometry, student isolation and relocated export')

pr.clear()
del pr
import gc
gc.collect()
app.exitQgis()
