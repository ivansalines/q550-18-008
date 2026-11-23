#!/usr/bin/env python3
"""Pin, extract and recursively authenticate exact original server genealogy."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for r,h in pins['files'].items():
        if sha((ROOT/r).read_bytes())!=h:raise RuntimeError('Pinned original changed: '+r)
    src=ROOT/'inputs/v18_48w_original_server_sendback.zip'
    root='q550_kappa_branch_width_v18_48w_bundle'
    dest=ROOT/'runtime/verified_parent'/root
    with zipfile.ZipFile(src) as z:
        if z.testzip():raise RuntimeError('Original server archive failed CRC')
        man=json.loads(z.read(root+'/SHA256SUMS_OUTPUT.json'))
        if man['version']!='v18.48w':raise RuntimeError('Parent version mismatch')
        expect={root+'/'+r for r in man['files']}|{root+'/SHA256SUMS_OUTPUT.json'}
        if set(n for n in z.namelist() if not n.endswith('/'))!=expect:
            raise RuntimeError('Changed parent archive file hierarchy')
        for r,h in man['files'].items():
            path=Path(r)
            if path.is_absolute() or '..' in path.parts or any(part in ('runtime','__pycache__') for part in path.parts):
                raise RuntimeError('Unsafe parent entry: '+r)
            data=z.read(root+'/'+r)
            if sha(data)!=h:raise RuntimeError('Parent SHA mismatch: '+r)
            target=dest/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(root+'/SHA256SUMS_OUTPUT.json'))
    verified=load(dest/'scripts/verify_parent.py','x_w_verify').verify()
    v,u,t,s,r,j,_=verified
    for name in ('physical_math.py','transversality_math.py','original_drive_math.py'):
        if (ROOT/'reference'/name).read_bytes()!=(dest/'reference'/name).read_bytes():
            raise RuntimeError('Historical mathematical source changed: '+name)
    if (ROOT/'reference/parent_ramp_math.py').read_bytes()!=(dest/'reference/parent_ramp_math.py').read_bytes():
        raise RuntimeError('Historical ramp model changed')
    prov={'original_v18_48w_server_sha256':sha(src.read_bytes()),
          'original_parent_manifest_entries':len(man['files']),
          'original_11D_physical_path_sha256':sha((j/'runtime/physical_paths.npz').read_bytes()),
          'recursive_ancestry_SHA_verified':True}
    (ROOT/'runtime/provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    return dest,v,u,t,s,r,j,prov
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
