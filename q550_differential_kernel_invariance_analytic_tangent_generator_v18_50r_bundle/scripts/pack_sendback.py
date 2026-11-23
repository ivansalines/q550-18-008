#!/usr/bin/env python3
"""Pack reproducible, small sendback; never include expanded historical runtime."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
keep=set()
for manifest,key in [('SOURCE_MANIFEST.json','files'),('SHA256SUMS_OUTPUT.json','file_sha256')]:
 data=json.loads((root/manifest).read_text())
 if data['root']!=root.name:raise RuntimeError('Wrong manifest root')
 for rel,expected in data[key].items():
  p=root/rel
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
   raise RuntimeError('Incorrect file digest: '+rel)
  keep.add(rel)
 keep.add(manifest)
out=root.parent/(root.name+'_server_sendback.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for rel in sorted(keep):z.write(root/rel,arcname=root.name+'/'+rel)
with zipfile.ZipFile(out) as z:
 if z.testzip() is not None:raise RuntimeError('Sendback ZIP CRC mismatch')
print('v18.50r SENDBACK CREATED',out,'files',len(keep),'bytes',out.stat().st_size)
