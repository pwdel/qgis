from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import subprocess,concurrent.futures,json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'derived/depth-scans'; OUT.mkdir(exist_ok=True)
files=[p for p in (ROOT/'sources/depth-scans').glob('*.pdf') if 'legend' not in p.name]
def render(p):
 dest=OUT/p.stem
 subprocess.run(['pdftoppm','-r','300','-gray','-png','-singlefile',str(p),str(dest)],check=True)
 im=Image.open(str(dest)+'.png').convert('L'); box=ImageChops.invert(im).point(lambda p:255 if p>60 else 0).getbbox()
 if box:
  x0,y0,x1,y1=box; box=(max(0,x0-35),max(0,y0-35),min(im.width,x1+35),min(im.height,y1+35)); im=im.crop(box)
 im.save(str(dest)+'.png',optimize=True)
 return {'name':p.stem,'source':str(p.relative_to(ROOT)),'image':str(dest.relative_to(ROOT))+'.png','size':im.size,'georeferenced':False,'crop_pixels':box}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: records=list(pool.map(render,files))
(ROOT/'derived/depth-manifest.json').write_text(json.dumps(records,indent=2))
canvas=Image.new('RGB',(1800,((len(records)+2)//3)*500),'#dedede'); d=ImageDraw.Draw(canvas)
for i,r in enumerate(records):
 im=Image.open(ROOT/r['image']); im.thumbnail((580,465)); x=(i%3)*600; y=(i//3)*500; canvas.paste(im,(x+(600-im.width)//2,y+25)); d.text((x+10,y+5),r['name'],fill='black')
canvas.save(OUT/'contact-sheet.jpg')
print(len(records),'rendered')
