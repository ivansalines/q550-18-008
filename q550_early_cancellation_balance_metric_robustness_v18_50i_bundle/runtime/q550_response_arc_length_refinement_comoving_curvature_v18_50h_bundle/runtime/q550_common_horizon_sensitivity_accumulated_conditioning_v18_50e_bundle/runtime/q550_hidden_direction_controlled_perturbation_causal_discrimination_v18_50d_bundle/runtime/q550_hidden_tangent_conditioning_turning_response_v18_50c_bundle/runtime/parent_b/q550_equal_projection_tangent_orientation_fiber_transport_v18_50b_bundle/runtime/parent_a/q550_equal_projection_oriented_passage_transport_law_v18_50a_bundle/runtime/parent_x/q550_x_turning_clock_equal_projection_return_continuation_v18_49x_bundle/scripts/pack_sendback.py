#!/usr/bin/env python3
"""Build reproducible sendback and checksums for full v18.49x bundle."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
items={str(p.relative_to(R)):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and 'runtime' not in p.relative_to(R).parts and p.name not in ('SHA256SUMS_OUTPUT.json','sendback.zip','RUN_EXIT') and p.suffix != '.log'}
manifest={'version':'v18.49x','root':R.name,'files':items}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for rel in [*items,'SHA256SUMS_OUTPUT.json']:
  z.write(R/rel,arcname=R.name+'/'+rel)
with zipfile.ZipFile(R/'sendback.zip') as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(items)+1
print('SENDBACK_DONE',len(items),'manifest members',flush=True)
