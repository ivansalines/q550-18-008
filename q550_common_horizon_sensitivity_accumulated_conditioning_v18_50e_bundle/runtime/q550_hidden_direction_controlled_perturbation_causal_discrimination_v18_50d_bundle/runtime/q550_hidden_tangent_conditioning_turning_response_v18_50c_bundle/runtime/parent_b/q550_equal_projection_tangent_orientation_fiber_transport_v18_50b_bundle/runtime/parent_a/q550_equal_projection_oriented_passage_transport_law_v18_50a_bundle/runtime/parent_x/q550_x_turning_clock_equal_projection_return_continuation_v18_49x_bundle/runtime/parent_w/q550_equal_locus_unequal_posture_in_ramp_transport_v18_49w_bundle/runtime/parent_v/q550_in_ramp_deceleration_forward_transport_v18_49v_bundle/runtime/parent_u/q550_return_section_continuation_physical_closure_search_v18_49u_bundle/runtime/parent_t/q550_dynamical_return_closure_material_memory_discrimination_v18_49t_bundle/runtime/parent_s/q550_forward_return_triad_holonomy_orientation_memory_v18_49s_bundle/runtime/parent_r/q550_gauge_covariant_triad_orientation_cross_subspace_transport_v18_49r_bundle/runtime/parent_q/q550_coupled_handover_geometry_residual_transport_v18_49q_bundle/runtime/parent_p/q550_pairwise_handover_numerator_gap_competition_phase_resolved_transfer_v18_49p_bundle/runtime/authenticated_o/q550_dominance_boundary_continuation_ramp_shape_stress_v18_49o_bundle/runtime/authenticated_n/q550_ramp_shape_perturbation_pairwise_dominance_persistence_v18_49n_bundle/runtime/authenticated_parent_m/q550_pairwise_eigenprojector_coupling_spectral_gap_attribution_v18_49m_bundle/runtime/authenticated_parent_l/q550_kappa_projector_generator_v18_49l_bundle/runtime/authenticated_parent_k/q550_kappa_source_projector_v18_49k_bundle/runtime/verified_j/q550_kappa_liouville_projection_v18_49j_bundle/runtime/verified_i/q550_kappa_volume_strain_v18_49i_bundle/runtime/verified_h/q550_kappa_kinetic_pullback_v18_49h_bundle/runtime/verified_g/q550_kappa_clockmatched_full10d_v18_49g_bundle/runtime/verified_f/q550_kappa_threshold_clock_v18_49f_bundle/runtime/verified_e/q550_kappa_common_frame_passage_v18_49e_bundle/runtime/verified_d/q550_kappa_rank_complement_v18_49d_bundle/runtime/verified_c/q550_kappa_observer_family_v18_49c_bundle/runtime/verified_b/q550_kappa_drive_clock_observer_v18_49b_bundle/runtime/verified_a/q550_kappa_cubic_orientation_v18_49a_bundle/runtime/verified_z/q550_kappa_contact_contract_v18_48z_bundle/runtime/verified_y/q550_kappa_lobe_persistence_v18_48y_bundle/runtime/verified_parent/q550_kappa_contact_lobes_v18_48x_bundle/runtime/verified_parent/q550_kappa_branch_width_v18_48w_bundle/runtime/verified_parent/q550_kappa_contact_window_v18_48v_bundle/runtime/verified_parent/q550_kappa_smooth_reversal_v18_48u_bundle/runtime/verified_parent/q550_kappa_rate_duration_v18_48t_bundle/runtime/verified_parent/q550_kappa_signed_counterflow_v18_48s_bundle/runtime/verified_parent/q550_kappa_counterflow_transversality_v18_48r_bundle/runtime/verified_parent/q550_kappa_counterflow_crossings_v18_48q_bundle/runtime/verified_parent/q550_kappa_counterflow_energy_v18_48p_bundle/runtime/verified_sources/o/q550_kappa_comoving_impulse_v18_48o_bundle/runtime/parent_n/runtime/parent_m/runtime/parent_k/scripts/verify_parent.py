#!/usr/bin/env python3
"""Read the exact v18.48j server sendback, verify its manifest and nested i/h genealogy.

No external server file is used, no historical input is modified. Python stdlib.
"""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]

def sha_bytes(x):return hashlib.sha256(x).hexdigest()
def safe_verify(z, version):
    names=z.namelist()
    manifests=[n for n in names if n.endswith('/SHA256SUMS_OUTPUT.json')]
    if len(manifests)!=1:raise ValueError('Expected one parent manifest')
    entry=manifests[0]; root=entry.rsplit('/',1)[0]+'/'
    m=json.loads(z.read(entry))
    if m['version']!=version:raise ValueError('Incorrect version')
    if len(m['files'])!=m['file_count']:raise ValueError('File count drift')
    expected={root+name for name in m['files']}
    actual={n for n in names if not n.endswith('/') and n!=entry}
    if expected!=actual:raise ValueError('Extra or missing archive file(s)')
    for n in names:
        p=pathlib.PurePosixPath(n)
        if n.startswith('/') or '..' in p.parts or not n.startswith(root):raise ValueError('Unsafe ZIP member')
    for member,digest in m['files'].items():
        if sha_bytes(z.read(root+member))!=digest:raise ValueError('Hash mismatch: '+member)
    return root,m

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=(ROOT/'inputs/v18_48j_original_server_sendback.zip').read_bytes()
    if sha_bytes(src)!=pins['parent_zip_sha256']:raise ValueError('v18.48j archive hash drift')
    with zipfile.ZipFile(ROOT/'inputs/v18_48j_original_server_sendback.zip') as z:
        if z.testzip():raise ValueError('Damaged v18.48j archive')
        root,m=safe_verify(z,'v18.48j')
        for name,dig in pins['original_source_sha256'].items():
            rel='reference/'+name if name!='gauge_math.py' else 'scripts/gauge_math.py'
            if sha_bytes(z.read(root+rel))!=dig:raise ValueError('Source does not match parent: '+name)
            if sha_bytes((ROOT/'reference'/name).read_bytes())!=dig:raise ValueError('Source changed: '+name)
        runtime=ROOT/'runtime/parent_j'
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name[len(root):]
            dest=runtime/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(z.read(name))
    # Invoke the exact unmodified v18.48j verifier on its extracted files.
    ref=runtime/'scripts/verify_parent.py';spec=importlib.util.spec_from_file_location('original_j_parent_verifier',ref)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    nested=mod.verify()
    prov={'v18_48j_server_sha256':pins['parent_zip_sha256'],
          'v18_48j_manifest_members':len(m['files']), 'nested':nested,
          'physical_paths_sha256':sha_bytes((runtime/'runtime/physical_paths.npz').read_bytes())}
    (ROOT/'runtime/provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    return prov
if __name__=='__main__':print(json.dumps(verify(),indent=2))
