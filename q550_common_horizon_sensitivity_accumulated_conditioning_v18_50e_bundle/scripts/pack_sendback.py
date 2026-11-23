#!/usr/bin/env python3
"""Write auditable output sendback with complete descriptive name and coherent ZIP root."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
VER='v18.50e'
rel=[]
for prefix in ('scripts','tests','results','inputs'):
    rel.extend(p for p in (ROOT/prefix).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
rel += [ROOT/'README.md',ROOT/'SCIENTIFIC_DECISION_RULES.md',ROOT/'SCIENTIFIC_REPORT.md',ROOT/'requirements.txt',ROOT/'run_on_server.sh']
files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(rel))}
manifest={'root':ROOT.name,'version':VER,'files':files}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
name=ROOT.parent/(ROOT.name+'_sendback.zip')
with zipfile.ZipFile(name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in sorted(set(rel)):z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
    z.write(ROOT/'SHA256SUMS_OUTPUT.json',arcname=ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(name) as z:
    assert z.testzip() is None
    assert set(z.namelist())=={ROOT.name+'/'+n for n in files}|{ROOT.name+'/SHA256SUMS_OUTPUT.json'}
    for rel,sha in files.items():assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==sha
print('Sendback:',name,'members',len(files)+1,'bytes',name.stat().st_size)
