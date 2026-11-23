#!/usr/bin/env python3
"""Verify unchanged v18.49d server data and its full nested genealogy to J."""
import hashlib, json, zipfile, importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs/v18_49d_original_server_sendback.zip'
    actual=hashlib.sha256(src.read_bytes()).hexdigest()
    if actual!=pin['parent_d_sha256']:raise RuntimeError('Original D SHA256 mismatch')
    r=pin['parent_d_root'];dst=ROOT/'runtime/verified_d'/r
    with zipfile.ZipFile(src) as z:
        if z.testzip():raise RuntimeError('Parent D ZIP CRC failure')
        entries={x for x in z.namelist() if not x.endswith('/')}
        manifest=json.loads(z.read(r+'/SHA256SUMS_OUTPUT.json'))
        if manifest.get('version')!='v18.49d':raise RuntimeError('Unexpected version')
        expected={r+'/'+x for x in manifest['files']}|{r+'/SHA256SUMS_OUTPUT.json'}
        if entries!=expected:raise RuntimeError('Parent D archive membership mismatch')
        for rel,sha in manifest['files'].items():
            rp=Path(rel)
            if rp.is_absolute() or '..' in rp.parts:raise RuntimeError('Unsafe path')
            raw=z.read(r+'/'+rel)
            if hashlib.sha256(raw).hexdigest()!=sha:raise RuntimeError('D member hash mismatch '+rel)
            path=dst/rp;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(r+'/SHA256SUMS_OUTPUT.json'))
    dver=dynamic(dst/'scripts/verify_parent.py','e_original_d_verifier')
    c,b,a,z,y,j,p=dver.verify()
    if not p['nested_original_genealogy_authenticated_to_J']:raise RuntimeError('Original history not verified')
    info={'parent_d_sha256':actual,'parent_d_member_count':len(manifest['files']),
          'history_authenticated_to_J':True,'source':'unaltered server D sendback'}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(info,indent=2)+'\n')
    return dst,c,b,a,z,y,j,info
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
