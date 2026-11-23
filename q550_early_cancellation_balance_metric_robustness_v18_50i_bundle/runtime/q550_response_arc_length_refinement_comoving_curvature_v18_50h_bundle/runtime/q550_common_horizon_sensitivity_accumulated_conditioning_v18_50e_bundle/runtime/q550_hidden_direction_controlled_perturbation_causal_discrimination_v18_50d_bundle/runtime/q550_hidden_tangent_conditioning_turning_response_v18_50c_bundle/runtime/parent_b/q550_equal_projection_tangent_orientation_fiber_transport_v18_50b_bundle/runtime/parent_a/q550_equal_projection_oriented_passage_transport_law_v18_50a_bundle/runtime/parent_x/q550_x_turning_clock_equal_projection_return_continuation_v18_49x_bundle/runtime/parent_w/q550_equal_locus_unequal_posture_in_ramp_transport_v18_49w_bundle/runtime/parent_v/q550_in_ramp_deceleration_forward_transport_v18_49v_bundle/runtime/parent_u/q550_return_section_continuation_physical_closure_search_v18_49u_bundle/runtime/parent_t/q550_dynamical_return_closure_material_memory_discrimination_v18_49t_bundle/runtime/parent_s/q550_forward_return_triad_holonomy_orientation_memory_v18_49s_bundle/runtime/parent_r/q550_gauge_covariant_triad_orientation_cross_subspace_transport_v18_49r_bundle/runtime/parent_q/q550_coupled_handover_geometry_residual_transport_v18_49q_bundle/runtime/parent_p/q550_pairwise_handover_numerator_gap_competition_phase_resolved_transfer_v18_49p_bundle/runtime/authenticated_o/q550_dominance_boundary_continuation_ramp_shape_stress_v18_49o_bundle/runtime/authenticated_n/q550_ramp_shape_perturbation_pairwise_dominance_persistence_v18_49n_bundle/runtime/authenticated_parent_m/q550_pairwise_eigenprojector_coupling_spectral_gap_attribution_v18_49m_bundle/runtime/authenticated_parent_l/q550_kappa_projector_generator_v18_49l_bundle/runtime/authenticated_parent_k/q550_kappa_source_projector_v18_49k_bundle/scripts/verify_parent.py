#!/usr/bin/env python3
"""Verify exact parent J sendback and its recursive provenance before any physics."""
from pathlib import Path
import hashlib,json,zipfile,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path)); mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def verify():
    info=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    source=ROOT/'inputs/v18_49j_original_server_sendback.zip'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=info['j_sendback_sha256']:raise RuntimeError('Parent J archive SHA-256 mismatch')
    prefix=info['j_root'];base=ROOT/'runtime/verified_j'/prefix
    with zipfile.ZipFile(source) as z:
        if z.testzip():raise RuntimeError('Parent J archive CRC error')
        manifest=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49j':raise RuntimeError('Wrong parent version')
        listed={prefix+'/'+p for p in manifest['files']}|{prefix+'/SHA256SUMS_OUTPUT.json'}
        if {p for p in z.namelist() if not p.endswith('/')}!=listed:
            raise RuntimeError('Unexpected parent members')
        for p,d in manifest['files'].items():
            if p.startswith('/') or '..' in Path(p).parts:raise RuntimeError('Unsafe parent member')
            raw=z.read(prefix+'/'+p)
            if hashlib.sha256(raw).hexdigest()!=d:raise RuntimeError('Parent member SHA-256 mismatch: '+p)
            dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        (base/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    prior=dynamic(base/'scripts/verify_parent.py','k_authenticated_j_verifier')
    i,h,g,f,e,d,c,b,a,z,y,j,provenance=prior.verify()
    if not provenance['ancestry_to_J']:raise RuntimeError('Broken genealogy before J')
    record={'source_j_sha256':digest,'source_j_members':len(listed),'ancestry_to_v18_48j':True}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(record,indent=2)+'\n')
    return base,i,h,g,f,e,d,c,b,a,z,y,j,record
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
