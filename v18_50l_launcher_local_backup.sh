#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3.13}"
"$PYTHON_BIN" tests/test_metric_and_gate.py
"$PYTHON_BIN" scripts/run_audit.py "$@"
"$PYTHON_BIN" scripts/verify_source_manifest.py
"$PYTHON_BIN" scripts/write_output_manifest.py
"$PYTHON_BIN" scripts/pack_sendback.py
printf 'v18.50l PASS: authenticated genealogy + new physical replay + output manifest\n'
