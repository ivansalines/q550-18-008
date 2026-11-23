#!/usr/bin/env python3
"""Verify the unchanged v18.48t sendback and its recursively pinned s/r/q/p/o/j ancestry."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for name,want in pins['files'].items():
        if sha(ROOT/name)!=want:raise RuntimeError('SOURCE SHA mismatch: '+name)
    zpath=ROOT/'inputs/v18_48t_original_server_sendback.zip'
    prefix='q550_kappa_rate_duration_v18_48t_bundle/'
    manifest_name=prefix+'SHA256SUMS_OUTPUT.json'
    folder=ROOT/'runtime/verified_parent'/prefix
    with zipfile.ZipFile(zpath) as z:
        if z.testzip() is not None:raise RuntimeError('Parent ZIP CRC error')
        m=json.loads(z.read(manifest_name))
        if m['version']!='v18.48t':raise RuntimeError('Wrong parent generation')
        expected={prefix+k for k in m['files']}|{manifest_name}
        actual={k for k in z.namelist() if not k.endswith('/')}
        if expected!=actual:raise RuntimeError('Unexpected or missing parent files')
        for rel,h in m['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe archive path')
            data=z.read(prefix+rel)
            if hashlib.sha256(data).hexdigest()!=h:raise RuntimeError('Parent SHA mismatch: '+rel)
            dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        (folder/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(manifest_name))
    spec=importlib.util.spec_from_file_location('q550_v1848t_parent_verify',folder/'scripts/verify_parent.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    parent_s,r,j,previous=mod.verify()
    for k in ('physical_math.py','transversality_math.py'):
        if (ROOT/'reference'/k).read_bytes()!=(folder/'reference'/k).read_bytes():
            raise RuntimeError('Historical physical math altered: '+k)
    info={'parent_t_server_sha256':sha(zpath),'parent_t_manifest_count':len(m['files']),
        'parent_t_report_sha256':sha(folder/'results/report.json'),
        'original_history_sha256':sha(j/'runtime/physical_paths.npz'),
        'parent_t_source_recursion_passed':True,'parent_s_to_j_verified':previous}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/provenance.json').write_text(json.dumps(info,indent=2)+'\n')
    return folder,parent_s,r,j,info
if __name__=='__main__':print(json.dumps(verify()[4],indent=2))
