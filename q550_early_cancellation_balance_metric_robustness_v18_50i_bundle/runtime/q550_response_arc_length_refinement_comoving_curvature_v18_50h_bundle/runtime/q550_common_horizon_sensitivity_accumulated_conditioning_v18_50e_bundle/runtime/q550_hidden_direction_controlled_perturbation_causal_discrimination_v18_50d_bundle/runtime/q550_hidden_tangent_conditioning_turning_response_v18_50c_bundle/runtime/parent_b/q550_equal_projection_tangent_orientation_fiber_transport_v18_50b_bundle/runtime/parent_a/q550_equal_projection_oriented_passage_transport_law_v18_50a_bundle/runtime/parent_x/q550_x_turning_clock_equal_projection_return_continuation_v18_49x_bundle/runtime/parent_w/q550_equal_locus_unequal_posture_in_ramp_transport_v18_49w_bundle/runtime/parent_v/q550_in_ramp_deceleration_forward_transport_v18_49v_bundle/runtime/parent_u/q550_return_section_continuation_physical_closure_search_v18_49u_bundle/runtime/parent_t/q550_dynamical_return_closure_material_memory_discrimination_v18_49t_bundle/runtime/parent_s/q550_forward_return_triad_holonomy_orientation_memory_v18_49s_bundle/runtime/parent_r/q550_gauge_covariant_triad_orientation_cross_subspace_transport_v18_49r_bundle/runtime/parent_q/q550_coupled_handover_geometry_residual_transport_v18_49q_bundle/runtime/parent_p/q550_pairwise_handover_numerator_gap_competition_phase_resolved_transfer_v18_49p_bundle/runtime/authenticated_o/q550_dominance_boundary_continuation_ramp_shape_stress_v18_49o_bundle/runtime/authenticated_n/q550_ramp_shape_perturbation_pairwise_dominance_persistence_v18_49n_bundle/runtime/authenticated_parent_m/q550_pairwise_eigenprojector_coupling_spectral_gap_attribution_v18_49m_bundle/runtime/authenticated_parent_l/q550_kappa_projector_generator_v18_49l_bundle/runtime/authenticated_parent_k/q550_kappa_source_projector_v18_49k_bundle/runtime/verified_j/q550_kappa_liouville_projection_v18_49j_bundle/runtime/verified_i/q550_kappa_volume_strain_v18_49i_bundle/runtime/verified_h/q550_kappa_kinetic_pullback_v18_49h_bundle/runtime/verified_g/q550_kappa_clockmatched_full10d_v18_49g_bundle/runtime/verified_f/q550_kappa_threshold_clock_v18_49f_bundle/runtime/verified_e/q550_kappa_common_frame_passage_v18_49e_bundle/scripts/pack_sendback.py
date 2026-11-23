"""Produce self-contained SHA256-verifiable sendback with original D byte-identical."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for p in ROOT.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(ROOT)
 if any(s in rel.parts for s in ('runtime','__pycache__','.git','.pytest_cache')):continue
 if p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json'):continue
 if rel.parts[0] in ('scripts','tests','inputs','results') or len(rel.parts)==1:files.append(p)
files=sorted(files)
manifest={'version':'v18.49e','parent':'unaltered original server D sendback; nested genealogy authenticated to J',
          'files':{p.relative_to(ROOT).as_posix():sha(p) for p in files}}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[ROOT/'SHA256SUMS_OUTPUT.json']:
  z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/'sendback.zip') as z:
 assert z.testzip() is None and len(z.namelist())==len(files)+1
 for rel,s in manifest['files'].items():
  assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==s
print('v18.49e sendback:',len(files)+1,'authenticated entries', (ROOT/'sendback.zip').stat().st_size,'bytes')
