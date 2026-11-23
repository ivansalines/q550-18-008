#!/usr/bin/env python3
"""Create reproducible sendback with original G zip unchanged and SHA manifest."""
import hashlib,zipfile,json,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
exclude={'sendback.zip','SHA256SUMS_OUTPUT.json'}
files=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(ROOT)
 if '__pycache__' in rel.parts or 'runtime' in rel.parts or p.name in exclude:continue
 files.append((rel,p))
manifest={'version':'v18.49h','status':'AUTHENTIC_11D_KINETIC_METRIC_DIAGNOSTIC',
          'files':{str(rel):hashlib.sha256(p.read_bytes()).hexdigest() for rel,p in files}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
name=ROOT.name
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for rel,p in files:z.write(p,name+'/'+str(rel))
 z.write(ROOT/'SHA256SUMS_OUTPUT.json',name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None
 for rel,p in files:
  assert hashlib.sha256(z.read(name+'/'+str(rel))).hexdigest()==manifest['files'][str(rel)]
print(f'sendback authenticated: {len(files)} entries + manifest, bytes={(ROOT/"sendback.zip").stat().st_size}')
