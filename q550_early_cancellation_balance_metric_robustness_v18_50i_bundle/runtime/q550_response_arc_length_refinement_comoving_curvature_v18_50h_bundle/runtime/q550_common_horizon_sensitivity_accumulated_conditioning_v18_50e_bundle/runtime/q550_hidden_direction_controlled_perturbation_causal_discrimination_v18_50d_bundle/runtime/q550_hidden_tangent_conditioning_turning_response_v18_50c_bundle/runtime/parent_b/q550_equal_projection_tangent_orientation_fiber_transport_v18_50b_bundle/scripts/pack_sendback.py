#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
items={str(p.relative_to(R)):digest(p) for p in sorted(R.rglob('*')) if p.is_file() and not any(z in p.relative_to(R).parts for z in ['runtime','__pycache__']) and p.name not in ['SHA256SUMS_OUTPUT.json','sendback.zip'] and not p.name.endswith('.log')}
m={'version':'v18.50b','root':R.name,'files':items}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(m,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for rel in [*items,'SHA256SUMS_OUTPUT.json']:z.write(R/rel,R.name+'/'+rel)
with zipfile.ZipFile(R/'sendback.zip') as z:
    if z.testzip() is not None:raise RuntimeError('Archive CRC failure')
    if len(z.namelist())!=len(items)+1:raise RuntimeError('Member count failure')
    for rel,check in items.items():
        if hashlib.sha256(z.read(R.name+'/'+rel)).hexdigest()!=check:raise RuntimeError('Member hash mismatch: '+rel)
print('v18.50b SENDBACK_DONE',len(items),'verified SHA-256 entries')
