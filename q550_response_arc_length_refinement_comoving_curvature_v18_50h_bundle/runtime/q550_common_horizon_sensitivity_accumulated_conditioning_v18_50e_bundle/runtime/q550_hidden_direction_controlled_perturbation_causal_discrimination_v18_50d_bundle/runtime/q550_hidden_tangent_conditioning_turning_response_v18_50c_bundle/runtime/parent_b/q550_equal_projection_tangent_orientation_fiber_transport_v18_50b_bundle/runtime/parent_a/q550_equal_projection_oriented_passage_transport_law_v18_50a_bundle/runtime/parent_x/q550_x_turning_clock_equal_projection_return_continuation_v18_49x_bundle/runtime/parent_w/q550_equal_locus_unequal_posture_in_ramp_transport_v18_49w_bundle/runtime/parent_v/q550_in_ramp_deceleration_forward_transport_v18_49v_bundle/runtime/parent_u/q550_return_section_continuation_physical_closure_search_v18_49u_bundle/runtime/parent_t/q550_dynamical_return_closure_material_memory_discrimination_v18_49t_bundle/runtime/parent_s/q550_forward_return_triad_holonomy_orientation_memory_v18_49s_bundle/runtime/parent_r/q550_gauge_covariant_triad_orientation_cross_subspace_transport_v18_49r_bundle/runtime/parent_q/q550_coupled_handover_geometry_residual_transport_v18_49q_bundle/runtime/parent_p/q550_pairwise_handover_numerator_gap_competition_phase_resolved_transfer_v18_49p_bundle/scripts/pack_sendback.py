#!/usr/bin/env python3
"""Produce archive with descriptive root, full filenames and SHA-256 provenance."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
allowed={'scripts','tests','inputs','results'}
selected={}
for p in sorted(R.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(R)
    if '__pycache__' in rel.parts or p.suffix=='.pyc':continue
    if rel.parts[0] not in allowed and str(rel) not in ('README.md','SCIENTIFIC_REPORT.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh'):continue
    selected[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'version':'v18.49p','root':R.name,'parent':'v18.49o','files':selected,
          'scientific_status':json.loads((R/'results/report.json').read_text())['status']}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
output=R.parent/(R.name+'_sendback.zip')
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for name in selected:z.write(R/name,arcname=R.name+'/'+name)
    z.write(R/'SHA256SUMS_OUTPUT.json',arcname=R.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(output) as z:
    if z.testzip() is not None:raise RuntimeError('Archive corrupted')
    members={x for x in z.namelist() if not x.endswith('/')}
    if members!={R.name+'/'+k for k in selected}|{R.name+'/SHA256SUMS_OUTPUT.json'}:raise RuntimeError('Member list mismatch')
print('v18.49p archive',output,'manifest entries',len(selected))
