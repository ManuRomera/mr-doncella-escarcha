"""Comprueba _data/aventura.json y content/direccion.json: IDs únicos, rutas de archivos existentes y referencias
de MR- Dirección (escenas, música, efectos, figuras, lecturas) que resuelven. Sale con 1 si hay errores."""
from pathlib import Path
import json,re,sys,collections
ROOT=Path(__file__).resolve().parents[1];MOD='mr-doncella-escarcha';PRE=f'modules/{MOD}/'
a=json.loads((ROOT/'_data/aventura.json').read_text())[0];p=json.loads((ROOT/'content/direccion.json').read_text())
err=[];warn=[]
for k in ['actors','journal','scenes','playlists','folders']:
 for i,n in collections.Counter(d['_id'] for d in a[k]).items():
  if n>1:err.append(f'{k}: _id repetido {i}')
for path in set(re.findall(r'"(modules/'+MOD+r'/[^"]+)"',json.dumps(a))):
 if not (ROOT/path[len(PRE):]).exists():err.append('falta '+path)
slug=lambda docs:{d.get('flags',{}).get(MOD,{}).get('slug') for d in docs}
scn=slug(a['scenes']);act=slug(a['actors']);snd={s['flags'][MOD]['slug'] for pl in a['playlists'] for s in pl['sounds']}
pages={(j['_id'],pg['_id']) for j in a['journal'] for pg in j['pages']}
for d in a['scenes']:
 dr=d['flags'][MOD].get('direction')
 if dr and (dr['journalId'],dr['pageId']) not in pages:err.append(f"lectura rota en {d['name']}")
for c in p['scenes']:
 if c['ref']['flag'][2] not in scn:err.append(f"escena de dirección sin escena: {c['ref']['flag'][2]}")
 for r in [c.get('music')]+[q['sound'] for q in c['cues']]:
  if r and r['flag'][2] not in snd:err.append(f"sonido inexistente {r['flag'][2]} en {c['name']}")
 for f in c['figures']:
  if f['ref']['flag'][2] not in act:warn.append(f"figura sin actor {f['ref']['flag'][2]} en {c['name']}")
for m in p['settings']['motifs']+p['settings']['effects']:
 r=m.get('music') or m.get('sound')
 if r['flag'][2] not in snd:err.append('motivo/efecto sin sonido '+m['id'])
sinimg=[d['name'] for d in a['actors'] if 'portada' in d.get('img','')]
print(f"{len(err)} errores, {len(warn)} avisos, {len(sinimg)} actores sin imagen propia")
for e in err[:40]:print('ERROR',e)
for w in warn[:15]:print('aviso',w)
sys.exit(1 if err else 0)
