"""Create a simple RGB image-only PDF for phone viewers; retain the full atlas."""
import argparse,subprocess,tempfile,json,hashlib
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--pages-dir',type=Path);args=parser.parse_args()
source=ROOT/'output/pdf/boundary-waters-six-page-atlas.pdf'
output=ROOT/'output/pdf/boundary-waters-iphone.pdf'
with tempfile.TemporaryDirectory(prefix='bw-mobile-') as tmp:
 pages=args.pages_dir or Path(tmp)
 if not args.pages_dir:
  subprocess.run(['pdftoppm','-r','250','-jpeg','-jpegopt','quality=92,optimize=y',str(source),str(pages/'page')],check=True)
 images=sorted(pages.glob('page-*.jpg'));assert len(images)==6
 pdf=canvas.Canvas(str(output),pagesize=(1224,792),pageCompression=1,pdfVersion=(1,3))
 pdf.setTitle('Boundary Waters - iPhone compatible atlas');pdf.setAuthor('pwdel/qgis')
 for image in images:
  with Image.open(image) as im:
   assert im.mode=='RGB' and im.size==(4250,2750),(im.mode,im.size)
  pdf.drawImage(str(image),0,0,width=1224,height=792,mask=None)
  pdf.setFillColorRGB(248/255,245/255,235/255);pdf.rect(0,0,1224,31,fill=1,stroke=0)
  pdf.setFillColorRGB(.14,.24,.23);pdf.setFont('Helvetica',9)
  pdf.drawCentredString(612,11,'PHONE COPY - Page images only. Original-map attachments and clickable links are available in the full atlas, not this copy.')
  pdf.showPage()
 pdf.save()
r=PdfReader(output);assert len(r.pages)==6
for p in r.pages:
 assert float(p.mediabox.width)==1224 and float(p.mediabox.height)==792
 assert not p.get('/Annots')
 objs=[o.get_object() for o in p['/Resources']['/XObject'].values()]
 assert len(objs)==1 and objs[0]['/Subtype']=='/Image' and objs[0]['/ColorSpace']=='/DeviceRGB' and '/SMask' not in objs[0]
record={'pages':6,'page_inches':[17,11],'dpi':250,'pdf_version':'1.3','color':'RGB','content':'one JPEG per page; no layers, transparency, annotations or embedded attachments','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'output_bytes':output.stat().st_size}
(ROOT/'docs/mobile-pdf-validation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
