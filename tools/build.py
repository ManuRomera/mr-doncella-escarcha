"""Fuentes de content/ → _data/aventura.json (un Adventure) + content/direccion.json (paquete de MR- Dirección).
Uso: python3 tools/build.py && node tools/build.mjs"""
from pathlib import Path
import json,hashlib,html,re,markdown
ROOT=Path(__file__).resolve().parents[1];MOD='mr-doncella-escarcha';PRE=f'modules/{MOD}/'
uid=lambda s:hashlib.sha256(s.encode()).hexdigest()[:16]
esc=html.escape
def has(p):return (ROOT/p).exists()
def asset(p,fallback):return PRE+(p if has(p) else fallback)
def fl(slug,**kw):return {MOD:{'slug':slug,**kw}}
def marks(h):
 # Mismo HTML que textWithTags del sistema Mist: [etiqueta] y [estado-n] arrastrables a fichas y tiradas
 def one(m):
  t=m[1].strip();mm=re.match(r'^(.*?)-(\d)$',t)
  if mm:return f'<mark class="draggable status" draggable="true" data-type="status" data-name="{mm[1]}" data-value="{mm[2]}">{t}</mark>'
  return f'<mark class="draggable tag" draggable="true" data-type="tag" data-name="{t}">{t}</mark>'
 return re.sub(r'(?<![@\w])\[([^\[\]<>]{1,60})\](?![({])',one,h)
def md(t):return marks(markdown.markdown(t,extensions=['tables','sane_lists']))
def tag(name,status=False,value=0):
 m=[i<value for i in range(6)]
 return {'name':name,'value':value,'isStatus':status,'burned':False,'toBurn':False,'selected':False,'positive':True,'markings':m,'might':0,'mightIcon':''}
def tags(lst):
 out=[]
 for t in lst:
  t=t.strip('[] ');mm=re.match(r'^(.*?)-(\d)$',t)
  out.append(tag(mm[1],True,int(mm[2])) if mm else tag(t))
 return out
PT=lambda n:{'name':n,'question':'','burned':False,'toBurn':False,'planned':False,'selected':False,'expiring':False,'expired':False}
SI=[{'name':'','active':False,'description':''}]*5
# Carpetas: tipo › capítulo › sección (ciudad o lugar) › Gentes/Desafíos. MR- Dirección agrupa su menú de escenas por estas carpetas.
folders={}
def fold(key,name,typ,parent=None,sort=0):
 if key not in folders:folders[key]={'_id':uid('folder/'+key),'name':name,'type':typ,'sorting':'m','sort':sort,'color':'#3d5a73','folder':folders[parent]['_id'] if parent else None,'flags':fl('folder-'+key)}
 return key
for k,n,t in [('heroes','Héroes y Compañía','Actor'),('guias','Guías y reglas','JournalEntry'),('rutinas','Rutinas','Item')]:fold(k,n,t)
F=lambda k:folders[k]['_id']
actors=[];journals=[];scenes=[];items=[];direction=[]
# ---------- Héroes y compañía ----------
H=json.loads((ROOT/'content/heroes.json').read_text())
MIGHT={'origen':'litm-origin','aventura':'litm-adventure','grandeza':'litm-greatness'}
comp=H['compania'];comp_id=uid('fellowship')
actors.append({'_id':comp_id,'name':comp['name'],'type':'litm-fellowship-themecard','img':asset('assets/scenes/portada.webp','assets/scenes/portada.webp'),'folder':F('heroes'),
 'system':{'biography':comp['bio'],'type':'litm-origin','quest':comp['quest'],'powertags':[PT(x) for x in comp['powertags']],'weaknesstags':[PT(x) for x in comp['weaknesstags']],'specialImprovements':SI,
  'notes':'<p>Etiquetas de Compañía: de un solo uso según las reglas; recuperadlas en el descanso en el campamento.</p>'},'ownership':{'default':3},'flags':fl('compania')})
