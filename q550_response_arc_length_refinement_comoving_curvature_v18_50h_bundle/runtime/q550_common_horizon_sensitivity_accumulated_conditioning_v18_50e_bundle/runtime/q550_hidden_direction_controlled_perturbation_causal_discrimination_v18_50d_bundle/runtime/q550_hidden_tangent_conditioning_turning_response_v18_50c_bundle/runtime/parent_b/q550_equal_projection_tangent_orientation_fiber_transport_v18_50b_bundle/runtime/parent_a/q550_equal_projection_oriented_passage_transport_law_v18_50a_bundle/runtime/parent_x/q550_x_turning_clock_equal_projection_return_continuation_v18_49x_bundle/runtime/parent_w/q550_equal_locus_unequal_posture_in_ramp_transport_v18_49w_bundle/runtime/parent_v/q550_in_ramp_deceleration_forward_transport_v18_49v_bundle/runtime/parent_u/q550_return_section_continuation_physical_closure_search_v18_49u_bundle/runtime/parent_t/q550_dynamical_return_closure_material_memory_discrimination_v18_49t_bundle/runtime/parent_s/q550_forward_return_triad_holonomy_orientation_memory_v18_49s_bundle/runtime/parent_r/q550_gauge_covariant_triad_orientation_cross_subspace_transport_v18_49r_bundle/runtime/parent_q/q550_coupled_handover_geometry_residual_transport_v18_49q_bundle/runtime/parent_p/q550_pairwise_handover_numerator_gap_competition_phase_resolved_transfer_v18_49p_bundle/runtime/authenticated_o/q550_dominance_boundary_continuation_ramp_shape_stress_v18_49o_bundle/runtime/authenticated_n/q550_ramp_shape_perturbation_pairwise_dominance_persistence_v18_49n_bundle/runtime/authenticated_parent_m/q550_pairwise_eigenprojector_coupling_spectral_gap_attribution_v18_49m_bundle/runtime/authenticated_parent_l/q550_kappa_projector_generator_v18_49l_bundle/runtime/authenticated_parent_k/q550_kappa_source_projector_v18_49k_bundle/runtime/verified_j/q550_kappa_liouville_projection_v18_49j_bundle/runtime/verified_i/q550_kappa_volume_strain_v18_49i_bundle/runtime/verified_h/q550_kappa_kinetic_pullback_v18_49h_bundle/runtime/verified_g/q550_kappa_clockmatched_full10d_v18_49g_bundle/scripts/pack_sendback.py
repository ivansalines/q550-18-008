"""Pack authentic reproducible results, code, inputs and a SHA-256 provenance map."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for p in sorted(R.rglob('*')):
    if not p.is_file():continue
    r=p.relative_to(R)
    if any(part in r.parts for part in ('runtime','__pycache__','.git','.pytest_cache')):continue
    if p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json'):continue
    if r.parts[0] in ('results','inputs','scripts','tests') or len(r.parts)==1:files.append(p)
manifest={'version':'v18.49g','parent':'Unchanged SHA256-authenticated v18.49f original server sendback, F->E->D->C->B->A->Z->...->J',
          'files':{p.relative_to(R).as_posix():hashfile(p) for p in files}}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as arc:
    for file in files+[R/'SHA256SUMS_OUTPUT.json']:
        arc.write(file,R.name+'/'+file.relative_to(R).as_posix())
with zipfile.ZipFile(R/'sendback.zip') as arc:
    assert arc.testzip() is None
    assert {x for x in arc.namelist() if not x.endswith('/')}=={R.name+'/'+x for x in manifest['files']}|{R.name+'/SHA256SUMS_OUTPUT.json'}
    for name,checksum in manifest['files'].items():
        assert hashlib.sha256(arc.read(R.name+'/'+name)).hexdigest()==checksum
print('v18.49g sendback',len(files)+1,'files authenticated; size', (R/'sendback.zip').stat().st_size)
