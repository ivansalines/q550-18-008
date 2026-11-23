#!/usr/bin/env python3
"""Create compact sendback, never embedding multi-gigabyte extracted runtime."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sm=json.loads((R/'SOURCE_MANIFEST.json').read_text())
om=json.loads((R/'SHA256SUMS_OUTPUT.json').read_text())
for rel,expected in sm['files'].items():
    if hashlib.sha256((R/rel).read_bytes()).hexdigest()!=expected:raise RuntimeError('Source drift: '+rel)
for rel,expected in om['file_sha256'].items():
    if hashlib.sha256((R/rel).read_bytes()).hexdigest()!=expected:raise RuntimeError('Output drift: '+rel)
rels=sorted(set(sm['files'])|set(om['file_sha256'])|{'SOURCE_MANIFEST.json','SHA256SUMS_OUTPUT.json'})
target=R.parent/(R.name+'_server_sendback.zip')
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for rel in rels:z.write(R/rel,arcname=R.name+'/'+rel)
with zipfile.ZipFile(target) as z:
    if z.testzip() is not None:raise RuntimeError('Sendback ZIP CRC error')
print('v18.50o SENDBACK',target,'members',len(rels),'bytes',target.stat().st_size)
