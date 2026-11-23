#!/usr/bin/env python3
"""Authenticates unmodified uploaded K server ZIP and executes its recursive genealogy."""
import sys,json,hashlib,zipfile,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path));module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
    info=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    archive=ROOT/'inputs/v18_49k_original_server_sendback.zip'
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest!=info['k_sendback_sha256']:raise RuntimeError('K parent SHA-256 mismatch')
    prefix=info['k_root'];dst=ROOT/'runtime/authenticated_parent_k'/prefix
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('K parent ZIP CRC failed')
        manifest=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49k' or manifest['root']!=prefix:raise RuntimeError('Wrong parent metadata')
        expected={prefix+'/'+p for p in manifest['files']}|{prefix+'/SHA256SUMS_OUTPUT.json'}
        if expected!={p for p in z.namelist() if not p.endswith('/')}:raise RuntimeError('Unlisted or absent parent member')
        for name,checksum in manifest['files'].items():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts:raise RuntimeError('Unsafe parent path')
            content=z.read(prefix+'/'+name)
            if hashlib.sha256(content).hexdigest()!=checksum:raise RuntimeError('K parent file tampered: '+name)
            out=dst/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(content)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    parent_verify=dynamic(dst/'scripts/verify_parent.py','l_parent_k_verify')
    j,i,h,g,f,e,d,c,b,a,z,y,janc,previous=parent_verify.verify()
    if not previous['ancestry_to_v18_48j']:raise RuntimeError('Historical physics ancestry not authenticated')
    proven={'parent_version':'v18.49k','parent_sha256':digest,'parent_members':len(expected),
        'ancestry_to_v18_48j':True,'historical_parent_record':previous}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(proven,indent=2)+'\n')
    return dst,j,i,h,g,f,e,d,c,b,a,z,y,janc,proven
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
