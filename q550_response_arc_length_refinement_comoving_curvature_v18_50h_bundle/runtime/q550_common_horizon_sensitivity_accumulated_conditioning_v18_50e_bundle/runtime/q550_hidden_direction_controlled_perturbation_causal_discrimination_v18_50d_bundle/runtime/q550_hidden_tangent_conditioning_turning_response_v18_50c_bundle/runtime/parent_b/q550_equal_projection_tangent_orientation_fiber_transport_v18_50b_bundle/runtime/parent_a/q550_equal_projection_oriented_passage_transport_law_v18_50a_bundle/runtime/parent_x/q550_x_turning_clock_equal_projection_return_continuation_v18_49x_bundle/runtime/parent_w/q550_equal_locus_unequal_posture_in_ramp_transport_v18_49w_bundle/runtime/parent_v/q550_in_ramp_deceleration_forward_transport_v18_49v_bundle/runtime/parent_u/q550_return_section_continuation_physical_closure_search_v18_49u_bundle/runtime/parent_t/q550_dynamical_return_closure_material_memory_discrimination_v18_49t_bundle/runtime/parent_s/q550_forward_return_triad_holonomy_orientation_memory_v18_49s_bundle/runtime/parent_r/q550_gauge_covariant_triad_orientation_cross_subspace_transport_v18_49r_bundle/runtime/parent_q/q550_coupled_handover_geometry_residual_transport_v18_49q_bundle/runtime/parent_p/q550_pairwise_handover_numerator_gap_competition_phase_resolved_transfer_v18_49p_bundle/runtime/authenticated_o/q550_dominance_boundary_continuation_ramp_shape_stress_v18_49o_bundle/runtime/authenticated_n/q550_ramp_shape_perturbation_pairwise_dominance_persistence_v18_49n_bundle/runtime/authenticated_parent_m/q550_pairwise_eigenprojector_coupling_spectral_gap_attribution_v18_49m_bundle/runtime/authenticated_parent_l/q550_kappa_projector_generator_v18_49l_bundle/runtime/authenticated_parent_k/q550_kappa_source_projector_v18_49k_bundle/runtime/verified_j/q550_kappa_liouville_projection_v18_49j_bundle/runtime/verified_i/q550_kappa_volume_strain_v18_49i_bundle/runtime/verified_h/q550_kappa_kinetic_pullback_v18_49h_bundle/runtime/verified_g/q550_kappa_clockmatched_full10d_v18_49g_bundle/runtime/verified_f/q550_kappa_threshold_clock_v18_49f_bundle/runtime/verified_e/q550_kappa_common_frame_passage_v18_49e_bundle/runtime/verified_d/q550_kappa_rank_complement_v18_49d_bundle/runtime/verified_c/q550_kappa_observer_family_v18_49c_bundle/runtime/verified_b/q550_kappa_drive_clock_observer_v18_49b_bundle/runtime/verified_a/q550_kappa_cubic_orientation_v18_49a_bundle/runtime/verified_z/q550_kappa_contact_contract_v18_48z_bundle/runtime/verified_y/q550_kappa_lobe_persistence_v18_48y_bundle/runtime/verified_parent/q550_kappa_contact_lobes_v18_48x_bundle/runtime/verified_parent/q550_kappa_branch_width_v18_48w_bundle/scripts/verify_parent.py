#!/usr/bin/env python3
"""Verify exact, unchanged v18.48v server sendback and recursive ancestry."""
from __future__ import annotations
import hashlib, importlib.util, json, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def load(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(sp);sys.modules[name]=mod;sp.loader.exec_module(mod)
    return mod
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for rel,h in pins['files'].items():
        if sha(ROOT/rel)!=h:raise RuntimeError('Pinned source mismatch: '+rel)
    rootname='q550_kappa_contact_window_v18_48v_bundle'
    src=ROOT/'inputs/v18_48v_original_server_sendback.zip'
    dest=ROOT/'runtime/verified_parent'/rootname
    with zipfile.ZipFile(src) as z:
        if z.testzip():raise RuntimeError('Bad parent ZIP CRC')
        mname=rootname+'/SHA256SUMS_OUTPUT.json'
        manifest=json.loads(z.read(mname))
        if manifest.get('version')!='v18.48v':raise RuntimeError('Unexpected original server parent version')
        expected={rootname+'/'+r for r in manifest['files']}|{mname}
        if set(x for x in z.namelist() if not x.endswith('/'))!=expected:raise RuntimeError('Parent archive hierarchy differs from manifest')
        for rel,h in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts or any(s in ('runtime','__pycache__') for s in p.parts):
                raise RuntimeError('Unsafe archive member: '+rel)
            b=z.read(rootname+'/'+rel)
            if hashlib.sha256(b).hexdigest()!=h:raise RuntimeError('Parent manifest mismatch: '+rel)
            target=dest/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(mname))
    u,t,s,r,j,ancestry=load(dest/'scripts/verify_parent.py','v_q550_parent_verify').verify()
    for name in ('physical_math.py','transversality_math.py'):
        if (dest/'reference'/name).read_bytes()!=(ROOT/'reference'/name).read_bytes():
            raise RuntimeError('Original physical source changed: '+name)
    if (dest/'reference/original_drive_math.py').read_bytes()!=(ROOT/'reference/original_drive_math.py').read_bytes():
        raise RuntimeError('Original analytic control source changed')
    if (dest/'scripts/ramp_math.py').read_bytes()!=(ROOT/'reference/parent_ramp_math.py').read_bytes():
        raise RuntimeError('Parent scalar width definition changed')
    meta={'parent_v_sendback_sha256':sha(src),'parent_manifest_sha256':sha(dest/'SHA256SUMS_OUTPUT.json'),
          'parent_v_manifest_files':len(manifest['files']),
          'original_11D_history_sha256':sha(j/'runtime/physical_paths.npz'),
          'recursive_ancestry_sha_verified':True}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    return dest,u,t,s,r,j,meta
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
