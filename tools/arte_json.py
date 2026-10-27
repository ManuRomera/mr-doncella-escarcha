"""Añade a docs/arte.json lo que piden content/cap1/*.json: escenas (sin personas), PNJ y desafíos (cuerpo entero sin fondo),
fondos de ayudas (soporte vacío). No duplica ids ya presentes. Uso: python3 tools/arte_json.py"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];cfg=json.loads((ROOT/'docs/arte.json').read_text());have={i['id'] for i in cfg['imagenes']}
S="Wide 3:2 environment establishing shot, no people or characters, room in the lower third for standing figures. "
T=("Full body character illustration, head and feet fully visible with generous padding, three quarter pose, readable distinctive silhouette. ","Isolated on genuine transparent background, no floor, no scenery, no shadow.")
add=lambda i:(cfg['imagenes'].append(i),have.add(i['id'])) if i['id'] not in have else None
for f in sorted(ROOT.glob('content/cap*/*.json')):
 J=json.loads(f.read_text())
 for e in J.get('escenas',[]):add({'id':e['slug'],'tipo':'escena','size':'1536x1024','prompt':S+e['imagen_en']})
 for n in J.get('pnj',[]):add({'id':'pnj-'+n['slug'],'tipo':'token','size':'1024x1536','prompt':T[0]+n['aspecto_en']+' Cold-weather clothing for an arctic frontier town. '+T[1]})
 linked={n.get('desafio') for n in J.get('pnj',[])}
 for d in J.get('desafios',[]):
  if d['slug'] in linked:continue
  if set(d.get('roles',[]))&{'Peligro','Obstáculo'}:
   add({'id':'peligro-'+d['slug'],'tipo':'escena','size':'1024x1024','prompt':'Square vignette illustration of a hazard, no people: '+d['aspecto_en']});continue
  add({'id':'desafio-'+d['slug'],'tipo':'token','size':'1024x1536','prompt':T[0].replace('character','creature or figure')+d['aspecto_en']+' '+T[1]})
 for a in J.get('ayudas',[]):add({'id':'ayuda-'+a['slug'],'tipo':'escena','size':'1024x1536','prompt':'Top-down flat view of a blank physical document filling the frame: '+a['fondo_en']+' The central 70% must be EMPTY and clean for handwriting to be added later. Absolutely no writing, letters, runes or symbols.'})
(ROOT/'docs/arte.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=1));print(len(cfg['imagenes']),'imágenes en la lista')
