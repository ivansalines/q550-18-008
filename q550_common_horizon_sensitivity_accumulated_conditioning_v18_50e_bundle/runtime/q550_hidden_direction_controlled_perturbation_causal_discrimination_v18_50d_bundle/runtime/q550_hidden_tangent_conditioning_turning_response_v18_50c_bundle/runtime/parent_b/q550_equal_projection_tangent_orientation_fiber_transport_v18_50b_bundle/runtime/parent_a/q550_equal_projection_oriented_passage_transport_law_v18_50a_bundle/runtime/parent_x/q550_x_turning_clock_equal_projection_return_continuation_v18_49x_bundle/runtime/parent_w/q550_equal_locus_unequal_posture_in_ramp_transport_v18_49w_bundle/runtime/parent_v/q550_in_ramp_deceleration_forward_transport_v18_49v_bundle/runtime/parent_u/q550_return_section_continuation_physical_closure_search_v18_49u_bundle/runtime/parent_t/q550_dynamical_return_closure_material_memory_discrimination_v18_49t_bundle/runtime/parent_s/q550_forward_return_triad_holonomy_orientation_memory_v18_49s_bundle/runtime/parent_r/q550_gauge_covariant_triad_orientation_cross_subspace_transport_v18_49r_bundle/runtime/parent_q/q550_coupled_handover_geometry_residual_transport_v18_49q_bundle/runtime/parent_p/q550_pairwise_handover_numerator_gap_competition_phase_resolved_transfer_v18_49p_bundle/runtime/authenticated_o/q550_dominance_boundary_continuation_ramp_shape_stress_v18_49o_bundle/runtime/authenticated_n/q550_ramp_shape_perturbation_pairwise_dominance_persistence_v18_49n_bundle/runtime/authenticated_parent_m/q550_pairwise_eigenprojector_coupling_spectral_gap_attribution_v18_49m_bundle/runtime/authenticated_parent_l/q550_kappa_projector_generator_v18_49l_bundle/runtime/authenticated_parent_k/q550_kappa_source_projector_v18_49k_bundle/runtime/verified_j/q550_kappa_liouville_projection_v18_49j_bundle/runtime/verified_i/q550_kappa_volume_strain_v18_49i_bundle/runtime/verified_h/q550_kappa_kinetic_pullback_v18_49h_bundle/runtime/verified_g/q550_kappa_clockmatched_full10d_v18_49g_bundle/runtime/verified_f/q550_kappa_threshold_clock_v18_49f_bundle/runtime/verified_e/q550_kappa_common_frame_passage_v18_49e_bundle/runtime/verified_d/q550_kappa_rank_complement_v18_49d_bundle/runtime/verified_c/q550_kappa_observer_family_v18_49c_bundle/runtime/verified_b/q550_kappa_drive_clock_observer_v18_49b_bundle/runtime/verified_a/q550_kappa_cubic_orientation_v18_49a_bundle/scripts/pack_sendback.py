#!/usr/bin/env python3
"""Build exact deterministic membership ZIP and SHA manifest for server sendback."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for p in ROOT.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(ROOT).as_posix()
    if rel in ('sendback.zip','SHA256SUMS_OUTPUT.json'):continue
    if any(part in p.relative_to(ROOT).parts for part in ('runtime','__pycache__','.git')):continue
    if rel in ('README.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh') or rel.startswith(('inputs/','scripts/','tests/','results/','reference/')):
        files.append(p)
m={'version':'v18.49a','ancestor_source':'byte-exact original Z server sendback, recursively SHA checked',
   'files':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(m,indent=2)+'\n')
files.append(ROOT/'SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files):z.write(p,arcname=ROOT.name+'/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(files)
print('Packed',len(files),'files',ROOT/'sendback.zip')
