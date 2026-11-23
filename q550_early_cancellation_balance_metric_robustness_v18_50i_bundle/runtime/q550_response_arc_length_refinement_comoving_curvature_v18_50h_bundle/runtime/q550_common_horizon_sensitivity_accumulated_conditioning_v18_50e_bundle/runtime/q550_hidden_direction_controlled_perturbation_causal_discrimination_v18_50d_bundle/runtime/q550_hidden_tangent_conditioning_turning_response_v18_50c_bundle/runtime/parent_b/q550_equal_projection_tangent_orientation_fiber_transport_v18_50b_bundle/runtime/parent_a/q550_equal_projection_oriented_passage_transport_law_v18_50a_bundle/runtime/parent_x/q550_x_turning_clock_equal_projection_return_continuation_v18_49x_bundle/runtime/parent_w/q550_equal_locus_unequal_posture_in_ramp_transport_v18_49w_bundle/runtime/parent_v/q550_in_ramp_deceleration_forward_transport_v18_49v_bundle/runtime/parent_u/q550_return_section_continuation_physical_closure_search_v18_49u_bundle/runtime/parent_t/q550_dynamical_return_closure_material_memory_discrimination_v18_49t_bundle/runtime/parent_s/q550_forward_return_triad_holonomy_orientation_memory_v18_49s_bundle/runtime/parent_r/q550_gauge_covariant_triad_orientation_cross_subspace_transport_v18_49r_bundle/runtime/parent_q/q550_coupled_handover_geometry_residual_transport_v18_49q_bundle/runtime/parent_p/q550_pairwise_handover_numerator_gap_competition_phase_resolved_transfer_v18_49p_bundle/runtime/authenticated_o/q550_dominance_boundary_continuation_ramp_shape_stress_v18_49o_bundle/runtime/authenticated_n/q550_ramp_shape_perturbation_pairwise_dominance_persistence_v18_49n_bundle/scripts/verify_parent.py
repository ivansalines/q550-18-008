#!/usr/bin/env python3
"""Verify immutable v18.49m server ZIP and its recursively authenticated Q550 ancestry."""
from pathlib import Path
import hashlib,json,zipfile,importlib.util,sys
ROOT=Path(__file__).resolve().parents[1]
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    archive=ROOT/'inputs/v18_49m_original_server_sendback.zip'
    digest=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
    if digest!=pins['m_sendback_sha256']:raise RuntimeError('v18.49m parent ZIP hash mismatch')
    prefix=pins['m_root'];dest=ROOT/'runtime/authenticated_parent_m'/prefix
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('Corrupt v18.49m original ZIP')
        hashes=json.loads(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
        if hashes['root']!=prefix or hashes['version']!='v18.49m':raise RuntimeError('Unexpected upstream manifest')
        expected={prefix+'/'+x for x in hashes['files']}|{prefix+'/SHA256SUMS_OUTPUT.json'}
        actual={x for x in z.namelist() if not x.endswith('/')}
        if actual!=expected:raise RuntimeError('Unexpected files in upstream archive')
        for path,sha in hashes['files'].items():
            rel=Path(path)
            if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Unsafe upstream path')
            data=z.read(prefix+'/'+path)
            if hashlib.sha256(data).hexdigest()!=sha:raise RuntimeError('Upstream manifest mismatch '+path)
            out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(prefix+'/SHA256SUMS_OUTPUT.json'))
    # The helper scripts are preserved verbatim; detect accidental edits here.
    for name in ('frame_math.py','generator_math.py','kinetic_metric.py','pairwise_math.py'):
        if (ROOT/'scripts'/name).read_bytes() != (dest/'scripts'/name).read_bytes():
            raise RuntimeError('Inherited module changed unexpectedly: '+name)
    old=dynamic(dest/'scripts/verify_parent.py','n_original_m_parent_verifier')
    *nodes,chain=old.verify()
    if not chain.get('ancestry_to_v18_48j'):raise RuntimeError('v18.48j ancestry not authenticated')
    provenance={'parent_version':'v18.49m','parent_sha256':digest,'upstream_ancestry_to_v18_48j':True,
                'parent_number_of_manifest_files':len(hashes['files']), 'nested_parent_version':chain['parent_version']}
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return dest,nodes,provenance
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
