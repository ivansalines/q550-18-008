#!/usr/bin/env python3
"""Package the complete executable audit genealogy and authenticated outputs."""
from pathlib import Path
import datetime,hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[]
for p in sorted(R.rglob('*')):
    if not p.is_file() or any(v in ('runtime','__pycache__','.pytest_cache') for v in p.relative_to(R).parts):continue
    if p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json') or p.suffix=='.pyc':continue
    paths.append(p)
files={str(p.relative_to(R)):sha(p) for p in paths}
m={'version':'v18.48p','archive_root':R.name,'file_count':len(files),'files':files}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(m,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in paths+[R/'SHA256SUMS_OUTPUT.json']:
        z.write(p,arcname=R.name+'/'+str(p.relative_to(R)))
with zipfile.ZipFile(R/'sendback.zip') as z:
    if z.testzip():raise RuntimeError('Generated sendback corrupted')
    for rel,digest in files.items():
        if hashlib.sha256(z.read(R.name+'/'+rel)).hexdigest()!=digest:raise RuntimeError('Sendback invalid '+rel)
print(f'v18.48p generated sendback.zip, {len(files)} authenticated content files')
