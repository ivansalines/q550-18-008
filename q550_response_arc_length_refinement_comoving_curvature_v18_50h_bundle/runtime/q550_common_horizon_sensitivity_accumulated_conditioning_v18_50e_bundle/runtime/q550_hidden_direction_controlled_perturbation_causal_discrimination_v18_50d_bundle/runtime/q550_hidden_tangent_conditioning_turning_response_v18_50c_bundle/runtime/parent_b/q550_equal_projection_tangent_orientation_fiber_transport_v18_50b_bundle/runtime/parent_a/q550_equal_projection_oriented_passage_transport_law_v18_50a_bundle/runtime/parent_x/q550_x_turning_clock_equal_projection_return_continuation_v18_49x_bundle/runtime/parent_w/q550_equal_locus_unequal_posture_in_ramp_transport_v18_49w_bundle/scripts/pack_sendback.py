#!/usr/bin/env python3
"""Create rooted full sendback with checked SHA256 manifest, excluding runtime caches."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=[]
for p in ROOT.rglob('*'):
 if not p.is_file() or 'runtime' in p.relative_to(ROOT).parts or p.name in {'sendback.zip','SHA256SUMS_OUTPUT.json'} or p.name.endswith('.pyc') or '__pycache__' in p.parts:continue
 paths.append(p)
paths.sort()
files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
manifest={'version':'v18.49w','root':ROOT.name,'files':files}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in paths:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
 z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None
 for relative,digest in files.items():assert hashlib.sha256(z.read(ROOT.name+'/'+relative)).hexdigest()==digest
print('Packaged rooted v18.49w server sendback:',len(files),'SHA256 verified')
