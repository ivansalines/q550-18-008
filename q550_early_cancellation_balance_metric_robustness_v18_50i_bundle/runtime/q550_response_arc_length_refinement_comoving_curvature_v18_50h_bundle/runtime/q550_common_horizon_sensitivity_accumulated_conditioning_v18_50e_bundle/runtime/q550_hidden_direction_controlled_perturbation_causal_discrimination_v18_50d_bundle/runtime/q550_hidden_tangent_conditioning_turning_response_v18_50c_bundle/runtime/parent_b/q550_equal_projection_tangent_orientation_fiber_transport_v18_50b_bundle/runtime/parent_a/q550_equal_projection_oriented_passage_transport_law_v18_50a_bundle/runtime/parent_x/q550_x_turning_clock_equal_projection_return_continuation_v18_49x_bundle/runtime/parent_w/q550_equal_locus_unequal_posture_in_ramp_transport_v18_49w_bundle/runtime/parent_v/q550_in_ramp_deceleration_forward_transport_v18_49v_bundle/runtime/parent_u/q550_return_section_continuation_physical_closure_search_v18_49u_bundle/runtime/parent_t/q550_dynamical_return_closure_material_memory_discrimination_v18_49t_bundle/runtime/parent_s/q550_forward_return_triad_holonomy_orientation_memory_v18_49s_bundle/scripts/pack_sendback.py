#!/usr/bin/env python3
"""Create audit sendback with scripts, reports, outputs, ancestral source ZIP and hashes."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
manifest={}
for f in sorted(ROOT.rglob('*')):
    if not f.is_file() or f.name.endswith('.pyc') or '__pycache__' in f.parts or 'runtime' in f.relative_to(ROOT).parts or f.name=='SHA256SUMS_OUTPUT.json':continue
    rel=f.relative_to(ROOT).as_posix()
    manifest[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
m={'version':'v18.49s','root':ROOT.name,'files':manifest}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(m,indent=2)+'\n')
out=ROOT.parent/(ROOT.name+'_sendback.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for rel in manifest:z.write(ROOT/rel,ROOT.name+'/'+rel)
    z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
print('Packed',out,'members',len(manifest)+1)
