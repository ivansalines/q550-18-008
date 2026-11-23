#!/usr/bin/env python3
"""Authenticate the original v18.48p server ZIP and its v18.48o/j ancestry."""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, subprocess, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(data): return hashlib.sha256(data).hexdigest()

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())['files']
    for rel, expected in pins.items():
        got=sha((ROOT/rel).read_bytes())
        if got!=expected: raise RuntimeError('Pinned source mismatch: '+rel)
    src=ROOT/'inputs/v18_48p_original_server_sendback.zip'
    base=ROOT/'runtime/verified_parent'
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None: raise RuntimeError('Corrupted parent archive')
        mf=[n for n in z.namelist() if n.endswith('/SHA256SUMS_OUTPUT.json')]
        if len(mf)!=1: raise RuntimeError('Missing/ambiguous parent manifest')
        prefix=mf[0].split('/')[0]+'/'
        if prefix!='q550_kappa_counterflow_energy_v18_48p_bundle/' or mf[0]!=prefix+'SHA256SUMS_OUTPUT.json':
            raise RuntimeError('Unexpected parent root')
        manifest=json.loads(z.read(mf[0]));assert manifest['version']=='v18.48p'
        expected={prefix+n for n in manifest['files']}|{mf[0]}
        actual={n for n in z.namelist() if not n.endswith('/')}
        if expected!=actual: raise RuntimeError('Unexpected archive members')
        for relative,digest in manifest['files'].items():
            pure=pathlib.PurePosixPath(relative)
            if pure.is_absolute() or '..' in pure.parts:raise RuntimeError('Unsafe archive path')
            contents=z.read(prefix+relative)
            if sha(contents)!=digest:raise RuntimeError('Parent SHA mismatch '+relative)
        for name in sorted(actual):
            file=base/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(z.read(name))
    p=base/prefix.rstrip('/')
    subprocess.run([sys.executable,str(p/'scripts/verify_parent.py')],cwd=p,check=True,
                   stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    if (ROOT/'reference/physical_math.py').read_bytes()!=(p/'scripts/physical_math.py').read_bytes():
        raise RuntimeError('Inherited energy formula mismatch')
    npz=p/'runtime/verified_sources/j/q550_kappa_gauge_covariant_v18_48j_bundle/runtime/physical_paths.npz'
    if sha(npz.read_bytes())!='3d78ce41378b3ce0fb955a281baae1d4bb6f8d107ab17c718cbbdb2a6696405a':
        raise RuntimeError('11D original historical source mismatch')
    result=p/'results/full_11d_protocol_trajectories.npz'
    import numpy as np
    q=np.load(result,allow_pickle=False)
    if q['state'].shape!=(40,41,11):raise RuntimeError('p historical saved IVP shape mismatch')
    provenance={'version':'v18.48q','parent_sha256':sha(src.read_bytes()),
                'parent_verified_members':len(manifest['files']),
                'physical_paths_sha256':sha(npz.read_bytes()),
                'p_trajectory_sha256':sha(result.read_bytes())}
    (ROOT/'runtime/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return p,provenance
if __name__=='__main__':
    print(json.dumps(verify()[1],indent=2))
