#!/usr/bin/env python3
"""Authenticate v18.49o sendback and recursively authenticate its parent chain."""
from pathlib import Path
import hashlib,importlib.util,json,zipfile
ROOT=Path(__file__).resolve().parents[1]

def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    mod=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs'/pins['parent_file']
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if digest!=pins['parent_sha256']:raise RuntimeError('v18.49o original ZIP checksum mismatch')
    prefix=pins['parent_root']
    dest=ROOT/'runtime/authenticated_o'/prefix
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:raise RuntimeError('Parent ZIP CRC failure')
        mani=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if mani['version']!='v18.49o' or mani['root']!=prefix or len(mani['files'])!=pins['manifest_count']:
            raise RuntimeError('Parent manifest identity/cardinality mismatch')
        members={n for n in z.namelist() if not n.endswith('/')}
        expected={prefix+'/'+n for n in mani['files']} | {prefix+'/SHA256SUMS_OUTPUT.json'}
        if members!=expected:raise RuntimeError('Parent archive has missing or extra files')
        for rel,sha in mani['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe parent path')
            b=z.read(prefix+'/'+rel)
            if hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError('Parent manifest digest mismatch '+rel)
            target=dest/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    for name,sha in pins['inherited_helper_sha256'].items():
        test=ROOT/'scripts'/('parent_o_experiment.py' if name=='run_audit.py' else name)
        if hashlib.sha256(test.read_bytes()).hexdigest()!=sha:raise RuntimeError('Inherited mathematical code differs: '+name)
    old=dynamic(dest/'scripts/verify_parent.py','p_verified_o_parent')
    nroot,mroot,nodes,previous=old.verify()
    if not previous['upstream_ancestry_to_v18_48j']:raise RuntimeError('Missing 48j ancestry')
    report={'source':'v18.49o authenticated server ZIP','sha256':digest,'manifest_entries':len(mani['files']),
            'n_m_l_k_j_genealogy_authenticated':True,'parent_report':previous}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return nroot,mroot,nodes,report
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