for h in H['heroes']:
 s=h['slug'];its=[]
 for i,t in enumerate(h['temas']):
  its.append({'_id':uid(f'{s}/tema/{i}'),'name':t['nombre'],'type':'themebook','sort':i*1000,'system':{'description':'','type':MIGHT[t['poderio']],'color':MIGHT[t['poderio']],
   'quest':t['gesta'],'story':t['tipo'],'tabCategory':'main','abandon':0,'improve':0,'milestone':0,'themeKitUUID':'','options':{'isStoryTheme':False},
   'powertags':[PT(x) for x in ([t['titulo']] if t['titulo'] else [])+t['poder']],'weaknesstags':[PT(t['debilidad'])],'specialImprovements':SI}})
 its.append({'_id':uid(f'{s}/mochila'),'name':f"Mochila de {h['name'].split()[0]}",'type':'backpack','system':{'items':[PT(x) for x in h['mochila']]}})
 for r in h['rutinas']:
  its.append({'_id':uid(f"{s}/rutina/{r['name']}"),'name':r['name'],'type':'rote','system':{'practitioners':h['name'],'actionType':r['tipo'],'powertags':[],'weaknesstags':[],'success':f"<p>{esc(r['exito'])}</p>",'consequences':f"<p>{esc(r['consecuencias'])}</p>"}})
 bio=(f"<h3>Primera impresión</h3><blockquote><p>{esc(h['intro'])}</p></blockquote><h3>Historia</h3><p>{esc(h['historia'])}</p>"
  f"<h3>Tu conflicto</h3><p>{esc(h['conflicto'])}</p><h3>Pregunta de creación</h3><p>{esc(h['pregunta'])}</p>"+(f"<h3>Libro de conjuros</h3><p>{esc(h['libro'])}</p>" if h.get('libro') else ''))
 actors.append({'_id':uid('heroe/'+s),'name':h['name'],'type':'litm-character','folder':F('heroes'),'img':PRE+f'assets/heroes/{s}-portrait.webp','items':its,
  'system':{'biography':bio,'editMode':False,'shortDescription':f"{h['epiteto']} · {h['short']}",'customBackground':PRE+f'assets/heroes/{s}-sheet.webp','customFontColor':'#f4efe6',
   'notes':f"<h3>Tu secreto · compártelo solo si tú decides</h3><p>{esc(h['secreto'])}</p>",'promises':0,'actorSharedSingleThemecardId':comp_id,'fellowships':[],'cardLayout':[]},
  'prototypeToken':{'name':h['name'],'actorLink':True,'disposition':1,'lockRotation':True,'texture':{'src':PRE+f'assets/heroes/{s}-token.webp'},'width':round(3*h.get('tokenScale',1),2),'height':round(3*h.get('tokenScale',1),2)},
  'ownership':{'default':0},'flags':fl(s,tipo='heroe')})
