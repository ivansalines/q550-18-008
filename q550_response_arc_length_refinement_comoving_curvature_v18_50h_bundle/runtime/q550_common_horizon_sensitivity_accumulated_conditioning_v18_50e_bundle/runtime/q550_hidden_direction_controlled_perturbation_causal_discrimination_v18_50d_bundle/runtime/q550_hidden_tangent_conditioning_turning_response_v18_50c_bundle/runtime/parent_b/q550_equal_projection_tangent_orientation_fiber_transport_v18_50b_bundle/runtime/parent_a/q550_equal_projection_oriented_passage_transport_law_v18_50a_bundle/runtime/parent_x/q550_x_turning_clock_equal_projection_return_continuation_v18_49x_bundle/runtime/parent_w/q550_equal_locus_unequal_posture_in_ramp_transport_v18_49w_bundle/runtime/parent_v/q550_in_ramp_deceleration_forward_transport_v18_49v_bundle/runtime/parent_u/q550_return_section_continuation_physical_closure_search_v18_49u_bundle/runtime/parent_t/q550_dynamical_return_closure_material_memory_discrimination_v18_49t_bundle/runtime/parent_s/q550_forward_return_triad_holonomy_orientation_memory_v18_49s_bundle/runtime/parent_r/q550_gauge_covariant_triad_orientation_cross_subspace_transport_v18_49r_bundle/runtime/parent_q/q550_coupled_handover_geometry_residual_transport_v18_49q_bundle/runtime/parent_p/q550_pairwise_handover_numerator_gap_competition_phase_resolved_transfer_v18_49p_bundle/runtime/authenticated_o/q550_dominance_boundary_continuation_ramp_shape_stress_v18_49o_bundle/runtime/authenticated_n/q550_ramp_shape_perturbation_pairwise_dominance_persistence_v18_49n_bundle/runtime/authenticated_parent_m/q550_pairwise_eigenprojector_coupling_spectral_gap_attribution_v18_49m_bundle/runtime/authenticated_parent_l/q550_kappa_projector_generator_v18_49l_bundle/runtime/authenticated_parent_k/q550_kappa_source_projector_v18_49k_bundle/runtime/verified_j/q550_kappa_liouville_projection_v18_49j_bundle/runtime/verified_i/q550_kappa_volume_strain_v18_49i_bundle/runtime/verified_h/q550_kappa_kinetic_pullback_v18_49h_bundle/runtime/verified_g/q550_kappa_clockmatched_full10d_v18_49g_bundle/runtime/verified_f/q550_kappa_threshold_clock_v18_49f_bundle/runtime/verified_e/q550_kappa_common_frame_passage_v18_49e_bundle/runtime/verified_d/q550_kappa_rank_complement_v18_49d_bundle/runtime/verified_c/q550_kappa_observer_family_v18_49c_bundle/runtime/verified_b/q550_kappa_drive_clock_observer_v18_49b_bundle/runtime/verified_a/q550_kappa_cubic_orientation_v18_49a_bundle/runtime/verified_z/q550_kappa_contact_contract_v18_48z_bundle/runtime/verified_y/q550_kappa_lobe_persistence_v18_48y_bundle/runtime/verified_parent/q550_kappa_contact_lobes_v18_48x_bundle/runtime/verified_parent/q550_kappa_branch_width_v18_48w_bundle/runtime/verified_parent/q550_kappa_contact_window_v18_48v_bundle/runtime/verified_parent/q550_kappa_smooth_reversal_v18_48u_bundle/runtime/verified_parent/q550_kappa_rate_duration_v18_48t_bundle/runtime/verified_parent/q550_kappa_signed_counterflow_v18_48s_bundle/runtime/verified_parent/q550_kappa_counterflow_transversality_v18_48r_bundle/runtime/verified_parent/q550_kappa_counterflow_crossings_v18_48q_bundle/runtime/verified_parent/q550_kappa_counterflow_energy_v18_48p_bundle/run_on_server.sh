#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PY="${Q550_PYTHON:-python3.13}"
"$PY" -c 'import numpy,scipy,matplotlib' || { echo 'Required Python dependencies missing' >&2; exit 2; }
"$PY" -m unittest discover -s tests -v
"$PY" scripts/run_audit.py "$@"
"$PY" scripts/plot_results.py
"$PY" scripts/pack_sendback.py
