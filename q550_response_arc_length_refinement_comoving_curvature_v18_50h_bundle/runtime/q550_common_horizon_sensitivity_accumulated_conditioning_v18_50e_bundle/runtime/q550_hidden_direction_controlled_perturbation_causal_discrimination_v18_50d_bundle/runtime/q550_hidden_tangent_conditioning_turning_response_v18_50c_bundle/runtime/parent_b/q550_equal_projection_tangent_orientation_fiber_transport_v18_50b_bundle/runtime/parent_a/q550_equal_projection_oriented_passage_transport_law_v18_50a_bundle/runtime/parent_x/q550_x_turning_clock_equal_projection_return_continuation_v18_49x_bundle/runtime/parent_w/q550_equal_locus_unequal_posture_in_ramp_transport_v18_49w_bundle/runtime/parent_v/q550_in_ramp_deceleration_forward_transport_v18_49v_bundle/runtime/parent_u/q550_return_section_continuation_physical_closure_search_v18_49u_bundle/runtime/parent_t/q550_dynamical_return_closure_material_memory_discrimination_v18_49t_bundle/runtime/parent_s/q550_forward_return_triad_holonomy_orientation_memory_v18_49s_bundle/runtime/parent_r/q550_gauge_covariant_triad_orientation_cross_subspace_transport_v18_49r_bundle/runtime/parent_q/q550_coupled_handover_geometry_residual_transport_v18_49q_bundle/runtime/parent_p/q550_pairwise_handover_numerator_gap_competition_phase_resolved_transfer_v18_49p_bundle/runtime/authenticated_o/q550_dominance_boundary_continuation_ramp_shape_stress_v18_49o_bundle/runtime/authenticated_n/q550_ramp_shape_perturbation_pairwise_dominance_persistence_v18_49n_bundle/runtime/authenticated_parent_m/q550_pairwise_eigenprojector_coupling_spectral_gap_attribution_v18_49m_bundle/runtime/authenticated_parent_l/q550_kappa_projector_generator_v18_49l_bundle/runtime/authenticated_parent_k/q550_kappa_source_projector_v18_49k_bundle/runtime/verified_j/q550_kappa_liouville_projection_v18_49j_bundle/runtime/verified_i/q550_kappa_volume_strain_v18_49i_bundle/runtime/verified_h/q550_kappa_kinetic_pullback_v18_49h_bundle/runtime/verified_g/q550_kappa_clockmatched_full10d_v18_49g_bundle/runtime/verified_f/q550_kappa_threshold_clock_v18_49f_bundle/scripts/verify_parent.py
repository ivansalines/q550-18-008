#!/usr/bin/env python3
"""Strictly verify unchanged E sendback and its authenticated D-to-J ancestry."""
from pathlib import Path
import zipfile,hashlib,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
 spec=importlib.util.spec_from_file_location(name,str(path))
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
 pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
 src=ROOT/'inputs/v18_49e_original_server_sendback.zip'
 if hashlib.sha256(src.read_bytes()).hexdigest()!=pin['parent_e_sha256']:raise RuntimeError('Original E SHA256 mismatch')
 r=pin['parent_e_root'];dst=ROOT/'runtime/verified_e'/r
 with zipfile.ZipFile(src) as z:
  if z.testzip() is not None:raise RuntimeError('E ZIP CRC failed')
  manifest=json.loads(z.read(r+'/SHA256SUMS_OUTPUT.json'))
  if manifest['version']!='v18.49e':raise RuntimeError('Unexpected parent E version')
  expected={r+'/'+x for x in manifest['files']}|{r+'/SHA256SUMS_OUTPUT.json'}
  if {x for x in z.namelist() if not x.endswith('/')}!=expected:raise RuntimeError('E ZIP file membership mismatch')
  for rel,sha in manifest['files'].items():
   p=Path(rel)
   if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe archive member')
   data=z.read(r+'/'+rel)
   if hashlib.sha256(data).hexdigest()!=sha:raise RuntimeError('E member hash mismatch: '+rel)
   out=dst/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(r+'/SHA256SUMS_OUTPUT.json'))
 e_ver=dynamic(dst/'scripts/verify_parent.py','f_parent_e_verifier')
 d,c,b,a,z,y,j,provenance=e_ver.verify()
 if not provenance['history_authenticated_to_J']:raise RuntimeError('Ancestry to J not authenticated')
 info={'parent_e_sha256':pin['parent_e_sha256'],'parent_e_entries':len(manifest['files'])+1,
       'nested_ancestry_authenticated_to_J':True,'root':r}
 (ROOT/'runtime/parent_verification.json').write_text(json.dumps(info,indent=2)+'\n')
 return dst,d,c,b,a,z,y,j,info
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
