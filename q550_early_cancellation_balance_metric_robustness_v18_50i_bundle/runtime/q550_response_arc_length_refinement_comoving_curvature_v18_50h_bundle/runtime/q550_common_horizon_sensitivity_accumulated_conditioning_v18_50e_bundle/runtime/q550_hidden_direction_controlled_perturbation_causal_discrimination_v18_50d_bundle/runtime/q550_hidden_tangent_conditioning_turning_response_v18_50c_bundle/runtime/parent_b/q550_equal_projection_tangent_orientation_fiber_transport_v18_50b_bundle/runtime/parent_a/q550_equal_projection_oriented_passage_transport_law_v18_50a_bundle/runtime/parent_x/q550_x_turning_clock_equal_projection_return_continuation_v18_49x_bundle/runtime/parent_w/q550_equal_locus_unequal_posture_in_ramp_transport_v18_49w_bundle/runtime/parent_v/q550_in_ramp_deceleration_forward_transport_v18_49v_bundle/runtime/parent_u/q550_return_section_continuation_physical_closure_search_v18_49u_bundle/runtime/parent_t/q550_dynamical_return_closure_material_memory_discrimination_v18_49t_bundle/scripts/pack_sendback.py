from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
manifest={}
for f in sorted(ROOT.rglob('*')):
    if not f.is_file() or f.name.endswith('.pyc') or '__pycache__' in f.parts or 'runtime' in f.relative_to(ROOT).parts or f.name=='SHA256SUMS_OUTPUT.json':continue
    manifest[f.relative_to(ROOT).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps({'version':'v18.49t','root':ROOT.name,'files':manifest},indent=2)+'\n')
out=ROOT.parent/(ROOT.name+'_sendback.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for rel in manifest:z.write(ROOT/rel,ROOT.name+'/'+rel)
    z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
print('Packed verified sendback',out,'members',len(manifest)+1)
