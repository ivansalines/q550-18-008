#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" scripts/verify_parent.py
"$PYTHON_BIN" tests/test_gate_math.py
"$PYTHON_BIN" scripts/run_audit.py
"$PYTHON_BIN" tests/test_decision_rules.py
"$PYTHON_BIN" scripts/verify_source_manifest.py
"$PYTHON_BIN" scripts/write_output_manifest.py
printf 'v18.50k PASS: source identity, algebra, event sequence, output manifest\n'
