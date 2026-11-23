"""Package immutable genealogy, executed Python, numeric outputs and SHA-256 manifest."""
import hashlib,json,zipfile,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=sorted(p for p in root.rglob('*') if p.is_file() and not any(d in p.parts for d in ('runtime','__pycache__')) and p.name not in ('sendback.zip',root.name+'_sendback.zip','SHA256SUMS_OUTPUT.json'))
manifest={'version':'v18.49m','root':root.name,'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(root/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(root/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[root/'SHA256SUMS_OUTPUT.json']:z.write(p,arcname=root.name+'/'+str(p.relative_to(root)))
with zipfile.ZipFile(root/'sendback.zip') as z:
 assert z.testzip() is None
 assert {i for i in z.namelist() if not i.endswith('/')}=={root.name+'/'+s for s in manifest['files']}|{root.name+'/SHA256SUMS_OUTPUT.json'}
shutil.copy2(root/'sendback.zip',root/(root.name+'_sendback.zip'))
print('Authentic sendback created:',len(files),'files and manifest, also descriptive filename')
