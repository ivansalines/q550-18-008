#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${Q550_PYTHON:-python3}"
"$PYTHON" tests/test_derivatives.py
"$PYTHON" scripts/run_audit.py
"$PYTHON" tests/test_audit_rules.py
"$PYTHON" scripts/verify_bundle.py
