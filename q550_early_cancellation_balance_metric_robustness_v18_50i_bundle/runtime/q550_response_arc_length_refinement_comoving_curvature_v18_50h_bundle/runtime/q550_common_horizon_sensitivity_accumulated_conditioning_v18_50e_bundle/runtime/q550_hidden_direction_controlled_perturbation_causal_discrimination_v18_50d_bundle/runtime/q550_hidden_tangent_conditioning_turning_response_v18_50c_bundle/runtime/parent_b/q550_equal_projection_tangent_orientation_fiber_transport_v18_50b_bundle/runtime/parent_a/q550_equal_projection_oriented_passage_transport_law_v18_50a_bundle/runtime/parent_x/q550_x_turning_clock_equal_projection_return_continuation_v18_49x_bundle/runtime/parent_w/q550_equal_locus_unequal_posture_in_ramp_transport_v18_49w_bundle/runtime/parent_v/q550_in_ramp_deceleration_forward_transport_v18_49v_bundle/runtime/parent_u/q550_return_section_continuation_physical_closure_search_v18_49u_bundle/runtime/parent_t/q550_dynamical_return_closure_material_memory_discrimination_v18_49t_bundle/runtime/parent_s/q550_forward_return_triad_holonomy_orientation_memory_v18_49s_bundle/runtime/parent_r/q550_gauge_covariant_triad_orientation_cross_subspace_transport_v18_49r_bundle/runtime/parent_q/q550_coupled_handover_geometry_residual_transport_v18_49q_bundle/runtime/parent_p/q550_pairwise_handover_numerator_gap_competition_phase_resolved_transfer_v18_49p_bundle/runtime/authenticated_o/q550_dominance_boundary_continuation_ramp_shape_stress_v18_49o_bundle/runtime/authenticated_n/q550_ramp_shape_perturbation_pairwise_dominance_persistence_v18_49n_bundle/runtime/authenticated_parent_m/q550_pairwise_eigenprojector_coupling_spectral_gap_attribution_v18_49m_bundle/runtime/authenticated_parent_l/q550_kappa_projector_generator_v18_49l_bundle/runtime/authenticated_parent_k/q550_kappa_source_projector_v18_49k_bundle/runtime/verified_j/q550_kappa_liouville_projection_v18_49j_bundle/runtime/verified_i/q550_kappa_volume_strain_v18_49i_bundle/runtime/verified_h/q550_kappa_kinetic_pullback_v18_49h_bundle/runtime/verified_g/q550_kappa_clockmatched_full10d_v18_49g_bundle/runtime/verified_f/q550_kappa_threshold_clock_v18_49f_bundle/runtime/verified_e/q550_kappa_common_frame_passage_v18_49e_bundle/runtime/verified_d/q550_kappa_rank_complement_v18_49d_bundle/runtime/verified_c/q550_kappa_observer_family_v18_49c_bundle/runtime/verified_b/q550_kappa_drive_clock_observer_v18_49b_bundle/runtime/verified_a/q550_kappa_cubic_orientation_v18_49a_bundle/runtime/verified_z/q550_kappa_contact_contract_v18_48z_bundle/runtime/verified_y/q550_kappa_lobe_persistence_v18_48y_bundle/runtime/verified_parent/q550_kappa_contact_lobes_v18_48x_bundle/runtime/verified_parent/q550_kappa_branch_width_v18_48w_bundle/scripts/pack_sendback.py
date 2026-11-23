#!/usr/bin/env python3
"""Write exact-hierarchy v18.48w sendback with a portable SHA-256 manifest."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
files=sorted((p for p in ROOT.rglob('*') if p.is_file()
   and p.name not in ('sendback.zip','SHA256SUMS_OUTPUT.json')
   and not any(part in ('runtime','__pycache__','.pytest_cache') for part in p.relative_to(ROOT).parts)
   and p.suffix!='.pyc' and not p.name.endswith('.log')),key=lambda p:str(p.relative_to(ROOT)))
manifest=ROOT/'SHA256SUMS_OUTPUT.json'
manifest.write_text(json.dumps({'version':'v18.48w','files':{str(p.relative_to(ROOT)):sha(p) for p in files}},indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in [*files,manifest]:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
print('Packed',len(files)+1,'entries with root',ROOT.name,'SHA256',sha(ROOT/'sendback.zip'))
