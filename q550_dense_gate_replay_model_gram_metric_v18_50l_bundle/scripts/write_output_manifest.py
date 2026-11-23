#!/usr/bin/env python3
import hashlib,json,platform
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'results').glob('*')) if p.is_file()}
M={'version':'v18.50l','mode':'per-execution outputs','python':platform.python_version(),'file_sha256':d}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(M,indent=2)+'\n')
print('OUTPUT MANIFEST WRITTEN',len(d),flush=True)
