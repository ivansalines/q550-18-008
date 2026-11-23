#!/usr/bin/env python3
"""Create a complete, light sendback excluding any expanded genealogical runtime."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
for mf,key in [('SOURCE_MANIFEST.json','files'),('SHA256SUMS_OUTPUT.json','file_sha256')]:
 doc=json.loads((root/mf).read_text())
 for rel,digest in doc[key].items():
  p=root/rel
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
   raise RuntimeError(f'{mf} verification failed: {rel}')
keep=set(json.loads((root/'SOURCE_MANIFEST.json').read_text())['files'])
keep.update(json.loads((root/'SHA256SUMS_OUTPUT.json').read_text())['file_sha256'])
keep.update(['SOURCE_MANIFEST.json','SHA256SUMS_OUTPUT.json'])
out=root.parent/(root.name+'_server_sendback.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for rel in sorted(keep):z.write(root/rel,arcname=root.name+'/'+rel)
with zipfile.ZipFile(out) as z:
 if z.testzip(): raise RuntimeError('Output zip CRC failure')
print('v18.50q SENDBACK CREATED',str(out),'files',len(keep),'bytes',out.stat().st_size)
