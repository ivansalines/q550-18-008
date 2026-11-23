#!/usr/bin/env python3
"""Verify unchanged packaged source, independent of runtime and regenerated PNGs."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'SOURCE_MANIFEST.json').read_text())
assert m['root']==R.name
for name,dig in m['files'].items():
    p=R/name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=dig:
        raise RuntimeError('Source drift: '+name)
print('v18.50o SOURCE VERIFIED',len(m['files']))
