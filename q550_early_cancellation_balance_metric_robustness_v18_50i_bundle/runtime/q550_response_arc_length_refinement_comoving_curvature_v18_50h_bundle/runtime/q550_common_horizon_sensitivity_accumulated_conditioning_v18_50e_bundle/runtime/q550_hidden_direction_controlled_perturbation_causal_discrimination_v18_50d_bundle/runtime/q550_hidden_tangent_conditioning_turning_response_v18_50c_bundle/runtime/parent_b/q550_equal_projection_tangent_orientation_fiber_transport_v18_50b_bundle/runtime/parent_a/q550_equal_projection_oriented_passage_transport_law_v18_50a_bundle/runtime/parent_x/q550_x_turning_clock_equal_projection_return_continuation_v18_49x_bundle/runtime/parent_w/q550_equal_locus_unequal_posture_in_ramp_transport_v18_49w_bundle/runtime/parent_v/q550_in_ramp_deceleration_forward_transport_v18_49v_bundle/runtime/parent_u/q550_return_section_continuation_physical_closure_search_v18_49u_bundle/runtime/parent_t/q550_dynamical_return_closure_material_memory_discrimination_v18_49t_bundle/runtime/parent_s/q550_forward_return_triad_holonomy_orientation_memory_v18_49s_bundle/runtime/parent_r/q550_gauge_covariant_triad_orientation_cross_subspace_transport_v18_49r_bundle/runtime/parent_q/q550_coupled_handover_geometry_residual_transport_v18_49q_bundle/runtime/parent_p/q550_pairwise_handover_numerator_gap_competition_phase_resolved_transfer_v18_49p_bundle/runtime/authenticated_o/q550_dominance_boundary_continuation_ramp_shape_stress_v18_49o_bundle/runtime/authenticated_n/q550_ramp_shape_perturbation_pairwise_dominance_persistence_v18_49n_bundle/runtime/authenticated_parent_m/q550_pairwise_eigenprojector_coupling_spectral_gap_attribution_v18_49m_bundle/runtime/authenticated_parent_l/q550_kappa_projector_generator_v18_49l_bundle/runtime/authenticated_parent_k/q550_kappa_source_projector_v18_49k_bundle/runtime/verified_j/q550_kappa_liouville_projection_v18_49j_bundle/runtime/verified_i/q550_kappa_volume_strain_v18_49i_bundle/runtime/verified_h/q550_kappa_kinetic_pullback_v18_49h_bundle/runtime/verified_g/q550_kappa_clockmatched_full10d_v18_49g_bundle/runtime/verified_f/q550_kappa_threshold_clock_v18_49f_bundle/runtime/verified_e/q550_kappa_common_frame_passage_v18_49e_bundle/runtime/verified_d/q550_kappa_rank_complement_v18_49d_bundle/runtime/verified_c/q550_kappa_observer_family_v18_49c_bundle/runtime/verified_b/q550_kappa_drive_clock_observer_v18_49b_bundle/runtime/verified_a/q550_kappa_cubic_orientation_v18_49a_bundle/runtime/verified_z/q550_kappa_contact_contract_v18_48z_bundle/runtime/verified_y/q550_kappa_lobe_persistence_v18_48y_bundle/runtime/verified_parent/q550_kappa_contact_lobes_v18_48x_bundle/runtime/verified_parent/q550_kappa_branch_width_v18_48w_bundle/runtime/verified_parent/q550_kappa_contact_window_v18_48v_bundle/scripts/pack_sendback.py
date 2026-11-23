#!/usr/bin/env python3
"""Deterministic provenance-aware archive. Explicitly exclude runtime and logs."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
files=sorted(p for p in ROOT.rglob('*') if p.is_file()
    and p!=ROOT/'sendback.zip' and p!=ROOT/'SHA256SUMS_OUTPUT.json'
    and not any(s in ('runtime','__pycache__','.pytest_cache') for s in p.relative_to(ROOT).parts)
    and p.suffix!='.pyc' and not p.name.endswith('.log'))
manifest=ROOT/'SHA256SUMS_OUTPUT.json'
manifest.write_text(json.dumps({'version':'v18.48v','files':{str(p.relative_to(ROOT)):sha(p) for p in files}},indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in [*files,manifest]:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
print('Packed',len(files)+1,'files including manifest, SHA',sha(ROOT/'sendback.zip'))
