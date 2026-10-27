#!/bin/bash
# Copia a content/cap1 las secciones que ya tienen ficha (.md) y JSON válido en Trabajo RIMA, y actualiza docs/arte.json
cd "$(dirname "$0")/.."; W="/Volumes/Datos_Dock/FoundryVTT/Trabajo RIMA/work"
for j in "$W"/json/*.json; do s=$(basename "$j" .json)
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));assert d.get('escenas') and all(0<len(x.get('slug',''))<=60 for k in ['escenas','pnj','desafios','ayudas'] for x in d.get(k,[]))" "$j" 2>/dev/null && [ -s "$W/digest/$s.md" ] && cp "$j" "$W/digest/$s.md" content/cap1/
done; ls content/cap1 | wc -l; python3 tools/arte_json.py
