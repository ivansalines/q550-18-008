#!/usr/bin/env python3
"""Package immutable input lineage plus exact generator, test and result files."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'sendback.zip','SHA256SUMS_OUTPUT.json'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 paths=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or 'runtime' in p.relative_to(ROOT).parts or '__pycache__' in p.parts or p.name in EXCLUDE:continue
  if p.relative_to(ROOT).parts[0] not in ('inputs','scripts','tests','results','reference') and p.name not in ('README.md','SCIENTIFIC_DECISION_RULES.md','ENVIRONMENT.json','requirements.txt','run_on_server.sh'):continue
  paths.append(p)
 manifest={'version':'v18.48o','file_count':len(paths),'files':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}}
 (ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(ROOT/'sendback.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in [*paths,ROOT/'SHA256SUMS_OUTPUT.json']:z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
 with zipfile.ZipFile(ROOT/'sendback.zip') as z:
  assert all(sha(z.read(ROOT.name+'/'+p))==h for p,h in manifest['files'].items())
 print('v18.48o manifest:',len(paths),'files, archive sha256',sha((ROOT/'sendback.zip').read_bytes()))
if __name__=='__main__':main()
