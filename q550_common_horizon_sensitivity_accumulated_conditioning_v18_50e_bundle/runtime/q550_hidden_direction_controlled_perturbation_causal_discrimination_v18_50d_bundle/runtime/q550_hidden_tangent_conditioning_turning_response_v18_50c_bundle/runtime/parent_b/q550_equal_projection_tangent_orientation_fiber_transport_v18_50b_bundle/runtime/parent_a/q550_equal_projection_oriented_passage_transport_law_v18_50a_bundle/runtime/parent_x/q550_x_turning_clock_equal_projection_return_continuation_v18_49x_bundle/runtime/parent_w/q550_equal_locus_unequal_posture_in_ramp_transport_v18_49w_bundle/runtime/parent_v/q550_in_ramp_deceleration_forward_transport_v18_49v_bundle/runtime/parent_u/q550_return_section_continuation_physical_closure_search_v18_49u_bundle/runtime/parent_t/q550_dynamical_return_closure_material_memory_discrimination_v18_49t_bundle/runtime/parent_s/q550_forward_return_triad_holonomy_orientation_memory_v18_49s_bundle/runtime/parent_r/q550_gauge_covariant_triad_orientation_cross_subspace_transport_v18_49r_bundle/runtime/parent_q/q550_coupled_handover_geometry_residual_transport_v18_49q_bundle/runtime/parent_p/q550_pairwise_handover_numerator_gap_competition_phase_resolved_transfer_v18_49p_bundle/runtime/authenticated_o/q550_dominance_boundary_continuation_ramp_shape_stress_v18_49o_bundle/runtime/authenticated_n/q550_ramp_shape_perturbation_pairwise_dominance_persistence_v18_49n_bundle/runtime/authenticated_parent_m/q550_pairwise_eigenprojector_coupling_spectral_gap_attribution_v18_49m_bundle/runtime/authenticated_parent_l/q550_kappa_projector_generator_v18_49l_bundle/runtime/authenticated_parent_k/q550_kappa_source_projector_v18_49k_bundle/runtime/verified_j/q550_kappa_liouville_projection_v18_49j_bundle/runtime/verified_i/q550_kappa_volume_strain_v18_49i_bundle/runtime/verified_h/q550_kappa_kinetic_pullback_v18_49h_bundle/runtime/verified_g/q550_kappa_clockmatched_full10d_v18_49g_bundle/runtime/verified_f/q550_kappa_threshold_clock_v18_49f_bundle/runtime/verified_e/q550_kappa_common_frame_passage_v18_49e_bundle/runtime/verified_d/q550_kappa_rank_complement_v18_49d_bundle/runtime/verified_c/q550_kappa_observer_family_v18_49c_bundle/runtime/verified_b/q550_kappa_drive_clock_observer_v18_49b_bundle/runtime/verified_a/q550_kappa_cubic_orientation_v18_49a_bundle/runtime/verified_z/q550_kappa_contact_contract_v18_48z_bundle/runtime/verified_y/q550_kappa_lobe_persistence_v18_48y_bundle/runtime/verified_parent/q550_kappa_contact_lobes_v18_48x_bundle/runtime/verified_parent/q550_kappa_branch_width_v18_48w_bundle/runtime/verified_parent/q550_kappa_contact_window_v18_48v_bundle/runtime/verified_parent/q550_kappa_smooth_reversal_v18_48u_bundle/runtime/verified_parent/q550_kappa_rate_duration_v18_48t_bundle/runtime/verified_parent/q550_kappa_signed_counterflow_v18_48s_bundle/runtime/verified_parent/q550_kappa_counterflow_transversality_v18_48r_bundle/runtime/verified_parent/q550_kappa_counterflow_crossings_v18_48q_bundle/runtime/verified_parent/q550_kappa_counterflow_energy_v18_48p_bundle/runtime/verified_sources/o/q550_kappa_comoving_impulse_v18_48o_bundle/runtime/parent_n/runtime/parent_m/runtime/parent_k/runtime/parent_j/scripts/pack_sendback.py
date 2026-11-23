"""Package complete executable genealogy and results (no bytecode/runtime duplication)."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
files=[]
for f in ROOT.rglob('*'):
 if not f.is_file() or f.name in ('sendback.zip','SHA256SUMS_OUTPUT.json') or '__pycache__' in f.parts or 'runtime' in f.parts:
  continue
 files.append(f)
files.sort()
manifest={'version':'v18.48j','archive_root':ROOT.name,'file_count':len(files),
          'files':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in files}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[ROOT/'SHA256SUMS_OUTPUT.json']:
  z.write(p,arcname=f'{ROOT.name}/{p.relative_to(ROOT).as_posix()}')
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None
 for name,digest in manifest['files'].items():
  assert sha(z.read(ROOT.name+'/'+name))==digest
print('SENDBACK',ROOT/'sendback.zip','verified files',len(files))
