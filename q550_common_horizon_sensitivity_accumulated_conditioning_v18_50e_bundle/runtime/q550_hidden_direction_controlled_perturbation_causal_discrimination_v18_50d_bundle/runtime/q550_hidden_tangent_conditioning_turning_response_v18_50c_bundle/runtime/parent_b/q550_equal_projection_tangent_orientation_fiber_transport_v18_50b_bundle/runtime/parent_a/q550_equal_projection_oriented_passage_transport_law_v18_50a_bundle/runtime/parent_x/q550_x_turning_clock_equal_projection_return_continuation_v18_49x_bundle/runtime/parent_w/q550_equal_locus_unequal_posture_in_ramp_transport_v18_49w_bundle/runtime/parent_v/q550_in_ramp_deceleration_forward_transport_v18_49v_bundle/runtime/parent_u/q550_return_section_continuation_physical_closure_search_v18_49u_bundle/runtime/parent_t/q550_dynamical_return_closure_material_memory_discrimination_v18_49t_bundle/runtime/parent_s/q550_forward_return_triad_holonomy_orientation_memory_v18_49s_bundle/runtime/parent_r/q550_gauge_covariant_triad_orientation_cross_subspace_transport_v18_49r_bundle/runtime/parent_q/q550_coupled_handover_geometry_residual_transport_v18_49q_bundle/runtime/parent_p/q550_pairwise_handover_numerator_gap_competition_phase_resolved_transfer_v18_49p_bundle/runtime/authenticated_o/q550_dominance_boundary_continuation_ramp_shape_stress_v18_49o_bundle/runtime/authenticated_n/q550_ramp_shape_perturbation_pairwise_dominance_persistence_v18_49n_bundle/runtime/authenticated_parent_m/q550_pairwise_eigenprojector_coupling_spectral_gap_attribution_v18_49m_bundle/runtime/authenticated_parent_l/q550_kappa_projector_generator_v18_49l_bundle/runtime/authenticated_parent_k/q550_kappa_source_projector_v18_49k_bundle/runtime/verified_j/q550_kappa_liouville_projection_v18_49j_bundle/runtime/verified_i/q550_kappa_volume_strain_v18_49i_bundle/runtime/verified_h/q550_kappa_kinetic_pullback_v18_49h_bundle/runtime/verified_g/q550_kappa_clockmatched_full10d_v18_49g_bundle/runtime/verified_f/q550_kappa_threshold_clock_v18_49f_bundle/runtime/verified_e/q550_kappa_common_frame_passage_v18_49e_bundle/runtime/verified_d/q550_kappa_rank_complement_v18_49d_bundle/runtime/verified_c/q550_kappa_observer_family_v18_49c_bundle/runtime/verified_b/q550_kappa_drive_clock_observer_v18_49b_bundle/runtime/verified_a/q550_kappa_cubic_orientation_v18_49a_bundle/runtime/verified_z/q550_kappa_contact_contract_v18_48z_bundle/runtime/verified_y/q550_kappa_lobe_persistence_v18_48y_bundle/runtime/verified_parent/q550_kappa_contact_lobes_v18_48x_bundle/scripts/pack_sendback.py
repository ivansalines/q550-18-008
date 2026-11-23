#!/usr/bin/env python3
"""Portable exact rooted-archive SHA256 manifest, excludes working/runtime files."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
files=sorted((p for p in ROOT.rglob('*') if p.is_file()
    and p.name not in ('sendback.zip','SHA256SUMS_OUTPUT.json')
    and not any(s in ('runtime','__pycache__','.pytest_cache') for s in p.relative_to(ROOT).parts)
    and p.suffix!='.pyc' and not p.name.endswith('.log')),
    key=lambda p:str(p.relative_to(ROOT)))
manifest=ROOT/'SHA256SUMS_OUTPUT.json'
manifest.write_text(json.dumps({'version':'v18.48x','files':{str(p.relative_to(ROOT)):sha(p) for p in files}},indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in [*files,manifest]:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
print('Packed v18.48x',len(files),'files + manifest;',sha(ROOT/'sendback.zip'))
