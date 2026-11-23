#!/usr/bin/env python3
"""Manifest of all reproducible genealogy members, no pycache or recursive ZIP."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R).as_posix()
 if (rel.startswith('runtime/') or rel.startswith('tests/__pycache__/') or rel.startswith('reference/__pycache__/')
     or rel.startswith('scripts/__pycache__/') or rel.endswith('.pyc')
     or rel=='sendback.zip' or rel=='SHA256SUMS_OUTPUT.json' or rel.endswith('_server.log')):continue
 files.append((rel,p))
manifest={'version':'v18.48k','archive_root':R.name,'file_count':len(files),
          'files':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files}}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for n,p in files:z.write(p,R.name+'/'+n)
 z.write(R/'SHA256SUMS_OUTPUT.json',R.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(R/'sendback.zip') as z:
 assert z.testzip() is None
print('SENDBACK',R/'sendback.zip','MANIFEST_MEMBERS',len(files))
