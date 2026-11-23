#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY="${Q550_PYTHON:-python3.13}"
command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" -m unittest discover -s tests -p 'test_*.py' -v
"$PY" scripts/run_audit.py "$@"
"$PY" scripts/check_outputs.py
"$PY" scripts/plot_results.py
"$PY" scripts/generate_report.py
"$PY" scripts/pack_sendback.py
