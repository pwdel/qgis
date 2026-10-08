from pathlib import Path
from PIL import Image,ImageDraw
import json
Image.MAX_IMAGE_PIXELS=None
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'derived/depth-panels';OUT.mkdir(exist_ok=True)
# Crop coordinates relative to whitespace-trimmed sheet (before optional CCW rotation).
settings={
 'hungry-jack':('hungry-jack-b0532010',(0.015,.24,.985,.66),0,'See contour labels'),
 'moss':('moss-c0310010',(.17,.10,.89,.40),0,'10 ft'),
 'duncan':('duncan-b0081010',(.01,.14,.86,.915),0,'10 ft'),
 'rose':('rose-b0093010',(.01,.175,.995,.84),0,'See contour labels'),
 'rove':('rove-c0334010',(.17,.235,.89,.39),0,'5 ft'),
 'mountain':('mountain-b0427010',(.46,.005,.87,.995),90,'20 ft'),
 'clearwater':('clearwater-b0076010',(.07,.028,.91,.982),90,'10 ft'),
 'west-pike':('west-pike-b0353010',(.025,.14,.98,.45),0,'10 ft'),
 'east-pike':('east-pike-b0412010',(.045,.025,.785,.85),0,'See contour labels'),
 'pine':('pine-b0090010',(.005,.315,.99,.57),0,'See contour labels'),
 'caribou':('caribou-c0238010',(.045,.12,.995,.53),0,'10 ft'),
 'little-caribou':('little-caribou-c0359010',(.44,.125,.91,.385),0,'5 ft')}
records=[]
for lake,(stem,box,rotation,interval) in settings.items():
 im=Image.open(ROOT/'derived/depth-scans'/f'{stem}.png'); crop=tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box));im=im.crop(crop)
 if rotation: im=im.rotate(rotation,expand=True)
 im.save(OUT/f'{lake}.png',dpi=(300,300),optimize=True)
 records.append({'lake':lake,'image':f'derived/depth-panels/{lake}.png','source':f'sources/depth-scans/{stem}.pdf','dimensions':im.size,'depth_units':'feet','contour_interval':interval,'georeferenced':False,'crop_fraction':box,'rotation_counterclockwise_degrees':rotation,'caption':'Historic Minnesota DNR depth scan; depths in feet. Independent inset, not georeferenced.'})
metadata=json.loads((ROOT/'sources/depth-selected-metadata.json').read_text())
for record in records: record.update(metadata[record['lake']])
(ROOT/'derived/depth-panels.json').write_text(json.dumps(records,indent=2))
canvas=Image.new('RGB',(1800,1600),'#e3e7e9');d=ImageDraw.Draw(canvas)
for i,r in enumerate(records):
 im=Image.open(ROOT/r['image']);im.thumbnail((580,365));x=(i%3)*600;y=(i//3)*400;canvas.paste(im,(x+(600-im.width)//2,y+25));d.text((x+10,y+5),r['lake']+' / '+r['contour_interval'],fill='black')
canvas.save(OUT/'contact-sheet.jpg')
