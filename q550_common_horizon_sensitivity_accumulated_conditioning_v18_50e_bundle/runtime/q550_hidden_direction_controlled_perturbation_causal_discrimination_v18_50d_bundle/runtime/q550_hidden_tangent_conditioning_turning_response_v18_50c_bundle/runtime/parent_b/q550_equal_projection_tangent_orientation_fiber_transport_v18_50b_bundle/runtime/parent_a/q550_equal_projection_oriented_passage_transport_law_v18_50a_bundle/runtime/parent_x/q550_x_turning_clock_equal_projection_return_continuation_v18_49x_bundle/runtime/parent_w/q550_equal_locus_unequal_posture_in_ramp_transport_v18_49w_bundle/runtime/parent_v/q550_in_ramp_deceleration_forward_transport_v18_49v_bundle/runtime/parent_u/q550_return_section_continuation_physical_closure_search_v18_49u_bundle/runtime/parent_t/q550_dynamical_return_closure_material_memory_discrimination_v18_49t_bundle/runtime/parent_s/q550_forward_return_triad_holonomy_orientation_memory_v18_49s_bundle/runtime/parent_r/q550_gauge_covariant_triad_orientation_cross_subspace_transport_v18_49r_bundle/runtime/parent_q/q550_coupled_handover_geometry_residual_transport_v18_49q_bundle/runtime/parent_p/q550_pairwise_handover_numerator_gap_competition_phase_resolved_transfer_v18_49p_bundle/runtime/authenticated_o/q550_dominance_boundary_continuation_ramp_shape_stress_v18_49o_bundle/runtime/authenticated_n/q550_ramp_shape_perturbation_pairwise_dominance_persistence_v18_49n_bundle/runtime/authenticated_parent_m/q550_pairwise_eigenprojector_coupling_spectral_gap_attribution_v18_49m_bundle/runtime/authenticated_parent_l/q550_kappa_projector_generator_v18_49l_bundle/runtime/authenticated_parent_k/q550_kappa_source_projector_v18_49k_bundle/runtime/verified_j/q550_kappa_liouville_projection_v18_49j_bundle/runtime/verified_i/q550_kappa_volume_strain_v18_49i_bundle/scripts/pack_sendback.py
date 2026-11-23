#!/usr/bin/env python3
"""Genealogy-preserving, hash-audited source and results archive."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or 'runtime' in p.relative_to(ROOT).parts or '__pycache__' in p.parts or p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json') or p.name.endswith('.log'):continue
 files.append(p)
manifest={'version':'v18.49i','status':'AUTHENTIC_MATERIAL_VOLUME_AND_PRINCIPAL_STRAIN_DIAGNOSTIC','files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
 z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 if z.testzip():raise RuntimeError('Broken sendback archive')
 for p in files:
  f=str(p.relative_to(ROOT));assert hashlib.sha256(z.read(ROOT.name+'/'+f)).hexdigest()==manifest['files'][f]
print('sendback complete:',len(files),'hashed files + manifest')
