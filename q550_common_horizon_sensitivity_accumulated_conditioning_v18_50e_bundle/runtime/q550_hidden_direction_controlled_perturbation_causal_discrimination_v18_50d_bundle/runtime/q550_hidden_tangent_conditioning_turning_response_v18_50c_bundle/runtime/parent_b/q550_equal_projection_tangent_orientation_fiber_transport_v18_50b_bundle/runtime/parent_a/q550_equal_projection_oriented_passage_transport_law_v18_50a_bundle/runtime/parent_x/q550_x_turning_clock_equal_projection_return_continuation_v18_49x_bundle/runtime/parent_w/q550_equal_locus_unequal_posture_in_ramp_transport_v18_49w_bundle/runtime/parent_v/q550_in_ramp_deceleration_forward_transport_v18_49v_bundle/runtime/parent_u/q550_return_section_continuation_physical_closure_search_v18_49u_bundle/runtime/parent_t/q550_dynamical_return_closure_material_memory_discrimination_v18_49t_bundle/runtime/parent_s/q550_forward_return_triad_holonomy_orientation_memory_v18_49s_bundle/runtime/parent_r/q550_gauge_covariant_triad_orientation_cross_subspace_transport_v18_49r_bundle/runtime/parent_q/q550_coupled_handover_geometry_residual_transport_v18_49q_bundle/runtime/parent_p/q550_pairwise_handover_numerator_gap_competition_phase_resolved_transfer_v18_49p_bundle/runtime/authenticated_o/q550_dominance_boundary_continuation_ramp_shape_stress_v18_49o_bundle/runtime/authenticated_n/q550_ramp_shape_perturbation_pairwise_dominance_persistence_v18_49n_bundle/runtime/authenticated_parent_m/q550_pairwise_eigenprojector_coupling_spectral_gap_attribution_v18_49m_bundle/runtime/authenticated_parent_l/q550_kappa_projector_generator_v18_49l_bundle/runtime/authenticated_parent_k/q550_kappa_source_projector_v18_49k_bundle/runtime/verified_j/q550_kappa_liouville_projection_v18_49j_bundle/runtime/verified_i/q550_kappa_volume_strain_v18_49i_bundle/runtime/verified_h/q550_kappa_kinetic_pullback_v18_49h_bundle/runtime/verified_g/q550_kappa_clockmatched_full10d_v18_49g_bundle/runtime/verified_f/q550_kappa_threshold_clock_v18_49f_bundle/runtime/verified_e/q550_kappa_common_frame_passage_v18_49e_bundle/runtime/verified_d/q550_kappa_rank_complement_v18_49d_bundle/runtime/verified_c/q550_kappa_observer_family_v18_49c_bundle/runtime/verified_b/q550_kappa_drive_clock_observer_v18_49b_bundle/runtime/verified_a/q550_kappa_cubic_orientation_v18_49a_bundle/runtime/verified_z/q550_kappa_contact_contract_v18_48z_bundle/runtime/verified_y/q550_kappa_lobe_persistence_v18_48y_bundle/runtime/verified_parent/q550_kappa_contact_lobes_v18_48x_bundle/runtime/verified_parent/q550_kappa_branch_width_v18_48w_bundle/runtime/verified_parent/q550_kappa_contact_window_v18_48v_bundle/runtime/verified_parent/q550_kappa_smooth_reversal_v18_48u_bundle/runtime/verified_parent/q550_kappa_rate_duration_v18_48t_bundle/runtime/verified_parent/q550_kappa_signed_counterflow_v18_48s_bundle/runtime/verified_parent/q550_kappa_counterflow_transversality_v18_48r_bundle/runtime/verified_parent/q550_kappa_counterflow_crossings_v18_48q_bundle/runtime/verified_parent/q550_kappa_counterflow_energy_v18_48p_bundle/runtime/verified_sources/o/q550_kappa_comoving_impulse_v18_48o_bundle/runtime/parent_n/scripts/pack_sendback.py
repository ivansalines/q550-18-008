#!/usr/bin/env python3
"""Create authenticated original-result sendback with immutable inputs."""
from pathlib import Path
import hashlib,json,platform,zipfile,sys
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'sendback.zip','SHA256SUMS_OUTPUT.json'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 keep=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or 'runtime' in p.relative_to(ROOT).parts or p.name in EXCLUDE or '__pycache__' in p.parts:continue
  if p.relative_to(ROOT).parts[0] not in ('inputs','scripts','tests','results','reference') and p.name not in ('README.md','SCIENTIFIC_DECISION_RULES.md','ENVIRONMENT.json','requirements.txt','run_on_server.sh'):continue
  keep.append(p)
 manifest=dict(version='v18.48n',file_count=len(keep),files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in keep})
 (ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in [*keep,ROOT/'SHA256SUMS_OUTPUT.json']:z.write(p,arcname=f'{ROOT.name}/{p.relative_to(ROOT)}')
 with zipfile.ZipFile(ROOT/'sendback.zip') as z:
  assert all(sha(z.read(f'{ROOT.name}/{rel}'))==h for rel,h in manifest['files'].items())
 print('v18.48n sendback manifest:',len(keep),'members; SHA256:',sha((ROOT/'sendback.zip').read_bytes()))
if __name__=='__main__':main()
