#!/usr/bin/env python3
"""Create reproducible sendback preserving the full descriptive audit name."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
NAME='q550_hidden_direction_controlled_perturbation_causal_discrimination_v18_50d_server_sendback.zip'
entries={}
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or 'runtime' in p.relative_to(ROOT).parts or '__pycache__' in p.parts or p.suffix=='.pyc':continue
 if p.name in (NAME,'SHA256SUMS_OUTPUT.json'):continue
 entries[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'root':ROOT.name,'version':'v18.50d','files':entries}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/NAME,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for rel in entries:z.write(ROOT/rel,ROOT.name+'/'+rel)
 z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(ROOT/NAME) as z:
 assert z.testzip() is None
 for rel,dig in entries.items():assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==dig,rel
print(f'Packed {len(entries)}/{len(entries)} members + manifest: {ROOT/NAME}')
