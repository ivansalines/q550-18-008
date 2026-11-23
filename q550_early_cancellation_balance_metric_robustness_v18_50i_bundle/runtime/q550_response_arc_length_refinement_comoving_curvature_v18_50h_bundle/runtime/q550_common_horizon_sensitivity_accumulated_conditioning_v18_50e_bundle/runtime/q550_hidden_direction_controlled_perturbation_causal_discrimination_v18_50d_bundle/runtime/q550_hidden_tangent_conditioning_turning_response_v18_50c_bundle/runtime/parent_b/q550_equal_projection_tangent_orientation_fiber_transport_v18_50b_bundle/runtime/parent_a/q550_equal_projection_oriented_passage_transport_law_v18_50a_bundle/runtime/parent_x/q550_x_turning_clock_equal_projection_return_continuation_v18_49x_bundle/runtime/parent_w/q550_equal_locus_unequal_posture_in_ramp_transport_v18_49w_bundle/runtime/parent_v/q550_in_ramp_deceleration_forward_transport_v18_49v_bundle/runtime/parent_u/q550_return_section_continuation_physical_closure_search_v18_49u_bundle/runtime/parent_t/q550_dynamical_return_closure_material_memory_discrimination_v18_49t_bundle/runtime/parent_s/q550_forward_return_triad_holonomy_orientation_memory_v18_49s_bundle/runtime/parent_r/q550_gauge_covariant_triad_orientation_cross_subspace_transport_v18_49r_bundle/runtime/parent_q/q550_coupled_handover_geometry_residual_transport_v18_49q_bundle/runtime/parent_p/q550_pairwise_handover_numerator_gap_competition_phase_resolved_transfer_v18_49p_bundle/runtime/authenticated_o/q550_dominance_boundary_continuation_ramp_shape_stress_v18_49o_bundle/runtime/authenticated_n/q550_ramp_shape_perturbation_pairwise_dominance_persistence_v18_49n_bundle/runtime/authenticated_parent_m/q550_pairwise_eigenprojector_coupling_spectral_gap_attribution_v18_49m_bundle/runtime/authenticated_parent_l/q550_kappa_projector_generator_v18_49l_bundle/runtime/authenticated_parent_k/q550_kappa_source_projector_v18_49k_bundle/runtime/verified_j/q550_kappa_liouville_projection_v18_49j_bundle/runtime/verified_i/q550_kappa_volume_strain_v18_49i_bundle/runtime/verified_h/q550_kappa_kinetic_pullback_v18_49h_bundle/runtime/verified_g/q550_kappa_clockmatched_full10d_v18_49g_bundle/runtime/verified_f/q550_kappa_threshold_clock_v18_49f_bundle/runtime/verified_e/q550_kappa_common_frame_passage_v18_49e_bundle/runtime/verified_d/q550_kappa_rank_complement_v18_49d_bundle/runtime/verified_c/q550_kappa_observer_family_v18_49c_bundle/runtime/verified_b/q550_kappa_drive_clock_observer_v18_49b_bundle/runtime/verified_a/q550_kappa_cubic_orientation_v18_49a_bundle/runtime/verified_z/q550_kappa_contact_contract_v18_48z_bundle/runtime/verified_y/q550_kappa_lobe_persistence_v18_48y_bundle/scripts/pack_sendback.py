#!/usr/bin/env python3
"""Bundle original Python genealogy and replay outputs in a verified rooted ZIP."""
from __future__ import annotations
import hashlib,json,platform,zipfile
from pathlib import Path
import numpy,scipy,matplotlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for buf in iter(lambda:f.read(1048576),b''):h.update(buf)
    return h.hexdigest()
( ROOT/'results/runtime_environment.json').write_text(json.dumps({
   'python':platform.python_version(),'numpy':numpy.__version__,
   'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,
   'model':'Original v18.48x 11D with unchanged physics SHA-256',
   'numeric_status':'floating point; no interval certification'},indent=2)+'\n')
paths=sorted((p for p in ROOT.rglob('*') if p.is_file()
   and p.name not in ('sendback.zip','SHA256SUMS_OUTPUT.json')
   and not any(s in ('runtime','__pycache__','.pytest_cache') for s in p.relative_to(ROOT).parts)
   and p.suffix!='.pyc' and not p.name.endswith('.log')),
   key=lambda p:str(p.relative_to(ROOT)))
man=ROOT/'SHA256SUMS_OUTPUT.json'
man.write_text(json.dumps({'version':'v18.48y','root':ROOT.name,
    'files':{str(p.relative_to(ROOT)):sha(p) for p in paths}},indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in [*paths,man]:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if not n.endswith('/')])==len(paths)+1
print(f'Packed v18.48y: {len(paths)} SHA-256 files, original ancestry and exact executed Python; ZIP SHA256={sha(ROOT/"sendback.zip")}')
