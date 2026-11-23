#!/usr/bin/env python3
"""Authenticate original v18.48m and its complete v18.48k/j/i/h ancestry."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    archive=ROOT/'inputs/v18_48m_original_server_sendback.zip'
    if sha(archive)!=pin['v18_48m_original_server_sha256']:
        raise ValueError('Original v18.48m ZIP SHA-256 mismatch')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Corrupt parent ZIP')
        expected_root='q550_kappa_subspace_intersection_v18_48m_bundle/'
        manifest_name=expected_root+'SHA256SUMS_OUTPUT.json'
        manifest=json.loads(z.read(manifest_name))
        if manifest['version']!='v18.48m' or manifest['file_count']!=29:raise ValueError('Unrecognized parent manifest')
        names=set(x for x in z.namelist() if not x.endswith('/'))
        if names!={expected_root+n for n in manifest['files']}|{manifest_name}:raise ValueError('Unexpected or missing parent member')
        for n,hexsha in manifest['files'].items():
            if hashlib.sha256(z.read(expected_root+n)).hexdigest()!=hexsha:raise ValueError('Parent member mismatch '+n)
        dest=ROOT/'runtime/parent_m'
        for n in sorted(names):
            rel=n.removeprefix(expected_root)
            p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
    spec=importlib.util.spec_from_file_location('v18_48m_parent_verifier',dest/'scripts/verify_parent.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    ancestor=mod.verify()
    physical=dest/'runtime/parent_k/runtime/parent_j/runtime/physical_paths.npz'
    if sha(physical)!=pin['physical_paths_sha256']:raise ValueError('Original physical states changed')
    result=dict(v18_48m_server_sha256=sha(archive),parent_manifest_members=29,
                v18_48m_original_report=json.loads((dest/'results/report.json').read_text())['classification'],
                ancestry=ancestor,physical_paths_sha256=sha(physical))
    (ROOT/'runtime/provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
