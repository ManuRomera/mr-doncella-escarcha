#!/bin/bash
# Espera a que vuelva la cuota de Codex y completa: JSON pendientes → sync → arte pendiente.
# Si Codex vuelve a agotar la cuota, reintenta cada 30 min hasta que no quede nada.
W="/Volumes/Datos_Dock/FoundryVTT/Trabajo RIMA/work"; M="$(cd "$(dirname "$0")/.." && pwd)"
until [ "$(date +%H%M)" -ge 2345 ] || [ "$(date +%H)" -lt 12 ]; do sleep 60; done
while :; do
  cd "$W" && ./lanzar-json.sh >> log/json-reanudado.txt 2>&1
  cd "$M" && ./tools/sync.sh && python3 tools/gen_codex.py --jobs 3 >> art/gen3.log 2>&1 && break
  echo "cuota agotada $(date +%H:%M), reintento en 30 min" >> art/gen3.log; sleep 1800
done
python3 tools/ingest.py && python3 tools/ayudas.py && npm run -s build && python3 tools/verify.py
