"""Package generated results + executable scripts, linked to pinned input ancestry."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
manifest={}
for p in root.rglob('*'):
 if not p.is_file() or 'runtime' in p.relative_to(root).parts or p.name in ('SHA256SUMS_OUTPUT.json','sendback.zip') or '__pycache__' in p.parts:continue
 manifest[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
obj={'version':'v18.49u','root':root.name,'files':dict(sorted(manifest.items()))}
(root/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(obj,indent=2)+'\n')
with zipfile.ZipFile(root/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for name in obj['files']:z.write(root/name,root.name+'/'+name)
 z.write(root/'SHA256SUMS_OUTPUT.json',root.name+'/SHA256SUMS_OUTPUT.json')
print('Packaged',root/'sendback.zip','entries',len(manifest))
