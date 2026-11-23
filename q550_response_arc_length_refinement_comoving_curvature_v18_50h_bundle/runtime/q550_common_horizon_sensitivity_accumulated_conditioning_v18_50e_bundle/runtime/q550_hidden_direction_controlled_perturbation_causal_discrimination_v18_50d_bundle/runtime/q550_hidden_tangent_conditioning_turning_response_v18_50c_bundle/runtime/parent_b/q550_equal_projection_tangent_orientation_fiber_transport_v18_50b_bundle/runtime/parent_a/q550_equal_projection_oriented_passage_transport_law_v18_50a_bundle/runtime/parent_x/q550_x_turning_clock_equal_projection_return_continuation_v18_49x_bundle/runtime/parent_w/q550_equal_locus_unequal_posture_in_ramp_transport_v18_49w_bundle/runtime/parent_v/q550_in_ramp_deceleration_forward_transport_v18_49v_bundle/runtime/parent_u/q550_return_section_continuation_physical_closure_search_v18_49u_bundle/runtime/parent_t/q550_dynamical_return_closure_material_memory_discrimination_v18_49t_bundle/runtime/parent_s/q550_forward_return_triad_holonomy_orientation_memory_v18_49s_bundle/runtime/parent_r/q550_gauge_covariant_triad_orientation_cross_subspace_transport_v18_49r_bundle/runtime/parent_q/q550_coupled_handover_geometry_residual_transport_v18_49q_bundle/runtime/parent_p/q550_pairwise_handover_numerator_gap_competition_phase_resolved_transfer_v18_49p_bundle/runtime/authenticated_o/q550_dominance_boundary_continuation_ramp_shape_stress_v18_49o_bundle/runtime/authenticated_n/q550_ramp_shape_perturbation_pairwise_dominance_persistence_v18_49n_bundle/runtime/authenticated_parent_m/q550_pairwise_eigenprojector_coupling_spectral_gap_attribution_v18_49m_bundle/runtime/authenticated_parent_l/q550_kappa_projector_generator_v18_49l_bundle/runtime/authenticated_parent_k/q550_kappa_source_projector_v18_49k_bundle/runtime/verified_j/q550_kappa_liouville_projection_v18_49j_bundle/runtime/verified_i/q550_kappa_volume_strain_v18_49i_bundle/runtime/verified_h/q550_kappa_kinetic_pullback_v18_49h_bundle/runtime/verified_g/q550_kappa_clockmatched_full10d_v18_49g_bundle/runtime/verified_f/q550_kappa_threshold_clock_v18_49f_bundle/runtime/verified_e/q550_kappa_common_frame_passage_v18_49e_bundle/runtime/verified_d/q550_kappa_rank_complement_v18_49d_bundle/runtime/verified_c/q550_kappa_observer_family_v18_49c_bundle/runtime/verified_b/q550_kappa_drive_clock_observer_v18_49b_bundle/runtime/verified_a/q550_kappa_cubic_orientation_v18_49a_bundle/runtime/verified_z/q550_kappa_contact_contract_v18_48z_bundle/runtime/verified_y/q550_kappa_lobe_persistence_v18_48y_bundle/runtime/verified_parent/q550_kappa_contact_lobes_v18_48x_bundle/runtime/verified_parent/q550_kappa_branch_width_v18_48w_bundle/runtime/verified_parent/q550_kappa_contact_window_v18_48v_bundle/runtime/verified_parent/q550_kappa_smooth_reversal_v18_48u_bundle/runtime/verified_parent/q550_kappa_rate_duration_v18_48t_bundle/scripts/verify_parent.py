#!/usr/bin/env python3
"""Authenticate unchanged v18.48s server sendback and all nested q/p/o/j ancestry."""
from __future__ import annotations
import hashlib,importlib.util,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())['files']
    for rel,digest in pins.items():
        if sha(ROOT/rel)!=digest:raise RuntimeError('Original source SHA-256 mismatch: '+rel)
    archive=ROOT/'inputs/v18_48s_original_server_sendback.zip'
    prefix='q550_kappa_signed_counterflow_v18_48s_bundle/'
    manifest_name=prefix+'SHA256SUMS_OUTPUT.json'
    extracted=ROOT/'runtime/verified_parent';parent=extracted/prefix
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('Corrupt original server sendback')
        manifest=json.loads(z.read(manifest_name))
        if manifest['version']!='v18.48s':raise RuntimeError('Wrong source generation')
        expected={prefix+k for k in manifest['files']}|{manifest_name}
        actual={n for n in z.namelist() if not n.endswith('/')}
        if expected!=actual:raise RuntimeError('Unexpected/missing parent ZIP members')
        for rel,expected_digest in manifest['files'].items():
            pure=Path(rel)
            if pure.is_absolute() or '..' in pure.parts:raise RuntimeError('Unsafe parent member '+rel)
            data=z.read(prefix+rel)
            if hashlib.sha256(data).hexdigest()!=expected_digest:raise RuntimeError('Bad SHA '+rel)
            path=parent/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        path=parent/'SHA256SUMS_OUTPUT.json';path.write_bytes(z.read(manifest_name))
    # The parent verifier recursively authenticates r/q/p/o/j inputs and full 11D history.
    spec=importlib.util.spec_from_file_location('v1848s_parent_verifier',parent/'scripts/verify_parent.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    r,j,parent_provenance=mod.verify()
    for mine,ref in [('reference/physical_math.py','reference/physical_math.py'),
                     ('reference/transversality_math.py','reference/transversality_math.py')]:
        if (ROOT/mine).read_bytes()!=(parent/ref).read_bytes():raise RuntimeError('Math copy not byte identical: '+mine)
    provenance={'parent_server_sha256':sha(archive),'parent_manifest_files':len(manifest['files']),
      'parent_report_sha256':sha(parent/'results/report.json'),
      'historic_11D_states_sha256':sha(j/'runtime/physical_paths.npz'),
      'r_q_p_o_j_genealogy_verified':True,'parent_s_verifier':parent_provenance,
      'physical_rhs_original':True}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return parent,r,j,provenance
if __name__=='__main__':print(json.dumps(verify()[3],indent=2))
