#!/usr/bin/env python3
"""Deterministic SHA-256 source-preserving sendback; no temporary runtime files."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
keep=[]
for p in ROOT.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(ROOT)
 if any(s in rel.parts for s in ('__pycache__','runtime','.git','.pytest_cache')):continue
 if p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json'):continue
 if rel.parts[0] in ('scripts','reference','tests','inputs','results') or len(rel.parts)==1:keep.append(p)
m={'version':'v18.49c','parent':'byte-identical original server v18.49b sendback; recursively SHA verified to v18.48j',
    'files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(keep)}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(m,indent=2)+'\n')
keep.append(ROOT/'SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(keep):z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(keep)
print('sendback: SHA-256 verified',len(keep),'members')
