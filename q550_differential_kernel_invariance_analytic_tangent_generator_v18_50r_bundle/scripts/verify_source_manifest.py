#!/usr/bin/env python3
"""Verify immutable source archive manifest, ignoring generated runtime outputs."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'SOURCE_MANIFEST.json').read_text())
assert manifest['root']==root.name
for rel,expected in manifest['files'].items():
 path=root/rel
 if not path.is_file():raise RuntimeError('Missing source '+rel)
 with path.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
 if actual!=expected:raise RuntimeError('Source drift: '+rel)
print('v18.50r SOURCE IDENTITY VERIFIED',len(manifest['files']))
