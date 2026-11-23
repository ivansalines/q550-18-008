#!/usr/bin/env python3
"""Authenticate the unmodified v18.49f server sendback and nested E...J lineage."""
from __future__ import annotations
import hashlib,importlib.util,json,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs/v18_49f_original_server_sendback.zip'
    if hashlib.sha256(src.read_bytes()).hexdigest()!=pin['parent_f_sha256']:
        raise RuntimeError('F parent SHA256 differs from source pin')
    r=pin['parent_f_root'];dst=ROOT/'runtime/verified_f'/r
    with zipfile.ZipFile(src) as archive:
        if archive.testzip() is not None:raise RuntimeError('F parent has a corrupt ZIP member')
        manifest=json.loads(archive.read(r+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49f':raise RuntimeError('Incorrect F parent version')
        expected={r+'/'+name for name in manifest['files']}|{r+'/SHA256SUMS_OUTPUT.json'}
        if set(n for n in archive.namelist() if not n.endswith('/'))!=expected:
            raise RuntimeError('Unexpected/missing F archive members')
        for rel,checksum in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe F member path')
            data=archive.read(r+'/'+rel)
            if hashlib.sha256(data).hexdigest()!=checksum:
                raise RuntimeError(f'F original member SHA256 mismatch: {rel}')
            out=dst/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(archive.read(r+'/SHA256SUMS_OUTPUT.json'))
    verify_f=dynamic(dst/'scripts/verify_parent.py','g_parent_f_verifier')
    e,d,c,b,a,z,y,j,provenance=verify_f.verify()
    if not provenance['nested_ancestry_authenticated_to_J']:
        raise RuntimeError('Historical chain not authenticated to J')
    report={'parent_f_sha256':pin['parent_f_sha256'],
            'parent_f_version':'v18.49f','parent_f_entries':len(manifest['files'])+1,
            'history_authenticated_to_J':True}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return dst,e,d,c,b,a,z,y,j,report
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
