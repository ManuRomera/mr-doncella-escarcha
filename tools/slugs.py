"""Deja en ASCII los slugs de content/cap*/*.json, los ids de docs/arte.json y los nombres de archivo de art/new y assets
(Codex a veces escribe «bandada-arpías»; Foundry y el zip se llevan mal con esas rutas). Idempotente; lo llama sync.sh."""
from pathlib import Path
import json, unicodedata
ROOT = Path(__file__).resolve().parents[1]
asc = lambda s: unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode() if isinstance(s, str) else s

for f in ROOT.glob('content/cap*/*.json'):
    J = json.loads(f.read_text()); old = json.dumps(J, ensure_ascii=False)
    for k in ['escenas', 'pnj', 'desafios', 'ayudas', 'objetos']:
        for x in J.get(k, []):
            x['slug'] = asc(x.get('slug', ''))
            if x.get('desafio'): x['desafio'] = asc(x['desafio'])
            if 'figuras' in x: x['figuras'] = [asc(s) for s in x['figuras']]
    if json.dumps(J, ensure_ascii=False) != old: f.write_text(json.dumps(J, ensure_ascii=False, indent=1))

p = ROOT / 'docs/arte.json'; cfg = json.loads(p.read_text()); seen = set(); out = []
for i in cfg['imagenes']:
    i['id'] = asc(i['id'])
    if i['id'] not in seen: seen.add(i['id']); out.append(i)
cfg['imagenes'] = out; p.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))

n = 0
for d in [ROOT / 'art/new', *(ROOT / 'assets').iterdir()]:
    if not d.is_dir(): continue
    for f in list(d.iterdir()):
        a = asc(unicodedata.normalize('NFC', f.name))
        if a != f.name and not f.name.isascii():
            t = f.with_name(a)
            if t.exists(): f.unlink()
            else: f.rename(t)
            n += 1
print(f'slugs en ASCII; {n} archivos renombrados')
