"""Package only local deliverables, with SHA256 integrity records."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'output/journey-network-project.zip';manifest=R/'docs/manifest-sha256.json'
files=[p for p in sorted(R.rglob('*')) if p.is_file() and p not in [out,manifest] and '__pycache__' not in p.parts and not p.name.endswith(('~','.pyc','-wal','-shm'))]
manifest.write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[manifest]:z.write(p,str(Path(R.name)/p.relative_to(R)))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(len(files)+1,'files;',round(out.stat().st_size/1024/1024,2),'MiB; ZIP integrity passed')
