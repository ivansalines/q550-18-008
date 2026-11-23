#!/usr/bin/env python3
"""Verify the exact, unchanged v18.48r server return and its nested q/p/o/j ancestry."""
from __future__ import annotations
import hashlib,json,pathlib,subprocess,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())['files']
    for rel,h in pins.items():
        if sha(ROOT/rel)!=h:raise RuntimeError('Source pin mismatch: '+rel)
    archive=ROOT/'inputs/v18_48r_original_server_sendback.zip'
    prefix='q550_kappa_counterflow_transversality_v18_48r_bundle/'
    mname=prefix+'SHA256SUMS_OUTPUT.json'
    out=ROOT/'runtime/verified_parent'
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('Damaged r archive')
        manifest=json.loads(z.read(mname))
        if manifest.get('version')!='v18.48r':raise RuntimeError('Wrong parent version')
        expected={prefix+f for f in manifest['files']}|{mname}
        actual={f for f in z.namelist() if not f.endswith('/')}
        if expected!=actual:raise RuntimeError('Parent member set inconsistent')
        for rel,h in manifest['files'].items():
            pure=pathlib.PurePosixPath(rel)
            if pure.is_absolute() or '..' in pure.parts:raise RuntimeError('Unsafe parent filename')
            content=z.read(prefix+rel)
            if hashlib.sha256(content).hexdigest()!=h:raise RuntimeError('Parent checksum mismatch '+rel)
            target=out/prefix/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
        target=out/mname;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(mname))
    parent=out/prefix
    subprocess.run([sys.executable,str(parent/'scripts/verify_parent.py')],cwd=parent,check=True,
                   stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    for mine,ref in [('reference/physical_math.py','reference/physical_math.py'),
                     ('reference/transversality_math.py','scripts/transversality_math.py')]:
        if (ROOT/mine).read_bytes()!=(parent/ref).read_bytes():raise RuntimeError('Math helper changed '+mine)
    j=parent/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle/runtime/verified_sources/j/q550_kappa_gauge_covariant_v18_48j_bundle'
    if not (j/'runtime/physical_paths.npz').exists():raise RuntimeError('Missing historical physical state data')
    provenance={'parent_sha256':sha(archive),'parent_r_verified_files':len(manifest['files']),
                'parent_r_report_sha256':sha(parent/'results/report.json'),
                'historical_paths_sha256':sha(j/'runtime/physical_paths.npz'),
                'original_11D_rhs':True,'parent_chain_verified':True}
    (ROOT/'runtime/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return parent,j,provenance
if __name__=='__main__':print(json.dumps(verify()[2],indent=2))
