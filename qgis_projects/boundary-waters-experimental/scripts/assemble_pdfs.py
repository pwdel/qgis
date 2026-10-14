"""Combine the separately exported QGIS sheets into the two final booklets."""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parents[1];P=R/'output/pdf'
for audience,count in [('student',3),('instructor',4)]:
 writer=PdfWriter()
 for i in range(1,count+1):
  p=P/f'{audience}-{i:02}.pdf';reader=PdfReader(p);assert len(reader.pages)==1
  writer.append(reader)
 writer.add_metadata({'/Title':f'Clearwater & the Eastern Lakes - {audience.title()}','/Author':'Clearwater navigation teaching experiment','/Subject':'Black-and-white compass navigation exercise; modern source data'})
 target=P/f'clearwater-{audience}.pdf'
 with target.open('wb') as out:writer.write(out)
 assert len(PdfReader(target).pages)==count
 print(target.name,count,'pages')
