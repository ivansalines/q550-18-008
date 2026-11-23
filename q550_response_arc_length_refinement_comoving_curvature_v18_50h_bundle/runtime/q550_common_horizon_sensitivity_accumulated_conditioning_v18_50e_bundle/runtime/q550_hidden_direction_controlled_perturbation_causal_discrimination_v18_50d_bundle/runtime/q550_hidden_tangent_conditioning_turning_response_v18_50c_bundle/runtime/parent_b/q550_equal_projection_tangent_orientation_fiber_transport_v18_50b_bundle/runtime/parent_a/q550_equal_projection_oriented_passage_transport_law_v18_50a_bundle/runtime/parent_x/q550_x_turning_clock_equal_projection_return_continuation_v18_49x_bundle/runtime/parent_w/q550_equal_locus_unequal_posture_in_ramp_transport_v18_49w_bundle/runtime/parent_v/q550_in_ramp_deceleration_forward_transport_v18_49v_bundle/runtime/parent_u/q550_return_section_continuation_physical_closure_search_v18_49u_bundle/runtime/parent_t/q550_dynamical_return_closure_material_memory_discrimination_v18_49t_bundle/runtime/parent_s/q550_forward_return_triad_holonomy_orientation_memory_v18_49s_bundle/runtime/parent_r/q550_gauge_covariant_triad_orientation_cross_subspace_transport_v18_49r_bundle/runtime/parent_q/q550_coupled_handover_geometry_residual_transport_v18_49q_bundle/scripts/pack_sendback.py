#!/usr/bin/env python3
"""Produce descriptive, single-root, CRC-checked, SHA-256-manifest archive."""
import zipfile,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
selected={}
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if '__pycache__' in rel.parts or p.suffix=='.pyc' or 'runtime' in rel.parts:continue
 if rel.parts[0] not in ('scripts','tests','inputs','results') and str(rel) not in ('README.md','SCIENTIFIC_REPORT.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh'):continue
 selected[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'root':R.name,'version':'v18.49q','parent':'v18.49p','files':selected,'status':json.loads((R/'results/report.json').read_text())['status']}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
output=R.parent/(R.name+'_sendback.zip')
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in selected:z.write(R/name,R.name+'/'+name)
 z.write(R/'SHA256SUMS_OUTPUT.json',R.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(output) as z:
 if z.testzip() is not None:raise RuntimeError('CRC failure')
 expected={R.name+'/'+k for k in selected}|{R.name+'/SHA256SUMS_OUTPUT.json'}
 if set(z.namelist())!=expected:raise RuntimeError('Unexpected archive structure')
 for rel,sha in selected.items():
  if hashlib.sha256(z.read(R.name+'/'+rel)).hexdigest()!=sha:raise RuntimeError('SHA mismatch '+rel)
print('v18.49q sendback verified:',output,'SHA entries',len(selected))
