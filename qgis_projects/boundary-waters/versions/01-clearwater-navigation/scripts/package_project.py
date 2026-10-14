"""Create a manifest and a portable project bundle, omitting build caches/backups."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def include(p):
 rel=p.relative_to(R)
 return p.is_file() and '__pycache__' not in rel.parts and not p.name.endswith(('~','.pyc')) and p.name not in ['manifest-sha256.json','clearwater-navigation-project.zip']
files=sorted(p for p in R.rglob('*') if include(p))
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
mp=R/'docs/manifest-sha256.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
target=R/'output/clearwater-navigation-project.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[mp]:z.write(p,Path('boundary-waters-experimental')/p.relative_to(R))
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for f in ['clearwater-navigation.qgz','clearwater-navigation.qgs','derived/clues.geojson','output/pdf/clearwater-student.pdf','output/pdf/clearwater-instructor.pdf']:
  assert 'boundary-waters-experimental/'+f in z.namelist()
print(f'Bundle verified: {len(files)+1} files, {target.stat().st_size/1048576:.1f} MiB')
