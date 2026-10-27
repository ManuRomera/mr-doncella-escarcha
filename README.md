# MR- La Rima de la Doncella de la Escarcha

Conversión **privada** de la campaña *Icewind Dale: Rime of the Frostmaiden* (D&D 5e) a **Legend in the Mist** para Foundry VTT, siguiendo la *Herramienta de conversión 5e* de Son of Oak. Uso personal: el texto de la aventura es de Wizards of the Coast y los efectos de sonido del archivo BBC solo permiten uso personal. **No publicar.**

## Qué trae (fase 1 · Cap. 1, Diez Ciudades)
- Seis héroes pregenerados de Poderío de Origen, con retrato, ficha con fondo de su origen y token de cuerpo entero sin fondo; carta de Compañía.
- Manual del Narrador por sección, lecturas por escena, PNJ y desafíos convertidos (nivel, límites, etiquetas, amenazas y consecuencias).
- Escenas ilustradas sin personajes (arte propio generado con Codex), miniaturas y escenas de las diez ciudades.
- Banda sonora (Kevin MacLeod, CC BY 4.0) con 12 piezas de escena y 13 motivos, y 21 efectos reales; bucles sin costura.
- Barra del Narrador con **MR- Dirección** (requerido): música, motivos, efectos, lecturas y figuras por escena; reloj de la Helor Eterna.
- Lotería de Auril (Configuración → MR- La Rima de la Doncella) y secretos de personaje adaptados.

## Requisitos
Foundry v13 · sistema `mist-engine-fvtt` ≥ 14.5.4 · módulo `mr-direccion` · recomendado `mr-litm-es`.

## Construir
```bash
python3 tools/audio.py        # música y efectos (descarga y bucles)
python3 tools/gen_codex.py    # arte pendiente de docs/arte.json → art/new
python3 tools/ingest.py       # art/new → assets (+ art/arte.zip)
python3 tools/ayudas.py       # ayudas con texto real
npm run build                 # content/ → _data/aventura.json → packs/ + dist/
```
Las fuentes de contenido están en `content/` (`heroes.json`, `cap1/*.json` + `cap1/*.md`, `extra/*.md`). El trabajo intermedio (texto extraído, fichas de Codex) vive en `/Volumes/Datos_Dock/FoundryVTT/Trabajo RIMA`.

Créditos de audio: [AUDIO-CREDITS.md](AUDIO-CREDITS.md).
