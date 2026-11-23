"""Verify authenticated v18.50b ancestry, including nested v18.50a and predecessors."""
import json,hashlib,zipfile,sys,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT='q550_equal_projection_tangent_orientation_fiber_transport_v18_50b_bundle'
FILE='q550_equal_projection_tangent_orientation_fiber_transport_v18_50b_authenticated_server_sendback.zip'
PIN='7a02c25ab637b2a0d2b9715b4ed43cf91306927f5e1ad4453276a979718e8204'
def digest(b):return hashlib.sha256(b).hexdigest()
def verify():
 src=ROOT/'inputs'/FILE
 if digest(src.read_bytes())!=PIN:raise RuntimeError('Parent v18.50b whole-ZIP SHA mismatch')
 dest=ROOT/'runtime/parent_b'/PARENT
 with zipfile.ZipFile(src) as z:
  if z.testzip() is not None:raise RuntimeError('v18.50b ZIP CRC error')
  pre=PARENT+'/'
  manifest=json.loads(z.read(pre+'SHA256SUMS_OUTPUT.json'))
  if manifest['root']!=PARENT or manifest['version']!='v18.50b':raise RuntimeError('wrong parent manifest')
  names={pre+k for k in manifest['files']}|{pre+'SHA256SUMS_OUTPUT.json'}
  if set(z.namelist())!=names:raise RuntimeError('Unexpected parent ZIP members')
  for rel,d in manifest['files'].items():
   p=Path(rel)
   if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe archive path')
   b=z.read(pre+rel)
   if digest(b)!=d:raise RuntimeError('Parent SHA mismatch '+rel)
   f=dest/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pre+'SHA256SUMS_OUTPUT.json'))
 sys.path.insert(0,str(dest/'scripts'))
 spec=importlib.util.spec_from_file_location('v18_50c_parent_b_verifier',dest/'scripts/verify_parent_a.py')
 mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 aroot,arpt,xroot,anc=mod.verify()
 report=json.loads((dest/'results/report.json').read_text())
 if report['counts']['authenticated_equal_x_passages_replayed']!=34 or report['counts']['failed_cases']!=0:
  raise RuntimeError('Unexpected v18.50b parent count/status')
 return dest,report,{'whole_zip_sha256':PIN,'parent_manifest_verified':len(manifest['files']),
                     'recursive_parent_verified':anc}
