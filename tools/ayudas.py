"""Compone las ayudas: fondo generado (art/new/ayuda-<slug>.png, sin texto) + texto real de content/cap1/*.json → assets/handouts/<slug>.webp"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import json
ROOT=Path(__file__).resolve().parents[1];FON=ROOT/'tools/fonts'
FONT={'carta':'IMFellEnglish-Regular.ttf','libro':'IMFellEnglish-Regular.ttf','cartel':'IMFellEnglish-Regular.ttf','nota':'Caveat-Regular.ttf','mapa':'Caveat-Regular.ttf'}
def wrap(d,text,font,w):
 out=[]
 for raw in text.split('\n'):
  cur=''
  for word in raw.split():
   t=(cur+' '+word).strip()
   if d.textlength(t,font=font)<=w or not cur:cur=t
   else:out.append(cur);cur=word
  out.append(cur)
 return out
def compose(a):
 src=ROOT/f"art/new/ayuda-{a['slug']}.png"
 if not src.exists():return False
 bg=Image.open(src).convert('RGB');W,H=bg.size;x0,y0,x1,y1=[int(v) for v in (W*.17,H*.15,W*.83,H*.85)];bw,bh=x1-x0,y1-y0
 d=ImageDraw.Draw(bg);ff=FON/FONT.get(a.get('tipo'),'IMFellEnglish-Regular.ttf')
 for size in range(int(W*.05),12,-1):
  f=ImageFont.truetype(str(ff),size);tf=ImageFont.truetype(str(FON/'CinzelDecorative-Regular.ttf'),int(size*.9))
  tl=wrap(d,a['titulo'],tf,bw);lines=wrap(d,a['texto'],f,bw)
  if len(tl)*tf.size*1.3+size*.8+len(lines)*size*1.32<=bh:break
 mask=Image.new('L',bg.size,0);m=ImageDraw.Draw(mask);y=y0
 for l in tl:m.text((x0+(bw-m.textlength(l,font=tf))/2,y),l,font=tf,fill=235);y+=tf.size*1.3
 y+=size*.8
 for l in lines:m.text((x0,y),l,font=f,fill=235);y+=size*1.32
 mask=mask.filter(ImageFilter.GaussianBlur(.6));bg.paste(Image.new('RGB',bg.size,(38,30,24)),mask=mask)
 out=ROOT/f"assets/handouts/{a['slug']}.webp";out.parent.mkdir(parents=True,exist_ok=True);bg.save(out,'WEBP',quality=80,method=6);return True
n=0
O=json.loads((ROOT/'content/oficial.json').read_text());NOAYUDA=set(O['descartar'])|set(O['ayudas'])
for f in sorted(ROOT.glob('content/cap*/*.json')):
 for a in json.loads(f.read_text()).get('ayudas',[]):
  if a['slug'] not in NOAYUDA:n+=compose(a)
print(n,'ayudas compuestas')