# ---------- Secciones del capítulo 1 ----------
TOWN_NAMES={'bryn-shander':'Bryn Shander','targos':'Targos','bremen':'Bremen','termalaine':'Termalaine','lonelywood':'Bosque Solitario','caer-konig':'Caer-Konig','caer-dineval':'Caer-Dineval','easthaven':'Puerto Este','buenaguamiel':'Buenaguamiel','refugio-dougan':'Refugio de Dougan'}
seen=set();alias={};byname={}
def npc_actor(d,kind,sec):
 s=d['slug'];nm=d['nombre'].lower()
 if s in seen or nm in seen:
  if nm in byname and s!=byname[nm]:alias[s]=byname[nm]
  return
 seen.update({s,nm});byname[nm]=s;folder=CUR[kind];base='assets/challenges' if kind=='desafio' else 'assets/npc'
 ch=d.get('_desafio') or (d if kind=='desafio' else None)
 bio=''
 if d.get('presentacion'):bio+=f"<h3>Primera impresión</h3><blockquote><p>{esc(d['presentacion'])}</p></blockquote>"
 for k,lab in [('papel','Papel'),('descripcion','Descripción'),('caracter','Carácter y voz'),('quiere','Quiere'),('sabe','Sabe')]:
  if d.get(k):bio+=f"<h3>{lab}</h3><p>{esc(d[k])}</p>"
 sysd={'biography':bio,'shortDescription':d.get('papel',''),'editMode':False,'difficulty':1,'roles':[],'mightyAspects':[],'limits':[],'secrets':[],'specialFeatures':[],'threatsAndConsequences':[],'floatingTagsAndStatuses':[]}
 if ch:
  sysd.update(difficulty=int(ch.get('nivel',1)),roles=ch.get('roles',[]),
   mightyAspects=[{'level':m['nivel'],'aspect':m['aspecto'],'mightIcon':m['nivel']} for m in ch.get('poderio',[])],
   limits=[{'name':l['nombre'],'value':str(l['valor']),'consequence':l.get('consecuencia','')} for l in ch.get('limites',[])],
   secrets=[{'name':x['nombre'],'description':x['descripcion']} for x in ch.get('secretos',[])],
   specialFeatures=[{'name':x['nombre'],'description':x['descripcion']} for x in ch.get('rasgos',[])],
   threatsAndConsequences=[{'name':x['nombre'],'description':x.get('descripcion',''),'list':x.get('consecuencias',[])} for x in ch.get('amenazas',[])],
   floatingTagsAndStatuses=tags([t for t in ch.get('etiquetas',[]) if not re.search(r'-\d$',t.strip('[] '))]))  # los estados se aplican jugando
  if kind=='desafio' and ch.get('descripcion') and not d.get('presentacion'):sysd['biography']=f"<p>{esc(ch['descripcion'])}</p>"
 tok=asset(f'{base}/{s}-token.webp','assets/scenes/portada.webp')
 if kind=='desafio' and not has(f'{base}/{s}-token.webp'):tok=asset(f'{base}/{s}.webp','assets/scenes/portada.webp')
 actors.append({'_id':uid('actor/'+s),'name':d['nombre'],'type':'litm-npc','folder':F(folder),'img':asset(f'{base}/{s}-portrait.webp',f'{base}/{s}.webp' if has(f'{base}/{s}.webp') else 'assets/scenes/portada.webp'),'system':sysd,
  'prototypeToken':{'name':d['nombre'],'actorLink':kind=='pnj','disposition':0 if kind=='pnj' else -1,'lockRotation':True,'texture':{'src':tok},'width':3,'height':3},
  'ownership':{'default':0},'flags':fl(s,tipo=kind,seccion=sec)})
order=0;hitos=[];relojes=[];vistas=set()  # slugs de escena ya usados: la misma escena puede salir en dos secciones
CAPS={'cap1':'Cap. 1 · Diez Ciudades','cap2':'Cap. 2 · El Valle del Viento Helado','cap3':'Cap. 3 · Sol Marchito','cap4':'Cap. 4 · La Luz de la Destrucción','cap5':'Cap. 5 · La Morada de Auril','cap6':'Cap. 6 · Las Cavernas del Hambre','cap7':'Cap. 7 · La Perdición de Ythryn'}
TOWN_SEC={'bremen':'04-bremen','bryn-shander':'05-bryn-shander','caer-dineval':'06-caer-dineval','caer-konig':'07-caer-konig','refugio-dougan':'08-refugio-dougan',
 'easthaven':'09-puerto-este','buenaguamiel':'10-buenaguamiel','lonelywood':'11-bosque-solitario','targos':'12-targos','termalaine':'13-termalaine'}
