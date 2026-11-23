#!/usr/bin/env python3
"""Deterministic archive membership with actual-file SHA256 hashes."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
keep=[]
for p in ROOT.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(ROOT);parts=rel.parts
 if any(x in parts for x in ('runtime','__pycache__','.git','.pytest_cache')):continue
 if p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json'):continue
 if parts[0] in ('inputs','reference','scripts','tests','results') or len(parts)==1:
  keep.append(p)
manifest={'version':'v18.49b','source':'byte-identical original user 49a sendback; SHA-verified nested genealogy to J','files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(keep)}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
keep.append(ROOT/'SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(keep):z.write(p,arcname=ROOT.name+'/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(keep)
print('Validated archived content:',len(keep),'files')
