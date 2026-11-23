#!/usr/bin/env python3
"""Build versioned full descriptive sendback archive with hashes and authentic genealogy."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
ZIPNAME='q550_hidden_tangent_conditioning_turning_response_v18_50c_server_sendback.zip'
# Exclude transient runtime and archive products. The input ancestral ZIP is included.
entries={}
for path in sorted(ROOT.rglob('*')):
 if not path.is_file() or 'runtime' in path.relative_to(ROOT).parts or '__pycache__' in path.parts:continue
 if path.name in (ZIPNAME,'SHA256SUMS_OUTPUT.json') or path.suffix=='.pyc':continue
 entries[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
manifest={'version':'v18.50c','root':ROOT.name,'files':entries}
(ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
dest=ROOT/ZIPNAME
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for rel in entries:z.write(ROOT/rel,ROOT.name+'/'+rel)
 z.write(ROOT/'SHA256SUMS_OUTPUT.json',ROOT.name+'/SHA256SUMS_OUTPUT.json')
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 pre=ROOT.name+'/'
 for name,dig in entries.items():
  assert hashlib.sha256(z.read(pre+name)).hexdigest()==dig,name
print(f'Packed {dest} ({len(entries)}/{len(entries)} hashes verified)')
