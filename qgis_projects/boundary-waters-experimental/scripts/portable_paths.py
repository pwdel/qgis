"""Normalize QGIS 4 layout fallback layer references as well as datasource paths."""
from pathlib import Path
import zipfile

def normalize(root):
 prefix=str(root.resolve())+'/'
 qgs=root/'clearwater-navigation.qgs';qgs.write_text(qgs.read_text().replace(prefix,'./'))
 qgz=root/'clearwater-navigation.qgz';tmp=root/'clearwater-navigation.portable.tmp'
 with zipfile.ZipFile(qgz) as src,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as dst:
  for info in src.infolist():
   data=src.read(info.filename)
   if info.filename.endswith('.qgs'):data=data.decode().replace(prefix,'./').encode()
   dst.writestr(info,data)
 tmp.replace(qgz)
 for p in (root/'layouts').glob('*.qpt'):p.write_text(p.read_text().replace(prefix,'../'))
if __name__=='__main__':normalize(Path(__file__).resolve().parents[1])
