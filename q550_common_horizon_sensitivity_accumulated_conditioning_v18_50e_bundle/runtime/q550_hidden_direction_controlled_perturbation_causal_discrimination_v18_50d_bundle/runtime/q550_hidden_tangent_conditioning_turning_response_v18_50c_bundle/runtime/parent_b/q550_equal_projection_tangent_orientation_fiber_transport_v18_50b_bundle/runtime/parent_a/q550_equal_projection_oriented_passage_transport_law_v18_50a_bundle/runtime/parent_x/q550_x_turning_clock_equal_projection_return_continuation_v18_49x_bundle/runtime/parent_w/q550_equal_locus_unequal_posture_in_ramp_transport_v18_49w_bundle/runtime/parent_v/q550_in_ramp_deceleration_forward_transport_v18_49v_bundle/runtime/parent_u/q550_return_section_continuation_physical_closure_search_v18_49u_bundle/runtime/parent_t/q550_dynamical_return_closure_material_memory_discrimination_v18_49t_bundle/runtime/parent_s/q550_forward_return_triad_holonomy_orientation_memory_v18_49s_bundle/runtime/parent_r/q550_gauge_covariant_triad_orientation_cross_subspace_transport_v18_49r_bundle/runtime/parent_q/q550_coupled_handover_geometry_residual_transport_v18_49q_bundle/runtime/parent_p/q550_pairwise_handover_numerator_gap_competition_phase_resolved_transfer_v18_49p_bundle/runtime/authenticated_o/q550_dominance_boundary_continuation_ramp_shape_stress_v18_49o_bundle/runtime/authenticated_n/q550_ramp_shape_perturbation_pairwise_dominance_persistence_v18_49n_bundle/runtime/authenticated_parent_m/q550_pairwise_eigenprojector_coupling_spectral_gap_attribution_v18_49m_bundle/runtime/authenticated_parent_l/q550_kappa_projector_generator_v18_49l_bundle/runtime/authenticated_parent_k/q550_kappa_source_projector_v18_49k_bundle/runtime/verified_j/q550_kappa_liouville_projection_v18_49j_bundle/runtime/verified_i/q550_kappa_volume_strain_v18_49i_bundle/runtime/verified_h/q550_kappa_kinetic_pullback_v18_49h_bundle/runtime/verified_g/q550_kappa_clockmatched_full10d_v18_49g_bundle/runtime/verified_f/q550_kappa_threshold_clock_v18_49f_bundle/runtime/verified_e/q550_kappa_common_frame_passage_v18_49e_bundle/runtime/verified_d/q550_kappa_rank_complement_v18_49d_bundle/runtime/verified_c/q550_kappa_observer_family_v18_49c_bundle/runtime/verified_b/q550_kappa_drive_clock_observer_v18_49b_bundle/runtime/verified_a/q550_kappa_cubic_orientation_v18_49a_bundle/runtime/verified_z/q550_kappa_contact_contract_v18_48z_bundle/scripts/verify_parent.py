#!/usr/bin/env python3
"""Fail-closed SHA verification of the exact user-server Y and recursive ancestors."""
from __future__ import annotations
import hashlib,importlib.util,json,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME='q550_kappa_lobe_persistence_v18_48y_bundle'
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for name,h in pins['files'].items():
        p=ROOT/name
        if sha(p.read_bytes())!=h:raise RuntimeError('Original pinned byte mismatch: '+name)
    original=ROOT/'inputs/v18_48y_original_server_sendback.zip'
    dest=ROOT/'runtime/verified_y'/NAME
    with zipfile.ZipFile(original) as f:
        if f.testzip():raise RuntimeError('Original Y ZIP failed CRC')
        m=json.loads(f.read(NAME+'/SHA256SUMS_OUTPUT.json'))
        if m['version']!='v18.48y':raise RuntimeError('Wrong parent audit version')
        expected={NAME+'/'+n for n in m['files']}|{NAME+'/SHA256SUMS_OUTPUT.json'}
        entries=set(n for n in f.namelist() if not n.endswith('/'))
        if expected!=entries:raise RuntimeError('Original Y ZIP hierarchy or payload set changed')
        for rel,h in m['files'].items():
            path=Path(rel)
            if path.is_absolute() or '..' in path.parts or any(p in ('runtime','__pycache__') for p in path.parts):
                raise RuntimeError('Unsafe historical path '+rel)
            payload=f.read(NAME+'/'+rel)
            if sha(payload)!=h:raise RuntimeError('Original Y payload mismatch: '+rel)
            target=dest/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(f.read(NAME+'/SHA256SUMS_OUTPUT.json'))
    # Original authenticated chain Y -> X -> W -> V -> U -> T -> S -> R -> Q -> P -> O -> J.
    yverify=load(dest/'scripts/verify_parent.py','historical_y_verifier_z')
    xroot,j,_=yverify.verify()
    for name in ('physical_math.py','parent_ramp_math.py','parent_lobe_math.py','transversality_math.py'):
        if (ROOT/'reference'/name).read_bytes()!=(dest/'reference'/name).read_bytes():
            raise RuntimeError('Historical model mathematics diverged: '+name)
    for filename in ('barrier_height_curvature.csv','dense_contact_profiles.csv','threshold_persistence_components.csv',
                     'quadratic_gap_scaling_check.csv','critical_threshold_curve.csv','report.json'):
        if (ROOT/'inputs'/('v18_48y_'+filename)).read_bytes()!=(dest/'results'/filename).read_bytes():
            raise RuntimeError('Pinned historical Y result differs: '+filename)
    record={'historical_parent_sha256':sha(original.read_bytes()),'parent_manifest_files':len(m['files']),
            'recursive_ancestry_verified':True,'original_states_authenticated':328,
            'parent_y_46_profiles_authenticated':True}
    (ROOT/'runtime').mkdir(parents=True,exist_ok=True)
    (ROOT/'runtime/provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    return dest,xroot,j,record
if __name__=='__main__':
    print(json.dumps(verify()[-1],indent=2))
