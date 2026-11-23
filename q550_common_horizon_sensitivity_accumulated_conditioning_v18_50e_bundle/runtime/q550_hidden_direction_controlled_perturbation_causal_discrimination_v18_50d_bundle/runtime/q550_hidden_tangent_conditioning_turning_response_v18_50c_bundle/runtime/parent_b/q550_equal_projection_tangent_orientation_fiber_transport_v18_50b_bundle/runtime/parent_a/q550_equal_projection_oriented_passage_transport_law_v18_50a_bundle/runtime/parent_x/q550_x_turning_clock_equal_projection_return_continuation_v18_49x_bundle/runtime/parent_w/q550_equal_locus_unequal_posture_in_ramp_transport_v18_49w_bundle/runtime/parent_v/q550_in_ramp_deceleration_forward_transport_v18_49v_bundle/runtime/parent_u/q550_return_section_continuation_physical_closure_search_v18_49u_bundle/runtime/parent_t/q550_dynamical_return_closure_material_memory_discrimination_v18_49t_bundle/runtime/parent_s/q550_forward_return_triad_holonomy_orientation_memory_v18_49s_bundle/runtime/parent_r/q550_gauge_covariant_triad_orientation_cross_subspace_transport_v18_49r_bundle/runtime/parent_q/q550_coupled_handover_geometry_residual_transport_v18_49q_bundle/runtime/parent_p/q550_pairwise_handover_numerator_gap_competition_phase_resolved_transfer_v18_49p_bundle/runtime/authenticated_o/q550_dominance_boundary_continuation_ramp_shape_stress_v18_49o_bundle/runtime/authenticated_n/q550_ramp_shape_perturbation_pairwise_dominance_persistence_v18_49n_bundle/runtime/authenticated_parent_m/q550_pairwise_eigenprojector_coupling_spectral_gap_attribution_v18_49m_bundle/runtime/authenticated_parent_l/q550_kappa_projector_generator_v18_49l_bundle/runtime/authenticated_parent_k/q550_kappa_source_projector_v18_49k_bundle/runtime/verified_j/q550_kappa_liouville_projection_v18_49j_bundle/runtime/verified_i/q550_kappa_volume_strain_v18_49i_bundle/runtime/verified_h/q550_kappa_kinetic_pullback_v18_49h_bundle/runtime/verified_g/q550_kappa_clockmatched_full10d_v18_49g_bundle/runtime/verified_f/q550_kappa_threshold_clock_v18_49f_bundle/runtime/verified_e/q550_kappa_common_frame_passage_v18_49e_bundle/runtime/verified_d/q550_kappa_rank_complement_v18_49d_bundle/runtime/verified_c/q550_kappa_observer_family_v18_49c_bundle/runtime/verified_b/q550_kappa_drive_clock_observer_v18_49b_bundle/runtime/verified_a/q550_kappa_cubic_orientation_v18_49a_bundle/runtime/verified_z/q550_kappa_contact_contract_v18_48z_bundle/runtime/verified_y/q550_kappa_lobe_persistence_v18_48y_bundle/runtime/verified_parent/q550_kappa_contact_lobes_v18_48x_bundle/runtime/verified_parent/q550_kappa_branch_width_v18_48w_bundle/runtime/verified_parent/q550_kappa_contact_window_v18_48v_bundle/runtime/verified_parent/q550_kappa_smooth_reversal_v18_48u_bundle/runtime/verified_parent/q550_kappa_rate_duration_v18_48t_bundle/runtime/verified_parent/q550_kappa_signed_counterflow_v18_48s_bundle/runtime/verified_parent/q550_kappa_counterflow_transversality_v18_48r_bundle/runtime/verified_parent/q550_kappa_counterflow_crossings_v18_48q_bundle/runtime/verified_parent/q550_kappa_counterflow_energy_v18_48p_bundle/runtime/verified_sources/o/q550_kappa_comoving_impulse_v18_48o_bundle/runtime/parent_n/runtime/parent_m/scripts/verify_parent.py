#!/usr/bin/env python3
"""Authenticate original v18.48k server sendback and recursively authenticate j/i/h."""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(b):return hashlib.sha256(b).hexdigest()
def verify_manifest(z,version):
    names=z.namelist()
    manifests=[s for s in names if s.endswith('/SHA256SUMS_OUTPUT.json')]
    if len(manifests)!=1:raise RuntimeError('Expected one SHA256SUMS_OUTPUT.json')
    ref=manifests[0]; prefix=ref.rsplit('/',1)[0]+'/'
    meta=json.loads(z.read(ref))
    if meta['version']!=version:raise ValueError('Wrong parent version')
    canonical=set(prefix+x for x in meta['files'])
    contents=set(n for n in names if not n.endswith('/') and n!=ref)
    if contents!=canonical or len(canonical)!=meta['file_count']:raise ValueError('Parent manifest mismatch')
    for name in names:
        po=pathlib.PurePosixPath(name)
        if name.startswith('/') or '..' in po.parts or not name.startswith(prefix):raise ValueError('ZIP traversal or wrong root')
    for rel,sha in meta['files'].items():
        if digest(z.read(prefix+rel))!=sha:raise ValueError('Parent member hash failure '+rel)
    return prefix,meta

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs/v18_48k_original_server_sendback.zip'
    if digest(src.read_bytes())!=pins['parent_zip_sha256']:raise ValueError('Parent ZIP changed')
    for name,sha in pins['reference_source_sha256'].items():
        if digest((ROOT/'reference'/name).read_bytes())!=sha:raise ValueError('Reference changed: '+name)
    with zipfile.ZipFile(src) as z:
        if z.testzip():raise ValueError('Damaged parent archive')
        pre,meta=verify_manifest(z,'v18.48k')
        for name in ('structural_jet.py','generated_base_jet.py','test_support_mobius_monodromy_audit.py'):
            if digest(z.read(pre+'reference/'+name))!=pins['reference_source_sha256'][name]:raise ValueError('Reference mismatch v18.48k')
        if digest(z.read(pre+'scripts/observer_geometry.py'))!=pins['reference_source_sha256']['observer_geometry_v18_48k.py']:
            raise ValueError('Original observer geometry changed')
        runtime=ROOT/'runtime/parent_k'
        for name in z.namelist():
            if name.endswith('/'):continue
            dst=runtime/name[len(pre):]
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(z.read(name))
    # Check nesting using original v18.48k verifier; it in turn verifies v18.48j, i and h.
    file=runtime/'scripts/verify_parent.py'
    spec=importlib.util.spec_from_file_location('original_parent_k_verifier',file)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    inner=mod.verify()
    physical=runtime/'runtime/parent_j/runtime/physical_paths.npz'
    phys_sha=digest(physical.read_bytes())
    prov={'parent_zip_sha256':pins['parent_zip_sha256'],'parent_verified_members':len(meta['files']),
          'nested_v18_48j':inner,'physical_paths_sha256':phys_sha}
    path=ROOT/'runtime/provenance.json';path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(prov,indent=2)+'\n')
    return prov
if __name__=='__main__': print(json.dumps(verify(),indent=2))
