"""Revisión automática de textos (content/cap*): restos de 5e, unidades, glosario LitM y copia literal del PDF.
Uso: python3 tools/revisar.py [--detalle sección]"""
import json,re,sys,glob
from pathlib import Path
W=Path('/Volumes/Datos_Dock/FoundryVTT/Trabajo RIMA/work/fuentes')
PAT={
 '5e: prueba/salvación/CD':r'\b(prueba|tirada de salvación|salvación) de (Fuerza|Destreza|Constitución|Inteligencia|Sabiduría|Carisma)|\bCD ?\d+|\(CD',
 '5e: nivel/PG/CA':r'\bnivel \d+ o superior|\bde nivel \d|puntos de golpe|\bPG\b|\bCA ?\d|clase de armadura|\bd20\b|ventaja|desventaja',
 '5e: monedas':r'\b\d+ ?(po|pp|pc|pe|pl)\b|piezas? de (oro|plata|cobre)',
 '5e: conjuros/rasgos':r'\blanzar \w+|espacio de conjuro|conjuro de nivel|visión en la oscuridad|descanso (corto|largo)|acción adicional|reacción\b',
 'unidades en pies':r'\b\d+ pies\b|\b(treinta|veinte|diez|cien|cuarenta|cincuenta|sesenta|quince|cinco) pies\b|\bpies? (de alto|de ancho|de profundidad)',
 'apéndices/mapas 5e':r'Apéndice [A-Z]|mapa \d+\.\d+|\b[A-Z]\d+\)',
 'nota de prompt':r'Sin Héroes\.|Sin personas\.',
 'DJ/Máster':r'\b(DM|DJ|Máster|Dungeon Master|director de juego)\b',
 'personajes jugadores':r'\bpersonajes jugadores|\bPJ\b|aventureros\b',
}
def textos(J,md):
 yield 'ficha',md
 for e in J.get('escenas',[]):yield 'lectura:'+e['slug'],e.get('lectura','')+' '+e.get('notas','')
 for n in J.get('pnj',[]):yield 'pnj:'+n['slug'],' '.join(str(n.get(k,'')) for k in ['presentacion','caracter','quiere','sabe','papel'])
 for d in J.get('desafios',[]):yield 'desafio:'+d['slug'],json.dumps({k:d.get(k) for k in ['descripcion','limites','rasgos','amenazas','secretos']},ensure_ascii=False)
 for a in J.get('ayudas',[]):yield 'ayuda:'+a['slug'],a.get('texto','')
def ngr(t,n=8):
 w=re.findall(r'\w+',t.lower());return {' '.join(w[i:i+n]) for i in range(len(w)-n+1)}
det=sys.argv[2] if len(sys.argv)>2 else None;tot={}
for f in sorted(glob.glob('content/cap*/*.json')):
 sec=Path(f).stem;J=json.load(open(f));md=Path(f).with_suffix('.md').read_text()
 src=(W/(sec+'.txt')).read_text() if (W/(sec+'.txt')).exists() else '';S=ngr(src)
 hits={};cop=[]
 for where,t in textos(J,md):
  for k,p in PAT.items():
   for m in re.finditer(p,t):hits.setdefault(k,[]).append((where,t[max(0,m.start()-50):m.end()+30].replace('\n',' ')))
  if where.startswith(('lectura','ayuda')) and S:
   g=ngr(t);r=len(g&S)/max(1,len(g))
   if r>.25:cop.append((where,round(r,2)))
 tot[sec]=(sum(len(v) for v in hits.values()),len(cop))
 if det and det in sec:
  for k,v in hits.items():
   print('##',k,len(v))
   for w,c in v[:12]:print('  ',w,'|',c)
  print('## copia literal (>25 % de 8-gramas):',cop)
if not det:
 for s,(h,c) in tot.items():print(f'{s:32} restos5e={h:4} lecturas_copiadas={c}')
 print('TOTAL',sum(h for h,_ in tot.values()),sum(c for _,c in tot.values()))
