#!/usr/bin/env python3
"""Verify this unpacked audit against its complete SHA-256 member manifest."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'SHA256SUMS.json').read_text())
assert m['root']==ROOT.name and m['version']=='v18.50j'
expected=set(m['files'])|{'SHA256SUMS.json'}
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
if actual!=expected:raise RuntimeError(f'Files missing or unlisted: {actual^expected}')
for name,digest in m['files'].items():
    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Hash mismatch '+name)
print(f'v18.50j bundle SHA-256 verified: {len(m["files"])}/{len(m["files"])}')
