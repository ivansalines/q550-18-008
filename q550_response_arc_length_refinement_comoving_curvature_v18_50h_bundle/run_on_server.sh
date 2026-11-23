#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY="${Q550_PYTHON:-python3.13}"
command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" -m unittest discover -s tests -v
"$PY" scripts/run_audit.py "$@"
if [[ $# -eq 0 ]]; then
  "$PY" scripts/early_zoom.py
fi
"$PY" scripts/pack_sendback.py
