#!/usr/bin/env python3
"""Make full-name, matched-root ZIP with independently verifiable per-file SHA256."""
from pathlib import Path
import hashlib,json,zipfile,shutil
R=Path(__file__).resolve().parents[1]
files={}
for p in sorted(R.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(R)
    if rel.parts[0] not in ('scripts','tests','inputs','results') and p.name not in ('README.md','SCIENTIFIC_REPORT.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh'):continue
    if '__pycache__' in rel.parts or p.suffix=='.pyc':continue
    files[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'version':'v18.49o','root':R.name,'files':files,'parent':'v18.49n',
          'scientific_status':json.loads((R/'results/report.json').read_text())['status']}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=R.parent/(R.name+'_sendback.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for f in files:z.write(R/f,arcname=R.name+'/'+f)
    z.write(R/'SHA256SUMS_OUTPUT.json',arcname=R.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(out) as z:
    if z.testzip() is not None:raise RuntimeError('Output CRC failure')
    assert {x for x in z.namelist() if not x.endswith('/')}=={R.name+'/'+x for x in files}|{R.name+'/SHA256SUMS_OUTPUT.json'}
shutil.copy2(out,R/'sendback.zip')
print('Created:',out)
