"""Restrict geospatial viewports to actual map frames; assemble final downloads."""
from pathlib import Path
import json,zipfile,shutil,hashlib
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ArrayObject,FloatObject,TextStringObject,NameObject
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/mobile';PDF=OUT/'geopdf'
records=json.loads((ROOT/'docs/mobile-layouts.json').read_text())
# QGIS 3.22 appendGeoreference extrapolates the main frame across the page.
# Restrict its ISO 32000 viewport to the actual main-map rectangle: no GPS in margins/insets.
for rec in records:
 path=ROOT/rec['pdf'];r=PdfReader(str(path));w=PdfWriter();page=r.pages[0]
 view=page['/VP'][0].get_object();measure=view['/Measure'].get_object()
 x,y,width,height=rec['map_mm'];factor=72/25.4;pageheight=float(page.mediabox.height)
 def arr(values):return ArrayObject([FloatObject(v) for v in values])
 view[NameObject('/BBox')]=arr([x*factor,pageheight-(y+height)*factor,(x+width)*factor,pageheight-y*factor])
 view[NameObject('/Name')]=TextStringObject('Main map - insets are reference only')
 # Counterclockwise lower-left, upper-left, upper-right, lower-right.
 measure[NameObject('/LPTS')]=arr([0,0,0,1,1,1,1,0]);measure[NameObject('/Bounds')]=arr([0,0,0,1,1,1,1,0])
 measure[NameObject('/GPTS')]=arr([n for lon,lat in rec['corners_lonlat'] for n in (lat,lon)])
 w.add_page(page);w.add_metadata({'/Title':rec['name'],'/Subject':'GPS applies only to main map. Insets and charts are reference. Research: 2026-10-09.'})
 with path.open('wb') as f:w.write(f)
for slug,start in [('ranch',2),('mount-carmel',8),('red-canyon',14)]:
 w=PdfWriter()
 for offset in [0,1,2,3,5]:w.append(str(next(PDF.glob(f'{start+offset:02}-*.pdf'))))
 with (PDF/(slug+'-five-maps.pdf')).open('wb') as f:w.write(f)
 folder=OUT/'qfield'/slug
 shutil.copy2(PDF/(slug+'-five-maps.pdf'),folder/'reference'/(slug+'-five-maps.pdf'))
 shutil.copy2(ROOT/'docs/MOBILE.md',folder/'READ-ME.md')
 # Refresh source notes after exporter, retaining frozen research dates.
 for src in (ROOT/'docs').glob('*.md'):shutil.copy2(src,folder/'reference/docs'/src.name)
 archive=OUT/'qfield'/(slug+'-qfield.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(folder.rglob('*')):
   if f.is_file() and not f.name.endswith(('.qgz~','-wal','-shm')):z.write(f,f.relative_to(folder))
 print(archive.name,archive.stat().st_size,flush=True)
 tifdir=OUT/'gaia'/(slug+'-custom-map-sources');shutil.copy2(ROOT/'docs/MOBILE.md',tifdir/'READ-ME.md')
 shutil.copy2(PDF/(slug+'-five-maps.pdf'),tifdir/'legends-and-evidence.pdf')
 with zipfile.ZipFile(OUT/'gaia'/(slug+'-custom-map-sources.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(tifdir.iterdir()):z.write(f,f.name)
w=PdfWriter()
for n in range(1,20):
 folder=ROOT/'output/pdf/riding' if n in [6,12,18] else PDF
 w.append(str(next(folder.glob(f'{n:02}-*.pdf'))))
with (PDF/'utah-riding-geospatial-atlas.pdf').open('wb') as f:w.write(f)
with zipfile.ZipFile(OUT/'geopdf-individual-sheets.zip','w',zipfile.ZIP_DEFLATED) as z:
 for rec in records:z.write(ROOT/rec['pdf'],Path(rec['pdf']).name)
manifest={}
for directory in [PDF,OUT/'gaia',OUT/'qfield']:
 for f in sorted(directory.iterdir()):
  if f.is_file():manifest[str(f.relative_to(ROOT))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
f=OUT/'geopdf-individual-sheets.zip';manifest[str(f.relative_to(ROOT))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
for f in sorted((OUT/'gaia/tiles').rglob('*.png')):
 manifest[str(f.relative_to(ROOT))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(ROOT/'docs/mobile-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
