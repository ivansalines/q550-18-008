#!/usr/bin/env python3
"""Authenticate immutable v18.49i sendback and recursively J ancestry."""
from pathlib import Path
import hashlib,json,zipfile,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path));mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def verify():
    info=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    source=ROOT/'inputs/v18_49i_original_server_sendback.zip'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=info['i_sendback_sha256']:raise RuntimeError('Original I sendback hash differs')
    prefix=info['i_root'];base=ROOT/'runtime/verified_i'/prefix
    with zipfile.ZipFile(source) as z:
        if z.testzip():raise RuntimeError('Original I sendback CRC failure')
        manifest=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49i':raise RuntimeError('Wrong parent')
        expected={prefix+'/'+p for p in manifest['files']}|{prefix+'/SHA256SUMS_OUTPUT.json'}
        if set(x for x in z.namelist() if not x.endswith('/'))!=expected:raise RuntimeError('Parent members do not match manifest')
        for p,d in manifest['files'].items():
            if p.startswith('/') or '..' in Path(p).parts:raise RuntimeError('Unsafe parent member')
            raw=z.read(prefix+'/'+p)
            if hashlib.sha256(raw).hexdigest()!=d:raise RuntimeError('Parent mismatch: '+p)
            dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        (base/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    prior=dynamic(base/'scripts/verify_parent.py','j_authentic_i_verify')
    h,g,f,e,d,c,b,a,z,y,j,provenance=prior.verify()
    if not provenance['ancestry_to_J']:raise RuntimeError('J history is not authenticated')
    record={'source_i_sha256':digest,'source_i_members':len(expected),'ancestry_to_J':True}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(record,indent=2)+'\n')
    return base,h,g,f,e,d,c,b,a,z,y,j,record
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
