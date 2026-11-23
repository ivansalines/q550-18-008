#!/usr/bin/env python3
"""Verify immutable sources without rejecting generated output or runtime."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'SOURCE_MANIFEST.json').read_text())
assert m['root']==root.name
for rel,digest in m['files'].items():
 p=root/rel
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
  raise RuntimeError('Source identity mismatch: '+rel)
print('v18.50q SOURCE IDENTITY VERIFIED',len(m['files']))