def town_scene(s,folder):
 # Fondo general de la ciudad para visitas libres: primera escena de su sección
 global order
 if not has(f'assets/scenes/ciudad-{s}.webp'):return
 n=TOWN_NAMES[s]
 scenes.append({'_id':uid('scene/ciudad-'+s),'name':n,'folder':F(folder),'width':1920,'height':1080,'padding':0,'grid':{'type':0,'size':100},'background':{'src':PRE+f'assets/scenes/ciudad-{s}.webp'},
  'thumb':PRE+f'assets/thumbs/ciudad-{s}.webp','tokenVision':False,'fog':{'exploration':False},'navigation':False,'sort':order,'flags':fl('ciudad-'+s)})
 direction.append({'ref':{'flag':[MOD,'slug','ciudad-'+s]},'order':order,'name':n,'reading':None,'music':{'flag':[MOD,'slug','pueblo']},'motifs':None,
  'cues':[{'label':'','icon':'wave-square','sound':{'flag':[MOD,'slug',x]}} for x in ['viento','campana','perros']],'ambient':'dim','figures':[],'handouts':[],'notes':'','thumb':PRE+f'assets/thumbs/ciudad-{s}.webp'})
 order+=1
CUR={}
for src in sorted(ROOT.glob('content/cap*/*.json')):
 cap=src.parent.name;nc=int(cap[3:]);sec=src.stem;ns=int(sec.split('-')[0]);J=json.loads(src.read_text());title=J.get('titulo',sec)
 sa=fold(f'actor/{sec}',title,'Actor',fold(f'actor/{cap}',CAPS[cap],'Actor',sort=nc),ns)
 CUR={'pnj':fold(f'actor/{sec}/pnj','Gentes','Actor',sa,1),'desafio':fold(f'actor/{sec}/desafios','Desafíos','Actor',sa,2)}
 fe=fold(f'scene/{sec}',title,'Scene',fold(f'scene/{cap}',CAPS[cap],'Scene',sort=nc),ns)
 jc=fold(f'journal/{cap}',CAPS[cap],'JournalEntry',sort=nc)
 fm,flec,fay=(fold(f'journal/{cap}/{k}',n,'JournalEntry',jc,i) for i,(k,n) in enumerate([('manual','Manual del Narrador'),('lecturas','Lecturas de escena'),('ayudas','Ayudas para los jugadores')]))
 d0=len(direction)
 for t,ts in TOWN_SEC.items():
  if ts==sec:town_scene(t,fe)
 # Manual del Narrador: la ficha .md partida por «## »
 mdp=src.with_suffix('.md');pages=[]
 if mdp.exists():
  parts=re.split(r'^## ',mdp.read_text(),flags=re.M)
  for i,p in enumerate(parts[1:]):
   head,_,body=p.partition('\n')
   if head.strip().lower().startswith('páginas de la fuente'):continue
   pages.append({'_id':uid(f'manual/{sec}/{i}'),'name':head.strip(),'type':'text','sort':i*1000,'title':{'show':True,'level':1},'text':{'format':1,'content':md(body)}})
 journals.append({'_id':uid('manual/'+sec),'name':title,'folder':F(fm),'pages':pages,'ownership':{'default':0},'flags':fl('manual-'+sec)})
 dmap={d['slug']:d for d in J.get('desafios',[])}
 hitos+=[{'id':uid(f'hito/{sec}/{h}')[:10],'label':f"{title}: {h.split(':')[0].strip()}"} for h in J.get('hitos',[]) if isinstance(h,str)]
 relojes+=[{'id':uid(f"reloj/{sec}/{r['nombre']}")[:10],'label':r['nombre'],'segments':max(2,min(12,int(r.get('segmentos',4))))} for r in J.get('relojes',[]) if isinstance(r,dict) and r.get('nombre')]
 for n in J.get('pnj',[]):
  if n.get('desafio') in dmap:n['_desafio']=dmap[n['desafio']];alias[n['desafio']]=n['slug']
  npc_actor(n,'pnj',sec)
 linked={n.get('desafio') for n in J.get('pnj',[])}
 for d in J.get('desafios',[]):
  if d['slug'] not in linked:npc_actor(d,'desafio',sec)
 # Lecturas: un diario por sección, una página por escena
 lect=[]
 for i,e in enumerate(J.get('escenas',[])):
  img=e['slug']
  if img in vistas:e['slug']=f"{img}-{sec[:2]}"
  vistas.add(e['slug'])
  body=(f"<blockquote><p>{esc(e['lectura'])}</p></blockquote><h3>Para el Narrador</h3><p>{esc(e.get('notas',''))}</p>"
   +(f"<p><strong>Etiquetas de escena:</strong> {marks(', '.join('['+esc(t)+']' for t in e.get('etiquetas',[])))}</p>" if e.get('etiquetas') else ''))
  body=marks(body)
  pid=uid(f'lectura/{sec}/{e["slug"]}');lect.append({'_id':pid,'name':e['nombre'],'type':'text','sort':i*1000,'title':{'show':True,'level':1},'text':{'format':1,'content':body}})
  jid=uid('lecturas/'+sec);bg=asset(f"assets/scenes/{img}.webp",f"assets/scenes/ciudad-{e.get('ciudad')}.webp" if has(f"assets/scenes/ciudad-{e.get('ciudad')}.webp") else 'assets/scenes/portada.webp')
  th=bg.replace('/scenes/','/thumbs/')
  scenes.append({'_id':uid('scene/'+e['slug']),'name':e['nombre'],'folder':F(fe),'width':1920,'height':1080,'padding':0,'grid':{'type':0,'size':100},'background':{'src':bg},'thumb':th,
   'tokenVision':False,'fog':{'exploration':False},'navigation':False,'sort':order,'flags':{MOD:{'slug':e['slug'],'seccion':sec,'direction':{'journalId':jid,'pageId':pid}}}})
  direction.append({'ref':{'flag':[MOD,'slug',e['slug']]},'order':order,'name':e['nombre'],'reading':{'sceneFlag':[MOD,'direction']},
   'music':{'flag':[MOD,'slug',e.get('musica','valle')]},'motifs':e.get('motivos') or None,
   'cues':[{'label':'','icon':'wave-square','sound':{'flag':[MOD,'slug',x]}} for x in e.get('efectos',[])],
   'ambient':e.get('ambiente'),'figures':[{'ref':{'flag':[MOD,'slug',alias.get(f,f)]},'label':''} for f in dict.fromkeys(e.get('figuras',[]))],'handouts':[],'notes':e.get('notas',''),'thumb':th})
  order+=1
 if lect:journals.append({'_id':uid('lecturas/'+sec),'name':'Lecturas · '+title,'folder':F(flec),'pages':lect,'ownership':{'default':0},'flags':fl('lecturas-'+sec)})
 for a in J.get('ayudas',[]):
  if 'ayuda/'+a['slug'] in seen:continue
  seen.add('ayuda/'+a['slug'])
  pg=([{'_id':uid('ayuda-img/'+a['slug']),'name':a['titulo'],'type':'image','src':PRE+f"assets/handouts/{a['slug']}.webp",'sort':0}] if has(f"assets/handouts/{a['slug']}.webp") else [])
  pg.append({'_id':uid('ayuda/'+a['slug']),'name':a['titulo']+' (texto)','type':'text','sort':1000,'text':{'format':1,'content':''.join(f'<p>{esc(x)}</p>' for x in a['texto'].split('\n') if x.strip())}})
  journals.append({'_id':uid('ayuda/'+a['slug']),'name':'Ayuda · '+a['titulo'],'folder':F(fold(f'journal/{sec}/ayudas',title,'JournalEntry',fay,ns)),'pages':pg,'ownership':{'default':0},'flags':fl(a['slug'],seccion=sec)})
 # Las ayudas de la sección, a mano en el menú «Ayudas» de cada escena de la barra
 for d in direction[d0:]:d['handouts']=[{'ref':{'flag':[MOD,'slug',a['slug']]},'label':a['titulo']} for a in J.get('ayudas',[])]
