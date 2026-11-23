#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'SOURCE_MANIFEST.json').read_text())
assert manifest['root']==root.name and manifest['version']=='v18.50n'
for name,digest in manifest['files'].items():
    target=root/name
    if not target.is_file():raise RuntimeError('Missing immutable source: '+name)
    actual=hashlib.sha256(target.read_bytes()).hexdigest()
    if actual!=digest:raise RuntimeError('Source drift: '+name)
print('v18.50n immutable sources VERIFIED',len(manifest['files']))
