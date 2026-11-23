#!/usr/bin/env python3
"""Authenticate original v18.49l server sendback and its recursive source ancestry."""
import sys,json,hashlib,zipfile,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    archive=ROOT/'inputs/v18_49l_original_server_sendback.zip'
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest!=pins['l_sendback_sha256']:raise RuntimeError('Original L ZIP digest mismatch')
    prefix=pins['l_root'];dst=ROOT/'runtime/authenticated_parent_l'/prefix
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('Original L ZIP CRC failed')
        manifest=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49l' or manifest['root']!=prefix:raise RuntimeError('Unexpected L manifest version/root')
        required={prefix+'/'+p for p in manifest['files']}|{prefix+'/SHA256SUMS_OUTPUT.json'}
        if required!={p for p in z.namelist() if not p.endswith('/')}:raise RuntimeError('Non-manifest L members or missing files')
        for path,digest_expected in manifest['files'].items():
            pp=Path(path)
            if pp.is_absolute() or '..' in pp.parts:raise RuntimeError('Unsafe archive member')
            data=z.read(prefix+'/'+path)
            if hashlib.sha256(data).hexdigest()!=digest_expected:raise RuntimeError('L manifest SHA mismatch '+path)
            out=dst/pp;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    parent_verifier=dynamic(dst/'scripts/verify_parent.py','m_parent_l_verify')
    pk,pj,i,h,g,f,e,d,c,b,a,z,y,j,previous=parent_verifier.verify()
    if not previous['ancestry_to_v18_48j']:raise RuntimeError('Ancestor not authenticated')
    provenance={'parent_version':'v18.49l','parent_sha256':digest,'parent_members':len(required),
        'ancestry_to_v18_48j':True,'historical_parent_record':previous}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return pk,pj,i,h,g,f,e,d,c,b,a,z,y,j,provenance
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
