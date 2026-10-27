"""Descarga y prepara la banda sonora (Kevin MacLeod, CC BY 4.0) y los efectos (archivo BBC, licencia RemArc).
Bucles sin costura (solapamiento circular), -26 LUFS, Ogg Opus. Escribe content/audio.json y AUDIO-CREDITS.md."""
from pathlib import Path
import subprocess,json,hashlib,urllib.parse,urllib.request
ROOT=Path(__file__).resolve().parents[1];SRC=Path('/Volumes/Datos_Dock/FoundryVTT/Trabajo RIMA/audio/src');SRC.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'assets/audio'
# slug, nombre, título original, motivo
MUSIC=[('valle','La tundra sin sol','Long Note Four',0),('auril','La Doncella de la Escarcha','Frost Waltz',0),('lago','Los lagos helados','Winter Reflections',0),
 ('pueblo','Diez Ciudades','Thatched Villagers',0),('taberna','Junto a la lumbre','Pippin the Hunchback',0),('hidromiel','La sala del hidromiel','Master of the Feast',0),
 ('bosque','El bosque de Bosque Solitario','Dreams Become Real',0),('mina','Bajo la piedra','Dark Hallway',0),('culto','La Espada Negra','Ice Demon',0),
 ('loteria','La lotería de la luna nueva','Dark Times',0),('noche','Noche de aurora','Night Vigil',0),('camino','Por el camino helado','Lost Frontier',0),
 ('batalla','Batalla','Volatile Reaction',1),('batalla-oscura','Combate oscuro','Unholy Knight',1),('persecucion','Persecución','Prelude and Action',1),
 ('sigilo','Sigilo','Dark Walk',1),('tension','Tensión','Disquiet',1),('horror','Horror','Anguish',1),('amenaza','Amenaza creciente','Gathering Darkness',1),
 ('misterio','Misterio','Comfortable Mystery 4',1),('duelo','Duelo','Mourning Song',1),('esperanza','Esperanza','Eternal Hope',1),
 ('bestia','La bestia','Heart of the Beast',1),('ventisca-m','Ventisca','Ossuary 6 - Air',1),('heroica','Gesta heroica','Five Armies',1)]
# slug, nombre, id BBC, inicio, duración, bucle
SFX=[('ventisca','Ventisca','07054119',20,90,1),('viento','Viento ártico','07005204',10,90,1),('lago-sfx','Lago helado','NHU05073127',5,90,1),
 ('hogar','Fuego del hogar','NHU05008080',5,60,1),('taberna-sfx','Parroquianos','07047064',10,90,1),('hielo-cruje','Hielo que cruje','07071025',0,14,0),
 ('hielo-rompe','Hielo que se rompe','NHU05061138',0,25,0),('lobos','Aullido de lobos','NHU05102193',0,30,0),('campana','Campana de la lotería','07040007',0,25,0),
 ('perros','Perros de trineo','07054122',0,20,0),('cuervo','Cuervo','NHU05099195',0,12,0),('puerta','Puerta de madera','07037346',0,10,0),
 ('pasos','Pasos en la nieve','07004054',0,20,0),('chapuzon','Chapuzón en agua helada','07044109',0,8,0),('rugido','Rugido de bestia','NHU05078122',0,12,0),
 ('cuerno','Cuerno de caza','07005023',0,10,0),('pico','Picos en la mina','07054175',10,30,0),('multitud','Multitud furiosa','07039068',0,30,0),
 ('latido','Latido','07070016',0,30,0),('alas','Aleteo gigante','07042227',0,12,0),('hacha-hielo','Hacha contra el hielo','07046148',0,20,0)]
def get(url,dest):
 if not dest.exists():urllib.request.urlretrieve(url,dest)
 return dest
def probe(p):return float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(p)]))['format']['duration'])
def loop_filter(start,end,n):
 d=end-start
 return (f'[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,asplit=3[m][h][t];[m]atrim=start={n}:end={d-n},asetpts=PTS-STARTPTS[b];'
  f'[h]atrim=end={n},asetpts=PTS-STARTPTS[head];[t]atrim=start={d-n},asetpts=PTS-STARTPTS[tail];[tail][head]acrossfade=d={n}:c1=qsin:c2=qsin[s];'
  '[b][s]concat=n=2:v=0:a=1,loudnorm=I=-26:TP=-4:LRA=6,aresample=48000[a]')
def enc(src,dest,f):
 if not dest.exists():subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-filter_complex',f,'-map','[a]','-c:a','libopus','-b:a','96k',str(dest)],check=True)
def stamp(p,**kw):return dict(path=str(p.relative_to(ROOT)),seconds=round(probe(p),2),sha256=hashlib.sha256(p.read_bytes()).hexdigest()[:16],**kw)
rec=[]
for d in ['music','sfx']:(OUT/d).mkdir(parents=True,exist_ok=True)
for slug,name,title,motif in MUSIC:
 url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(title)+'.mp3'
 src=get(url,SRC/(title+'.mp3'));dur=probe(src);dest=OUT/'music'/(slug+'.ogg')
 enc(src,dest,loop_filter(4,dur-6,min(6,(dur-10)/4)))
 rec.append(stamp(dest,slug=slug,name=name,kind='music',motif=bool(motif),repeat=True,title=title,author='Kevin MacLeod',source=url,license='CC BY 4.0'))
 print(slug,flush=True)
for slug,name,bid,start,dur,loop in SFX:
 src=get(f'https://sound-effects-media.bbcrewind.co.uk/mp3/{bid}.mp3',SRC/(bid+'.mp3'));dest=OUT/'sfx'/(slug+'.ogg')
 end=min(probe(src),start+dur)
 f=loop_filter(start,end,3) if loop else f'[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={end-start-1.5}:d=1.5,loudnorm=I=-22:TP=-3,aresample=48000[a]'
 enc(src,dest,f)
 rec.append(stamp(dest,slug=slug,name=name,kind='sfx',repeat=bool(loop),title=bid,author='BBC Sound Effects',source=f'https://sound-effects.bbcrewind.co.uk/search?q={bid}',license='RemArc (uso personal, educativo o de investigación)'))
 print(slug,flush=True)
(ROOT/'content/audio.json').write_text(json.dumps(rec,ensure_ascii=False,indent=1))
t='# Créditos de audio\n\nMúsica: Kevin MacLeod (incompetech.com), licencia Creative Commons Atribución 4.0 (https://creativecommons.org/licenses/by/4.0/). Recortada, adaptada a bucle sin costura y normalizada.\n\n'
t+=''.join(f'- **{r["name"]}**: «{r["title"]}» — Kevin MacLeod.\n' for r in rec if r['kind']=='music')
t+='\nEfectos: «BBC Sound Effects» (https://sound-effects.bbcrewind.co.uk), © BBC, licencia RemArc: solo uso personal, educativo o de investigación. Por eso este módulo no se publica.\n\n'
t+=''.join(f'- **{r["name"]}**: BBC {r["title"]}.\n' for r in rec if r['kind']=='sfx')
(ROOT/'AUDIO-CREDITS.md').write_text(t);print(len(rec),'audios')
