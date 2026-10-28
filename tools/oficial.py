"""Saca del PDF de la aventura los mapas, escudos y planos listados en content/oficial.json → assets/oficial/<nombre>.webp.
Uso: python3 tools/oficial.py"""
from pathlib import Path
import json,io,fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];PDF='/Volumes/Datos_Dock/Rol/02 Aventuras y campañas/Colección de aventuras/Dungeons & Dragons/La Rima de la Doncella de la Escarcha.pdf'
O=json.loads((ROOT/'content/oficial.json').read_text());out=ROOT/'assets/oficial';out.mkdir(exist_ok=True);d=fitz.open(PDF)
for nombre,x in O['imagenes'].items():
 im=Image.open(io.BytesIO(d.extract_image(x)['image'])).convert('RGB')
 sm=d.xref_get_key(x,'SMask')  # la transparencia va en otro objeto del PDF
 if sm[0]=='xref':
  m=Image.open(io.BytesIO(d.extract_image(int(sm[1].split()[0]))['image'])).convert('L').resize(im.size);im.putalpha(m)
 im.save(out/f'{nombre}.webp',quality=88)
print(len(O['imagenes']),'imágenes del libro')
