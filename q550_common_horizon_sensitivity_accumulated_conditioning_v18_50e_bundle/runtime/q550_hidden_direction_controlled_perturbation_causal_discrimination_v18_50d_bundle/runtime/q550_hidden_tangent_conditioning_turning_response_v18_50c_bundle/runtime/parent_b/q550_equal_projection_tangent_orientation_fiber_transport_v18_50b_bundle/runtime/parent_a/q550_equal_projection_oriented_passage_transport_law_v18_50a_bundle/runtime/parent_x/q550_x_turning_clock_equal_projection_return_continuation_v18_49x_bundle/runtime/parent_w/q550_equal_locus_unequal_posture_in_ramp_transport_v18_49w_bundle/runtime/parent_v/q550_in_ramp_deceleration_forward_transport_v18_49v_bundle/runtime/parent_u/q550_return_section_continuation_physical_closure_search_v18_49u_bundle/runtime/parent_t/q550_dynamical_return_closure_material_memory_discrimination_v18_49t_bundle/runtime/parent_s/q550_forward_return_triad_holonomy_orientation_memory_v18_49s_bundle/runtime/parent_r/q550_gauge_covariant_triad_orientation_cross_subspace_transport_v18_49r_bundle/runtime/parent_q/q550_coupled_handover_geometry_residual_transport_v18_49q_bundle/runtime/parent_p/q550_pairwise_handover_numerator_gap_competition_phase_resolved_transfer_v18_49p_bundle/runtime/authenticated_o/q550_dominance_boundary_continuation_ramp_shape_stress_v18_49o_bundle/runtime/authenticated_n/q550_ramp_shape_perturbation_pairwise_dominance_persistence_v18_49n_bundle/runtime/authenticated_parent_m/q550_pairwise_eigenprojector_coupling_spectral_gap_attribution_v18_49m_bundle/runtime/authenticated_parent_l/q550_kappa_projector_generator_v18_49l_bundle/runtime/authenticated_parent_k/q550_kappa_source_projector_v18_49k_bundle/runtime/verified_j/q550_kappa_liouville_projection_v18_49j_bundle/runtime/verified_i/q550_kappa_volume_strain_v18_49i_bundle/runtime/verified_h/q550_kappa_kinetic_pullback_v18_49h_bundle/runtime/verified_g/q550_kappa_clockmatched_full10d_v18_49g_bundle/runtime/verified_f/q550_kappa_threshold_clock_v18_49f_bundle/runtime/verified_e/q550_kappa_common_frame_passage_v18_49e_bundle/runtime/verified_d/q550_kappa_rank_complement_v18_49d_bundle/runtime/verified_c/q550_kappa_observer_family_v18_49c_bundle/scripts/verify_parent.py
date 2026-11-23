#!/usr/bin/env python3
"""SHA-256 fail-closed authentication of original server B and nested J ancestry."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def dynamic(file,name):
 spec=importlib.util.spec_from_file_location(name,str(file));mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def verify():
 pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
 arc=ROOT/'inputs/v18_49b_original_server_sendback.zip'
 if sha(arc.read_bytes())!=pins['parent_B_sha256']:raise RuntimeError('Original server B digest mismatch')
 for rec in pins['reference_files']:
  if sha((ROOT/rec['path']).read_bytes())!=rec['sha256']:raise RuntimeError('Source copy mutated: '+rec['path'])
 parent=pins['original_root'];dst=ROOT/'runtime/verified_b'/parent
 with zipfile.ZipFile(arc) as z:
  if z.testzip() is not None:raise RuntimeError('ZIP CRC failed')
  m=json.loads(z.read(parent+'/SHA256SUMS_OUTPUT.json'))
  if m.get('version')!='v18.49b':raise RuntimeError('Wrong parent version')
  expected={parent+'/'+k for k in m['files']}|{parent+'/SHA256SUMS_OUTPUT.json'}
  actual={n for n in z.namelist() if not n.endswith('/')}
  if expected!=actual:raise RuntimeError(f'Archive hierarchy/membership mismatches: {len(expected)} vs {len(actual)}')
  for rel,digest in m['files'].items():
   rp=Path(rel)
   if rp.is_absolute() or '..' in rp.parts or '__pycache__' in rp.parts or 'runtime' in rp.parts:raise RuntimeError('Unsafe member '+rel)
   raw=z.read(parent+'/'+rel)
   if sha(raw)!=digest:raise RuntimeError('Invalid B member hash '+rel)
   dest=dst/rp;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(parent+'/SHA256SUMS_OUTPUT.json'))
 for src,new in [('reference/physical_math.py','reference/physical_math.py'),('reference/parent_ramp_math.py','reference/parent_ramp_math.py'),('reference/y_original_run_audit.py','reference/y_original_run_audit.py'),('reference/structural_jet.py','reference/structural_jet.py'),('scripts/observer_math.py','reference/parent_observer_math.py')]:
  if (dst/src).read_bytes()!=(ROOT/new).read_bytes():raise RuntimeError('Mismatch vs authenticated B source '+src)
 older=dynamic(dst/'scripts/verify_parent.py','v1849b_authenticated_verifier')
 aroot,zroot,yroot,jroot,parent_record=older.verify()
 record={'source':'original user-server B sendback','parent_B_sha256':pins['parent_B_sha256'],'parent_B_files':len(m['files']),
         'nested_original_genealogy_authenticated_to_J':bool(parent_record['ancestry_verified_to_J'])}
 (ROOT/'runtime').mkdir(exist_ok=True)
 (ROOT/'runtime/parent_verification.json').write_text(json.dumps(record,indent=2)+'\n')
 return dst,aroot,zroot,yroot,jroot,record
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
