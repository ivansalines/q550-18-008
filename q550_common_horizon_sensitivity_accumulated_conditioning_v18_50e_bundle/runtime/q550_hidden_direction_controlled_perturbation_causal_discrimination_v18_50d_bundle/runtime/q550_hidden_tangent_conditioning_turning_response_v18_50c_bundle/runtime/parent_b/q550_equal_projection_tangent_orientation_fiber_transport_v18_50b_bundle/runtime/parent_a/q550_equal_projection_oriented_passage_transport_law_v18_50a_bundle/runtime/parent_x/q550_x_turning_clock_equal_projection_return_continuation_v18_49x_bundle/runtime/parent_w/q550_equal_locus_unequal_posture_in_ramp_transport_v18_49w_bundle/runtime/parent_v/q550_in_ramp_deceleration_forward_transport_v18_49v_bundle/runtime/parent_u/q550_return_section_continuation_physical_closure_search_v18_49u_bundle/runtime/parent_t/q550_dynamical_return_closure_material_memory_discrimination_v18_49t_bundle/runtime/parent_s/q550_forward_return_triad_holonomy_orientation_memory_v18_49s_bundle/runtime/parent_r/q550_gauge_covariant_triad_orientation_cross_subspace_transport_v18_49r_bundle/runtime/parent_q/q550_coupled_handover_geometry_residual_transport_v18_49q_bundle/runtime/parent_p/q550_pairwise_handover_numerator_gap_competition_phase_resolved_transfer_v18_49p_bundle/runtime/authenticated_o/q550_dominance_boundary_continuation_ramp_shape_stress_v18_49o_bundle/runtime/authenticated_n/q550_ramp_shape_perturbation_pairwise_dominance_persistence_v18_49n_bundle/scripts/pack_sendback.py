#!/usr/bin/env python3
"""Package full source+parent ZIP+measured results; maintain self-identifying archive root."""
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
assert ROOT.name.endswith('_v18_49n_bundle')
files={}
for p in sorted(ROOT.rglob('*')):
    if not p.is_file():continue
    r=p.relative_to(ROOT)
    if r.parts[0] in ('runtime','__pycache__') or '__pycache__' in r.parts or r.suffix=='.pyc':continue
    if p.name in ('sendback.zip',ROOT.name+'_sendback.zip','SHA256SUMS_OUTPUT.json'):continue
    if r.parts[0] not in ('scripts','tests','inputs','results') and p.name not in ('README.md','SCIENTIFIC_REPORT.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh','v18_49n_server.log'):continue
    files[str(r)]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'version':'v18.49n','root':ROOT.name,'files':files,'parent':'v18.49m','source':'Genuine authenticated Q550 dynamic solver and outputs'}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=ROOT.parent/(ROOT.name+'_sendback.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for f in files:z.write(ROOT/f,arcname=ROOT.name+'/'+f)
    z.write(ROOT/'SHA256SUMS_OUTPUT.json',arcname=ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('Zip CRC mismatch')
    actual={n for n in z.namelist() if not n.endswith('/')}
    if actual!={ROOT.name+'/'+f for f in files}|{ROOT.name+'/SHA256SUMS_OUTPUT.json'}:raise RuntimeError('Zip membership mismatch')
shutil.copy2(archive,ROOT/'sendback.zip')
print('Generated',archive,'size',archive.stat().st_size)
