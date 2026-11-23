#!/usr/bin/env python3
"""Verify C source byte-for-byte, complete nested provenance and hierarchy."""
from __future__ import annotations
import hashlib, importlib.util, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def dynamic(file,name):
    spec=importlib.util.spec_from_file_location(name,str(file))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def verify():
    record=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    arc=ROOT/'inputs/v18_49c_original_server_sendback.zip'
    digest=hashlib.sha256(arc.read_bytes()).hexdigest()
    if digest!=record['parent_c_sha256']:raise RuntimeError('Parent C SHA mismatch')
    root_name=record['parent_c_root']
    dst=ROOT/'runtime/verified_c'/root_name
    with zipfile.ZipFile(arc) as z:
        if z.testzip():raise RuntimeError('Parent C CRC failed')
        manifest=json.loads(z.read(root_name+'/SHA256SUMS_OUTPUT.json'))
        if manifest.get('version')!='v18.49c':raise RuntimeError('Incorrect parent version')
        expected={root_name+'/'+k for k in manifest['files']}|{root_name+'/SHA256SUMS_OUTPUT.json'}
        present={n for n in z.namelist() if not n.endswith('/')}
        if expected!=present:raise RuntimeError('Parent membership mismatch')
        for rel,sha in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts or '__pycache__' in p.parts:raise RuntimeError('Unsafe path')
            raw=z.read(root_name+'/'+rel)
            if hashlib.sha256(raw).hexdigest()!=sha:raise RuntimeError('Parent member SHA mismatch: '+rel)
            dest=dst/p;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_bytes(raw)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(root_name+'/SHA256SUMS_OUTPUT.json'))
    # Execute unchanged C verifier from its own original package; it recursively authenticates B ... J.
    original=dynamic(dst/'scripts/verify_parent.py','v1849c_parent_verifier')
    b,a,z,y,j,parent=original.verify()
    if not parent['nested_original_genealogy_authenticated_to_J']:raise RuntimeError('Missing genealogy')
    verified={'parent_c_sha256':digest,'parent_c_members':len(manifest['files']),
              'nested_original_genealogy_authenticated_to_J':True}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(verified,indent=2)+'\n')
    return dst,b,a,z,y,j,verified

if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
