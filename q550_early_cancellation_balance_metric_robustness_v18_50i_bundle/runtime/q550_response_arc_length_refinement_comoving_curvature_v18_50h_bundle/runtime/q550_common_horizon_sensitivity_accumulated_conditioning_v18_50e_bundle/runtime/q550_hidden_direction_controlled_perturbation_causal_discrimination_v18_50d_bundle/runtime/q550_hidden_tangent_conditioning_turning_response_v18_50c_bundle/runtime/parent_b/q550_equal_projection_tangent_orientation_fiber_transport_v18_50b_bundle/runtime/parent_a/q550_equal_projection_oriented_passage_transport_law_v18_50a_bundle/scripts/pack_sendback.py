#!/usr/bin/env python3
"""Produce complete-root checked server sendback preserving exact audit ancestry."""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
items={str(p.relative_to(R)):digest(p) for p in sorted(R.rglob('*')) if p.is_file() and not any(x in p.relative_to(R).parts for x in ('runtime','__pycache__')) and p.name not in ('sendback.zip','SHA256SUMS_OUTPUT.json','RUN_EXIT') and not p.name.endswith('.log')}
m={'version':'v18.50a','root':R.name,'files':items}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(m,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for rel in [*items,'SHA256SUMS_OUTPUT.json']:z.write(R/rel,R.name+'/'+rel)
with zipfile.ZipFile(R/'sendback.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(items)+1
 assert all(hashlib.sha256(z.read(R.name+'/'+rel)).hexdigest()==s for rel,s in items.items())
print('v18.50a SENDBACK_DONE',len(items),'verified SHA-256 entries')
