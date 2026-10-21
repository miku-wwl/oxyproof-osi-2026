"""Private coordinate-review images from preserved IAB frames; no new actions."""
import bisect,json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'.local/cursor-review'
CASES=[('A1',4.0),('A1',4.5),('A1',6.5),('A1',9.2),('A2',1.3),('A2',3.2),('A2',3.6),('A2',5.2),('A2',7.2),('A2',16.2),('A2',17.2),('B',12.1),('B',12.8),('B',13.5),('B',17.2),('B',18.5),('C',13.1),('C',13.3),('C',13.6),('D',1.1),('D',1.3),('D',1.6),('E',12.1),('E',12.3),('E',12.6)]
def main():
    OUT.mkdir(exist_ok=True)
    contact=Image.new('RGB',(4*640,7*384),'#111418');d=ImageDraw.Draw(contact)
    for i,(take,t) in enumerate(CASES):
        folder=ROOT/'.local/browser-demo-capture'/take;m=json.loads((folder/'capture-manifest.json').read_text(encoding='utf-8'))
        f=m['frames'][max(0,bisect.bisect_right([f['t'] for f in m['frames']],t)-1)]
        with Image.open(folder/f['file']) as raw:im=ImageOps.fit(raw.crop((0,0,1749,984)),(1920,1080),Image.Resampling.LANCZOS)
        dr=ImageDraw.Draw(im)
        for e in m['events']:
            if e['kind']=='element-click' and abs(e['requested_t']-t)<.75 and e.get('point'):
                p=e['point'];x=p['x']*1920/p['width'];y=p['y']*1080/p['height']
                dr.ellipse((x-10,y-10,x+10,y+10),outline='red',width=2)
                dr.text((x+12,y),e['label'],fill='red')
        im.save(OUT/f'{take}-{t:.1f}.jpg',quality=95)
        x=i%4*640;y=i//4*384;contact.paste(im.resize((640,360)),(x,y));d.text((x+8,y+364),f'{take} {t:.1f} s / source {f["t"]:.3f}',fill='white')
    contact.save(OUT/'contact.jpg',quality=95)
    print(OUT)
if __name__=='__main__':main()
