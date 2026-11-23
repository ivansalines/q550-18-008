from pathlib import Path
import zipfile,hashlib,json
root=Path(__file__).resolve().parents[1]
inputs=root/'inputs'
# Exclude runtime caches; preserve complete authentic input archive and own scripts/results.
files=sorted(p for p in root.rglob('*') if p.is_file() and ('runtime' not in p.relative_to(root).parts) and ('__pycache__' not in p.parts) and p.name not in {'SHA256SUMS.json','sendback.zip'} and not p.name.endswith('.pyc'))
manifest={'root':root.name,'version':'v18.50i','files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(root/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(root/'SHA256SUMS.json')
with zipfile.ZipFile(root/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for p in files:z.write(p,arcname=root.name+'/'+str(p.relative_to(root)))
print('Packed',len(manifest['files']),'files to',root/'sendback.zip')