# Diarios propios (content/extra/*.md: «# título», páginas por «## »)
for src in sorted((ROOT/'content/extra').glob('*.md')):
 t=src.read_text();title=re.search(r'^# (.+)$',t,re.M)[1];parts=re.split(r'^## ',t,flags=re.M)[1:]
 pages=[{'_id':uid(f'extra/{src.stem}/{i}'),'name':p.partition('\n')[0].strip(),'type':'text','sort':i*1000,'title':{'show':True,'level':1},'text':{'format':1,'content':md(p.partition('\n')[2])}} for i,p in enumerate(parts)]
 journals.append({'_id':uid('extra/'+src.stem),'name':title,'folder':F('guias'),'pages':pages,'ownership':{'default':2 if 'heroes' in src.stem else 0},'flags':fl('extra-'+src.stem)})
# ---------- Audio ----------
A=json.loads((ROOT/'content/audio.json').read_text())
def pl(name,key,lst,mode):
 return {'_id':uid('playlist/'+key),'name':name,'mode':mode,'sorting':'m','fade':None,'flags':fl('playlist-'+key),
  'sounds':[{'_id':uid('sound/'+a['slug']),'name':a['name'],'path':PRE+a['path'],'repeat':a['repeat'],'volume':0.5 if a['kind']=='music' else 0.6,'sort':i*100,'flags':fl(a['slug'])} for i,a in enumerate(lst)]}
