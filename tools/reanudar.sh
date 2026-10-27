#!/bin/bash
# Espera a que vuelva la cuota de Codex y completa: JSON pendientes → sync → arte pendiente (reanudable).
W="/Volumes/Datos_Dock/FoundryVTT/Trabajo RIMA/work"; M="$(cd "$(dirname "$0")/.." && pwd)"
until [ "$(date +%H%M)" -ge 2345 ]; do sleep 60; done
cd "$W" && ./lanzar-json.sh > log/json-reanudado.txt 2>&1
cd "$M" && ./tools/sync.sh && python3 tools/gen_codex.py --jobs 3 > art/gen3.log 2>&1
grep -c "^OK" art/gen3.log; grep -c "^ERR" art/gen3.log
