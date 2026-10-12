"""Assemble complete PDF structures for Apple Preview and other readers."""
from pathlib import Path
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parents[1];P=R/'output/pdf'
for name,files in [('journey-chart',['01']),('journey-instructor',['02','03','04'])]:
 w=PdfWriter()
 for n in files:w.append(PdfReader(P/f'sheet-{n}.pdf'))
 w.add_metadata({'/Title':"The Canoe Traveller's Network" + (' - instructor key' if name.endswith('instructor') else ''),'/Author':'Boundary Waters teaching experiment'})
 with (P/f'{name}.pdf').open('wb') as f:w.write(f)
 print(name,len(w.pages),'pages')
