#!/usr/bin/env python3
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files={}
for p in ROOT.rglob('*'):
 if p.is_file() and not any(x in ('runtime','__pycache__') for x in p.relative_to(ROOT).parts) and p.name not in ('SHA256SUMS_OUTPUT.json','sendback.zip'):
  files[p.relative_to(ROOT).as_posix()]=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
manifest={'version':'v18.49v','root':ROOT.name,'files':dict(sorted(files.items()))}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for relative in list(manifest['files'])+['SHA256SUMS_OUTPUT.json']:
  z.write(ROOT/relative,ROOT.name+'/'+relative)
print('v18.49v sendback packed:',len(files),'source files; zip entries verified by source SHA manifest')
