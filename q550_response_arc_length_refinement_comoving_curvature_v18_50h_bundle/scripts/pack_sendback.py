"""Create a faithful sendback zip with executable script and digest ledger."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
files=[p for p in ROOT.rglob('*') if p.is_file() and 'runtime' not in p.relative_to(ROOT).parts and p.name not in ('SHA256SUMS.json','sendback.zip')]
manifest={'root':ROOT.name,'version':'v18.50h','files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
(ROOT/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files)+[ROOT/'SHA256SUMS.json']:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
print('Packed',len(files),'files and SHA256 manifest')
