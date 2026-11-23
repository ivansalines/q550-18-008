#!/usr/bin/env python3
"""Authenticate the immutable v18.48n parent and recursively authenticate v18.48m/k/j/i/h."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify():
 pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
 archive=ROOT/'inputs/v18_48n_original_server_sendback.zip'
 if sha(archive)!=pin['v18_48n_original_server_sha256']:raise RuntimeError('v18.48n original SHA mismatch')
 root='q550_kappa_dance_rhythm_v18_48n_bundle/'
 with zipfile.ZipFile(archive) as z:
  if z.testzip():raise RuntimeError('Corrupt v18.48n ZIP')
  manifest=json.loads(z.read(root+'SHA256SUMS_OUTPUT.json'))
  if manifest.get('version')!='v18.48n' or manifest.get('file_count')!=26:raise RuntimeError('Unexpected v18.48n manifest')
  members={name for name in z.namelist() if not name.endswith('/')}
  expected={root+p for p in manifest['files']}|{root+'SHA256SUMS_OUTPUT.json'}
  if members!=expected:raise RuntimeError('Unexpected parent members')
  dest=ROOT/'runtime/parent_n'
  for rel,h in manifest['files'].items():
   raw=z.read(root+rel)
   if hashlib.sha256(raw).hexdigest()!=h:raise RuntimeError('Corrupted original member: '+rel)
   target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  mpath=dest/'SHA256SUMS_OUTPUT.json';mpath.write_bytes(z.read(root+'SHA256SUMS_OUTPUT.json'))
 spec=importlib.util.spec_from_file_location('v18_48n_verifier',dest/'scripts/verify_parent.py')
 m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 ancestor=m.verify()
 if sha(dest/'inputs/v18_48m_original_server_sendback.zip')!=pin['v18_48m_original_server_sha256']:
  raise RuntimeError('Original v18.48m parent mismatch')
 physical=dest/'runtime/parent_m/runtime/parent_k/runtime/parent_j/runtime/physical_paths.npz'
 if sha(physical)!=pin['physical_paths_sha256']:raise RuntimeError('Physical history SHA mismatch')
 result=dict(v18_48n_sha256=sha(archive),parent_manifest_members=len(manifest['files']),ancestry=ancestor,physical_paths_sha256=sha(physical))
 p=ROOT/'runtime/provenance.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
