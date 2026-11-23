#!/usr/bin/env python3
"""Hash generated results separately from immutable sources."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
res=R/'results'
paths=sorted(p for p in res.iterdir() if p.is_file() and p.suffix in ('.json','.csv','.png') and p.name!='SHA256SUMS_OUTPUT.json')
if not (res/'report.json').is_file():raise RuntimeError('Only a preflight was run; no full physical audit report')
manifest={'version':'v18.50o','mode':'regenerated','file_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print('v18.50o OUTPUT MANIFEST WRITTEN',len(paths))
