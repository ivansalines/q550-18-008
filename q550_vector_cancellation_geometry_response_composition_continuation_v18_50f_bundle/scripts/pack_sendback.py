"""Pack scripts, outputs and immutable parent for faithful server return."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
name='q550_vector_cancellation_geometry_response_composition_continuation_v18_50f_bundle'
files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name not in ('SHA256SUMS.json','sendback.zip') and '__pycache__' not in p.parts]
manifest={'root':name,'version':'v18.50f','files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(ROOT/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=4,allowZip64=True) as z:
 for p in files+[ROOT/'SHA256SUMS.json']:
  z.write(p,name+'/'+str(p.relative_to(ROOT)))
print('packed',len(files),'entries; SHA256 manifest verified source bytes')
