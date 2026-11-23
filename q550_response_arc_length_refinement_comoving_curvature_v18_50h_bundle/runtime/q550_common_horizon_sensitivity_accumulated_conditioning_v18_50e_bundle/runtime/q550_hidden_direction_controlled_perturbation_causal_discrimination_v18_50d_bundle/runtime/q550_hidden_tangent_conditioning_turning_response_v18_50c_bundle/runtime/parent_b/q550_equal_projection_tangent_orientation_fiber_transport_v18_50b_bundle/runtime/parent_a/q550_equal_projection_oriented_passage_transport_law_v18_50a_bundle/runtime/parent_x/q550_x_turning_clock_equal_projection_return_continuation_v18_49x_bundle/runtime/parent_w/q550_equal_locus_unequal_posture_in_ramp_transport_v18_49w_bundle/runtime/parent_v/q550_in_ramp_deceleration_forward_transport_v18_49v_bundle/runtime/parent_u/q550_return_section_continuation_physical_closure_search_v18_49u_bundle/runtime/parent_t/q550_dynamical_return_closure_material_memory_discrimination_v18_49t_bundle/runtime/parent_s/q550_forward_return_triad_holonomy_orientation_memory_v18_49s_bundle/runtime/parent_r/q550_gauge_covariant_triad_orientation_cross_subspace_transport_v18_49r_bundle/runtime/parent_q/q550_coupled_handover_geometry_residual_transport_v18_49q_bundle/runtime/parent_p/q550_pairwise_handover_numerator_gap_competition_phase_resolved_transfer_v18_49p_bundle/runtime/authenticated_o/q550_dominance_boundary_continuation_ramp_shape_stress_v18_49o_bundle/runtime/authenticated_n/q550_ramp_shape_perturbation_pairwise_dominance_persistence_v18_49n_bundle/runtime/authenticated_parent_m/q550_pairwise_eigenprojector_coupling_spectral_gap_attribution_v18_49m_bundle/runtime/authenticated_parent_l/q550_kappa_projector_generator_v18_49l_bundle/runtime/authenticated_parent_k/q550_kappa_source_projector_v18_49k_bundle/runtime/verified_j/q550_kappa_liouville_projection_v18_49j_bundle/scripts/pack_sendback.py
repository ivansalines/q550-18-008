#!/usr/bin/env python3
"""Pack all executable sources, immutable ancestor, data and figures; hash contents."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or 'runtime' in p.relative_to(ROOT).parts or '__pycache__' in p.parts or p.name in ('SHA256SUMS_OUTPUT.json','sendback.zip') or p.name.endswith('.log'):continue
 files.append(p)
manifest={'version':'v18.49j','classification':'AUTHENTIC_Q550_LIOUVILLE_STRAIN_PROJECTION_DIAGNOSTIC',
 'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
 z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None
 for p in files:
  rel=str(p.relative_to(ROOT));assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==manifest['files'][rel]
print(f'v18.49j sendback authenticated: {len(files)} files + manifest')