playlists=[pl('Rima · Banda sonora','musica',[a for a in A if a['kind']=='music' and not a['motif']],-1),pl('Rima · Motivos','motivos',[a for a in A if a.get('motif')],-1),pl('Rima · Efectos','efectos',[a for a in A if a['kind']=='sfx'],-1)]
# ---------- Paquete de dirección ----------
motifs=[{'id':a['slug'],'label':a['name'],'icon':'music','music':{'flag':[MOD,'slug',a['slug']]}} for a in A if a.get('motif')]
pack={'schema':1,'id':MOD,'title':'MR- La Rima de la Doncella de la Escarcha','version':json.loads((ROOT/'module.json').read_text())['version'],'author':'Manu Romera','license':'Uso privado',
 'settings':{'fade':3.5,'motifs':motifs,'effects':[{'id':x,'label':n,'icon':i,'sound':{'flag':[MOD,'slug',x]}} for x,n,i in [('ventisca','Ventisca','snowflake'),('campana','Campana','bell'),('lobos','Lobos','paw')]],
  'markers':{'milestones':hitos,'clocks':[{'id':'helor','label':'La Helor Eterna (próxima luna nueva)','segments':6}]+relojes}},'scenes':direction}
(ROOT/'content/direccion.json').write_text(json.dumps(pack,ensure_ascii=False,indent=1))
# Fuera carpetas vacías (secciones sin Gentes o sin Desafíos)
usado={d.get('folder') for d in actors+journals+scenes+items}
while (vac:=[k for k,f in folders.items() if f['_id'] not in usado and not any(g.get('folder')==f['_id'] for g in folders.values())]):
 for k in vac:del folders[k]
adv={'_id':uid('adventure'),'name':'MR- La Rima de la Doncella de la Escarcha','img':PRE+'assets/scenes/portada.webp',
 'description':'<p>Campaña de horror invernal para <em>Legend in the Mist</em>: seis héroes pregenerados, las Diez Ciudades y sus misiones, desafíos convertidos, lecturas por escena, música y efectos. La barra de MR- Dirección se configura sola.</p>',
 'actors':actors,'items':items,'journal':journals,'scenes':scenes,'macros':[],'folders':list(folders.values()),'playlists':playlists,'tables':[],'cards':[],'flags':fl('aventura')}
(ROOT/'_data').mkdir(exist_ok=True);(ROOT/'_data/aventura.json').write_text(json.dumps([adv],ensure_ascii=False,indent=1))
print(json.dumps({'actores':len(actors),'diarios':len(journals),'escenas':len(scenes),'sonidos':sum(len(p['sounds']) for p in playlists)}))
