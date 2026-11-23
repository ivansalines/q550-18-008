#!/usr/bin/env python3
"""Authenticate the unchanged q sendback and its fully nested p/o/j genealogy."""
from __future__ import annotations
import hashlib, json, pathlib, subprocess, sys, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())['files']
    for rel,digest in pin.items():
        if sha((ROOT/rel).read_bytes())!=digest:raise RuntimeError('Pinned original source mismatch: '+rel)
    zpath=ROOT/'inputs/v18_48q_original_server_sendback.zip'
    out=ROOT/'runtime/verified_parent'
    prefix='q550_kappa_counterflow_crossings_v18_48q_bundle/'
    with zipfile.ZipFile(zpath) as z:
        if z.testzip() is not None:raise RuntimeError('Damaged parent ZIP')
        mname=prefix+'SHA256SUMS_OUTPUT.json'
        manifest=json.loads(z.read(mname))
        if manifest['version']!='v18.48q':raise RuntimeError('Wrong version')
        exp={prefix+k for k in manifest['files']}|{mname}
        actual=set(n for n in z.namelist() if not n.endswith('/'))
        if exp!=actual:raise RuntimeError('Parent member mismatch')
        for rel,expected in manifest['files'].items():
            pure=pathlib.PurePosixPath(rel)
            if '..' in pure.parts or pure.is_absolute():raise RuntimeError('Unsafe path')
            content=z.read(prefix+rel)
            if sha(content)!=expected:raise RuntimeError('Parent SHA mismatch '+rel)
            dest=out/prefix/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
        dest=out/mname;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(mname))
    p=out/prefix
    subprocess.run([sys.executable,str(p/'scripts/verify_parent.py')],cwd=p,check=True,
                   stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    for local,par in [('reference/physical_math.py','reference/physical_math.py'),
                      ('reference/crossing_math_q.py','scripts/crossing_math.py')]:
        if (ROOT/local).read_bytes()!=(p/par).read_bytes():raise RuntimeError('Source code drift '+local)
    imported=p/'runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle/runtime/verified_sources/j/q550_kappa_gauge_covariant_v18_48j_bundle/runtime/physical_paths.npz'
    if not imported.exists():raise RuntimeError('Missing original physical 11D paths')
    prov={'version':'v18.48r','parent_sha256':sha(zpath.read_bytes()),
          'parent_q_verified_members':len(manifest['files']),
          'original_paths_sha256':sha(imported.read_bytes()),
          'historical_q_pairs_sha256':sha((p/'results/near_crossing_pairs.csv').read_bytes())}
    (ROOT/'runtime/provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    return p,prov
if __name__=='__main__':print(json.dumps(verify()[1],indent=2))
