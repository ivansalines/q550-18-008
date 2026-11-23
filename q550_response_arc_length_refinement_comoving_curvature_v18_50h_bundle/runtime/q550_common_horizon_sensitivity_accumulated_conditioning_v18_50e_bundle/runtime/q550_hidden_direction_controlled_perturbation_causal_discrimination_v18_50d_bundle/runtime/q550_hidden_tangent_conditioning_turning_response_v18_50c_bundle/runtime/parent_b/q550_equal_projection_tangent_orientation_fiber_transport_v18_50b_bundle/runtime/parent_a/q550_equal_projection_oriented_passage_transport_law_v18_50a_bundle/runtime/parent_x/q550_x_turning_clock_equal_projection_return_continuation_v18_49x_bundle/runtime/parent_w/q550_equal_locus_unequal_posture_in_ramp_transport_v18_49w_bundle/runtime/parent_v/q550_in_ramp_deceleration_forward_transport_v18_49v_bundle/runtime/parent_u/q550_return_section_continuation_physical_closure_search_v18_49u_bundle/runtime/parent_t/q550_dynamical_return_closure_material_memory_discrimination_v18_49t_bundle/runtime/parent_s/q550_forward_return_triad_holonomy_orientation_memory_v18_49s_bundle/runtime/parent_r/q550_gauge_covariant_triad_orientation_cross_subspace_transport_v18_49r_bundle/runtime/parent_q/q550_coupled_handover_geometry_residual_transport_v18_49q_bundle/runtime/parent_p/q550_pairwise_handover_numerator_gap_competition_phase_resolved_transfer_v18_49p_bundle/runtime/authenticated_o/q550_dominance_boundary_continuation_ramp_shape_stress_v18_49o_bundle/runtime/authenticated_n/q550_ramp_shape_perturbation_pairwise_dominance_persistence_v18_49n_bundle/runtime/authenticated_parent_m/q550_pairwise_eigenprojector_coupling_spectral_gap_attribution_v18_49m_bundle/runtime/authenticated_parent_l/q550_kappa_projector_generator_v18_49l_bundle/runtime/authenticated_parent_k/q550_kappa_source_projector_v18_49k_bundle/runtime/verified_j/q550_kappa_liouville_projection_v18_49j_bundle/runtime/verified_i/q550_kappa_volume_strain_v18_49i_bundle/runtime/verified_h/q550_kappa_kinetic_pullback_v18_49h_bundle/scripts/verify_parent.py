#!/usr/bin/env python3
"""Hash-verify the exact v18.49g server sendback and authenticate nested F...J ancestry."""
import hashlib,importlib.util,json,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    source=ROOT/'inputs/v18_49g_original_server_sendback.zip'
    actual=hashlib.sha256(source.read_bytes()).hexdigest()
    if actual!=pin['g_sendback_sha256']:raise RuntimeError('Changed original G server ZIP')
    root=pin['g_root'];dst=ROOT/'runtime/verified_g'/root
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:raise RuntimeError('Corrupt G ZIP')
        manifest=json.loads(z.read(root+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49g':raise RuntimeError('Wrong G version')
        files={root+'/'+p for p in manifest['files']}|{root+'/SHA256SUMS_OUTPUT.json'}
        if set(n for n in z.namelist() if not n.endswith('/'))!=files:
            raise RuntimeError('G archive members inconsistent with manifest')
        for p,sha in manifest['files'].items():
            parts=Path(p).parts
            if p.startswith('/') or '..' in parts:raise RuntimeError('Unsafe G member')
            payload=z.read(root+'/'+p)
            if hashlib.sha256(payload).hexdigest()!=sha:raise RuntimeError(f'G SHA mismatch {p}')
            target=dst/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(root+'/SHA256SUMS_OUTPUT.json'))
    g_verify=dynamic(dst/'scripts/verify_parent.py','h_g_verified_parent')
    f,e,d,c,b,a,z,y,j,provenance=g_verify.verify()
    if not provenance['history_authenticated_to_J']:
        raise RuntimeError('Nested J genealogy is not authenticated')
    result={'g_sha256':actual,'g_members':len(files),'genealogy_to_J':True}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return dst,f,e,d,c,b,a,z,y,j,result
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
