"""Self-contained, SHA256 authenticated response preserving original E bytes."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if any(part in rel.parts for part in ('runtime','__pycache__','.git','.pytest_cache')):continue
 if p.name in ('sendback.zip','SHA256SUMS_OUTPUT.json'):continue
 if rel.parts[0] in ('results','inputs','scripts','tests') or len(rel.parts)==1:
  files.append(p)
manifest={'version':'v18.49f','parent':'unchanged SHA-authenticated server E original, nested ancestry D..J',
 'files':{p.relative_to(R).as_posix():sha(p) for p in files}}
(R/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(R/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[R/'SHA256SUMS_OUTPUT.json']:
  z.write(p,R.name+'/'+p.relative_to(R).as_posix())
with zipfile.ZipFile(R/'sendback.zip') as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)+1
 for path,digest in manifest['files'].items():
  assert hashlib.sha256(z.read(R.name+'/'+path)).hexdigest()==digest
print(f'v18.49f sendback {len(files)+1} entries, CRC and SHA256 PASS, size={(R/"sendback.zip").stat().st_size}')
