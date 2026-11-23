#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
M=json.loads((R/'SOURCE_MANIFEST.json').read_text())
assert M['version']=='v18.50l' and M['root']==R.name
for file,digest in M['files'].items():
    p=R/file
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise RuntimeError('Source drift: '+file)
print('SOURCE IDENTITY VERIFIED',len(M['files']),flush=True)
