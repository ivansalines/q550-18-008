#!/usr/bin/env python3
"""Reproducible complete runnable sendback with original parent source pinning."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
allowed=('inputs/','reference/','scripts/','results/','tests/')
files=[]
for p in ROOT.rglob('*'):
    if not p.is_file():continue
    name=p.relative_to(ROOT).as_posix()
    if name in ('sendback.zip','SHA256SUMS_OUTPUT.json') or '__pycache__' in p.parts:continue
    if any(t in p.parts for t in ('runtime','.git')):continue
    if name in ('README.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh') or name.startswith(allowed):
        files.append(p)
manifest={'version':'v18.48z','historical_parent':'user server Y exact bytes, recursively authenticated',
          'files':{p.relative_to(ROOT).as_posix():digest(p) for p in sorted(files)}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(ROOT/'SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
    for f in sorted(files):z.write(f,arcname=ROOT.name+'/'+f.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
    assert z.testzip() is None
    assert len([a for a in z.namelist() if not a.endswith('/')])==len(files)
print(f'Packed {len(files)} exact files into {ROOT/"sendback.zip"}')
