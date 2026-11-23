#!/usr/bin/env python3
"""Verify the unchanged H server sendback and its recursively pinned ancestry."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'inputs/v18_49h_original_server_sendback.zip'
PIN=ROOT/'inputs/SOURCE_PINS.json'
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path));obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;spec.loader.exec_module(obj);return obj

def verify():
    info=json.loads(PIN.read_text());s=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if s!=info['h_sendback_sha256']:raise RuntimeError('Immutable H server source SHA differs')
    root=info['h_root'];out=ROOT/'runtime/verified_h'/root
    with zipfile.ZipFile(SOURCE) as z:
        if z.testzip():raise RuntimeError('Bad H archive')
        man=json.loads(z.read(root+'/SHA256SUMS_OUTPUT.json'))
        if man['version']!='v18.49h':raise RuntimeError('Unexpected H version')
        required={root+'/'+p for p in man['files']}|{root+'/SHA256SUMS_OUTPUT.json'}
        if set(m for m in z.namelist() if not m.endswith('/'))!=required:raise RuntimeError('H zip members mismatch')
        for p,sh in man['files'].items():
            if p.startswith('/') or '..' in Path(p).parts:raise RuntimeError('Unsafe source path')
            payload=z.read(root+'/'+p)
            if hashlib.sha256(payload).hexdigest()!=sh:raise RuntimeError('Invalid H original SHA: '+p)
            dest=out/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload)
        (out/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(root+'/SHA256SUMS_OUTPUT.json'))
    prior=dynamic(out/'scripts/verify_parent.py','i_authenticated_h_verifier')
    # H verifies G and nested F,E,D,C,B,A,Z,Y,J sources.
    g,f,e,d,c,b,a,zz,y,j,prov=prior.verify()
    if not prov['genealogy_to_J']:raise RuntimeError('Full genealogy was not authenticated')
    result={'h_sha256':s,'h_members':len(required),'ancestry_to_J':True}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return out,g,f,e,d,c,b,a,zz,y,j,result
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
