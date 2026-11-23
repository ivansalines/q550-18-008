#!/usr/bin/env python3
"""Authenticate user-returned n ZIP, its full SHA256 manifest, and inherited m→48j chain."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    source=ROOT/'inputs/v18_49n_authentic_server_sendback.zip'
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    if sha!=pins['n_parent_server_sha256']:raise RuntimeError('Authentic v18.49n source hash mismatch')
    prefix=pins['n_root']
    out=ROOT/'runtime/authenticated_n'/prefix
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:raise RuntimeError('Upstream ZIP CRC failure')
        manifest=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49n' or manifest['root']!=prefix:raise RuntimeError('Unexpected parent identity')
        if len(manifest['files'])!=pins['n_manifest_file_count']:raise RuntimeError('Parent manifest cardinality mismatch')
        expected={prefix+'/'+f for f in manifest['files']}|{prefix+'/SHA256SUMS_OUTPUT.json'}
        actual={x for x in z.namelist() if not x.endswith('/')}
        if actual!=expected:raise RuntimeError('Parent extra/missing entries')
        for f,hash_expected in manifest['files'].items():
            rel=Path(f)
            if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Parent traversal attempt')
            data=z.read(prefix+'/'+f)
            if hashlib.sha256(data).hexdigest()!=hash_expected:raise RuntimeError('Manifest mismatch '+f)
            target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        (out/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    for name in ('frame_math.py','generator_math.py','kinetic_metric.py','pairwise_math.py'):
        if (ROOT/'scripts'/name).read_bytes()!=(out/'scripts'/name).read_bytes():
            raise RuntimeError('Inherited helper differs: '+name)
    old=dynamic(out/'scripts/verify_parent.py','o_parent_n_verifier')
    mroot,nodes,provenance=old.verify()
    if not provenance.get('upstream_ancestry_to_v18_48j'):
        raise RuntimeError('Verified ancestry does not reach v18.48j')
    report={'source_version':'v18.49n','n_parent_sha256':sha,'n_manifest_files':len(manifest['files']),
            'm_parent_sha256':provenance['parent_sha256'],'upstream_ancestry_to_v18_48j':True}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return out,mroot,nodes,report

if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
