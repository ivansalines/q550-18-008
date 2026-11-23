import zipfile,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
include=('scripts','tests','inputs','results')
selected={}
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if '__pycache__' in rel.parts or 'runtime' in rel.parts or p.suffix=='.pyc':continue
 if rel.parts[0] in include or str(rel) in ('README.md','SCIENTIFIC_REPORT.md','SCIENTIFIC_DECISION_RULES.md','requirements.txt','run_on_server.sh'):
  selected[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
status=json.loads((R/'results/report.json').read_text())['status'] if (R/'results/report.json').exists() else 'UNEXECUTED'
manifest={'root':R.name,'version':'v18.49r','parent':'v18.49q','status':status,'files':selected}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=R.parent/(R.name+('_sendback.zip' if status!='UNEXECUTED' else '.zip'))
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for rel in selected:z.write(R/rel,R.name+'/'+rel)
 z.write(R/'SHA256SUMS_OUTPUT.json',R.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(selected)+1
 assert all(hashlib.sha256(z.read(R.name+'/'+rel)).hexdigest()==sha for rel,sha in selected.items())
print('Authentic v18.49r ZIP generated and verified:',out,'SHA entries',len(selected),flush=True)
