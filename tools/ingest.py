"""art/new/*.png → assets/*.webp. Escenas 1920×1080 + miniatura 400 px; tokens recortados al canal alfa;
retrato 512 sacado de la cabeza del token; hoja de héroe 1200×800. Reanudable; empaqueta art/arte.zip."""
from pathlib import Path
from PIL import Image
import sys,zipfile
ROOT=Path(__file__).resolve().parents[1];NEW=ROOT/'art/new';A=ROOT/'assets'
def save(im,p,q=84):
 p.parent.mkdir(parents=True,exist_ok=True);im.save(p,'WEBP',quality=q,method=6)
def scene(src,dest):
 im=Image.open(src).convert('RGB');w,h=im.size;nh=round(w*9/16);top=max(0,(h-nh)//2)
 im=im.crop((0,top,w,top+nh)).resize((1920,1080),Image.LANCZOS);save(im,A/'scenes'/(dest+'.webp'))
 save(im.resize((400,225),Image.LANCZOS),A/'thumbs'/(dest+'.webp'),80)
def token(src,folder,slug):
 im=Image.open(src).convert('RGBA');a=im.split()[-1].point(lambda v:255 if v>24 else 0);box=a.getbbox()
 if not box:raise SystemExit(f'{src}: sin alfa')
 fig=im.crop(box);pad=round(fig.height*.04);c=Image.new('RGBA',(fig.width+2*pad,fig.height+2*pad));c.paste(fig,(pad,pad))
 if c.height>1400:c=c.resize((round(c.width*1400/c.height),1400),Image.LANCZOS)
 save(c,A/folder/(slug+'-token.webp'),88)
 s=round(fig.width*.62);cx=fig.width//2;head=fig.crop((max(0,cx-s//2),0,max(0,cx-s//2)+s,s))
 bg=Image.new('RGBA',head.size,(30,38,54,255));bg.alpha_composite(head);save(bg.convert('RGB').resize((512,512),Image.LANCZOS),A/folder/(slug+'-portrait.webp'))
for p in sorted(NEW.glob('*.png')):
 n=p.stem
 if n.startswith('heroe-') and n.endswith('-token'):token(p,'heroes',n[6:-6])
 elif n.startswith('heroe-') and n.endswith('-hoja'):save(Image.open(p).convert('RGB').resize((1200,800),Image.LANCZOS),A/'heroes'/(n[6:-5]+'-sheet.webp'))
 elif n.startswith('pnj-'):token(p,'npc',n[4:])
 elif n.startswith('desafio-'):token(p,'challenges',n[8:])
 elif n.startswith('peligro-'):save(Image.open(p).convert('RGB').resize((768,768),Image.LANCZOS),A/'challenges'/(n[8:]+'.webp'))
 elif n.startswith('objeto-'):save(Image.open(p).convert('RGBA').resize((512,512),Image.LANCZOS),A/'objects'/(n[7:]+'.webp'))
 elif n.startswith('ayuda-'):continue  # las compone tools/ayudas.py
 else:scene(p,n)
with zipfile.ZipFile(ROOT/'art/arte.zip','w',zipfile.ZIP_STORED) as z:
 for p in sorted(NEW.glob('*.png')):z.write(p,p.name)
print(len(list(NEW.glob('*.png'))),'imágenes ingeridas')
