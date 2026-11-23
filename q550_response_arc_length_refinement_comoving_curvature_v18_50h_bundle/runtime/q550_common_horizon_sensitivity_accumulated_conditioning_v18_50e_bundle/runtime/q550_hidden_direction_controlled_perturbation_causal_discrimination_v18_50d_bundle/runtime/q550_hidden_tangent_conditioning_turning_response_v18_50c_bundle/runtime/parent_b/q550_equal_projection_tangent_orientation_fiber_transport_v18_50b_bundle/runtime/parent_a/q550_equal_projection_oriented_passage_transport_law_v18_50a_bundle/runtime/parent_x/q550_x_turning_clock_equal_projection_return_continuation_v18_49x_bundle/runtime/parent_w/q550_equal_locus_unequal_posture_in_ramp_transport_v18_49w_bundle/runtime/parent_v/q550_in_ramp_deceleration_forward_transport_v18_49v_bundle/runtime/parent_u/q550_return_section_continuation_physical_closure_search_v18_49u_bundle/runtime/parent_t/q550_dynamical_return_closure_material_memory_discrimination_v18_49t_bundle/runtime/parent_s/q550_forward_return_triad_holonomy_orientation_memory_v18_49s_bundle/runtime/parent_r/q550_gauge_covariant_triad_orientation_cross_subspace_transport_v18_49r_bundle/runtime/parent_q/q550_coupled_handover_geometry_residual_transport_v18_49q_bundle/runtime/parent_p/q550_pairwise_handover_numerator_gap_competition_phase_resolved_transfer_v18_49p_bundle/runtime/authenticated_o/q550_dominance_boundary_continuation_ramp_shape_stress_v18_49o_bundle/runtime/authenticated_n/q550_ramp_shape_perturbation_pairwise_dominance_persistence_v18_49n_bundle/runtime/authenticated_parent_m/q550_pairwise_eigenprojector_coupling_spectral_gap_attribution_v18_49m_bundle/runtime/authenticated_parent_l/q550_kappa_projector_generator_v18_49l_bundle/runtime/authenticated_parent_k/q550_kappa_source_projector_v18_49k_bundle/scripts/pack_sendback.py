#!/usr/bin/env python3
"""Create SHA-256 authenticated ZIP containing scripts, inputs and generated outputs."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(k in p.parts for k in ('runtime','__pycache__')) and p.name not in ('sendback.zip','SHA256SUMS_OUTPUT.json'))
manifest={'version':'v18.49k','root':ROOT.name,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files+[ROOT/'SHA256SUMS_OUTPUT.json']:
        z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
    if z.testzip():raise RuntimeError('Corrupted sendback ZIP')
    members={p for p in z.namelist() if not p.endswith('/')}
    expected={ROOT.name+'/'+x for x in manifest['files']}|{ROOT.name+'/SHA256SUMS_OUTPUT.json'}
    if members!=expected:raise RuntimeError('Incorrect sendback members')
print('Authenticated',len(manifest['files']),'members; sendback.zip ready')
