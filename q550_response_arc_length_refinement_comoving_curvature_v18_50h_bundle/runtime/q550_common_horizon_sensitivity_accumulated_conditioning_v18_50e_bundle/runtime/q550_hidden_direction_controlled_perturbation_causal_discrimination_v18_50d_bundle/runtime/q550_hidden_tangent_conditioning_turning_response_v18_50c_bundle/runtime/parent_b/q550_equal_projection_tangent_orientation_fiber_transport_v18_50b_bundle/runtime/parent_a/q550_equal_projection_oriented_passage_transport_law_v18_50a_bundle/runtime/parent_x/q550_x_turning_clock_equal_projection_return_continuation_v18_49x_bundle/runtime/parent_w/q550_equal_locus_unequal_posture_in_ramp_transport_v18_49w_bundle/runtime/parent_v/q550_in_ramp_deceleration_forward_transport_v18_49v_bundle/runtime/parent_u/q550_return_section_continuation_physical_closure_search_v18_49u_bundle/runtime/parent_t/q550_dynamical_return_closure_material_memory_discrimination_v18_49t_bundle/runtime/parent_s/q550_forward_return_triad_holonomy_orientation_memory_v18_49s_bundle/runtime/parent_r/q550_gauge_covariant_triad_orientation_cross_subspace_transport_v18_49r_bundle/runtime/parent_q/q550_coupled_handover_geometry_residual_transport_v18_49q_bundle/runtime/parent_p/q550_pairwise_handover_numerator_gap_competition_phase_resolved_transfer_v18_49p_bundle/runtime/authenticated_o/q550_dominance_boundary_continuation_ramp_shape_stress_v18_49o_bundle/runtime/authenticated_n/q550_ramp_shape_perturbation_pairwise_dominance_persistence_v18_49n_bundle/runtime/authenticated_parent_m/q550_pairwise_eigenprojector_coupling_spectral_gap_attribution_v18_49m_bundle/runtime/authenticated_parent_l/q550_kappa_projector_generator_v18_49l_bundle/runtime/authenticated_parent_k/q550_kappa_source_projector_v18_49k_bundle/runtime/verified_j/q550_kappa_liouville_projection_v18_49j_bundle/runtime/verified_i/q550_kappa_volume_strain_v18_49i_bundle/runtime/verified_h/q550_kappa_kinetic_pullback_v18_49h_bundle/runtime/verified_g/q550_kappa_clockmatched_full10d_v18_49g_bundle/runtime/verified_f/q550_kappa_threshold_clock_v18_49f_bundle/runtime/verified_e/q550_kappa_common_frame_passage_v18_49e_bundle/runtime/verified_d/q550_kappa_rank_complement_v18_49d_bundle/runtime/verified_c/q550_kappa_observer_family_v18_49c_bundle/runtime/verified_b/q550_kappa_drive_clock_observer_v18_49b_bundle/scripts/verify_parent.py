#!/usr/bin/env python3
"""Fail-closed authentication of v18.49a and its complete historical ancestry."""
from pathlib import Path
import hashlib, json, zipfile, importlib.util, sys
ROOT=Path(__file__).resolve().parents[1]
PARENT='q550_kappa_cubic_orientation_v18_49a_bundle'
def sha(data):return hashlib.sha256(data).hexdigest()
def dynamic(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    sys.modules[name]=m;s.loader.exec_module(m);return m
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for rel,h in pins['files'].items():
        if sha((ROOT/rel).read_bytes())!=h:raise RuntimeError('Pinned source changed: '+rel)
    archive=ROOT/'inputs/v18_49a_original_server_sendback.zip'
    dst=ROOT/'runtime/verified_a'/PARENT
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError('Source ZIP CRC failed')
        manifest=json.loads(z.read(PARENT+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49a':raise RuntimeError('Wrong historical version')
        want={PARENT+'/'+p for p in manifest['files']}|{PARENT+'/SHA256SUMS_OUTPUT.json'}
        have={x for x in z.namelist() if not x.endswith('/')}
        if want!=have:raise RuntimeError('Unexpected/missing ancestral ZIP files')
        for rel,expected in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe path')
            data=z.read(PARENT+'/'+rel)
            if sha(data)!=expected:raise RuntimeError('Ancestral content failed: '+rel)
            target=dst/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(PARENT+'/SHA256SUMS_OUTPUT.json'))
    if (dst/'reference/parent_ramp_math.py').read_bytes()!=(ROOT/'reference/parent_ramp_math.py').read_bytes():
        raise RuntimeError('Drive math source disagreement')
    parent=dynamic(dst/'scripts/verify_parent.py','authenticated_A_verifier_49b')
    zroot,yroot,j,older=parent.verify()
    if (zroot/'reference/physical_math.py').read_bytes()!=(ROOT/'reference/physical_math.py').read_bytes():
        raise RuntimeError('Historical mechanical source changed')
    if (zroot/'reference/y_original_run_audit.py').read_bytes()!=(ROOT/'reference/y_original_run_audit.py').read_bytes():
        raise RuntimeError('Historical IVP source changed')
    jets=list(zroot.rglob('structural_jet.py'))
    jets=[x for x in jets if '/verified_sources/j/' in x.as_posix()]
    if len(jets)!=1:raise RuntimeError('Authentic J jet source ambiguous')
    if jets[0].read_bytes()!=(ROOT/'reference/structural_jet.py').read_bytes():raise RuntimeError('Jet source changed')
    record={'parent_A_sha256':sha(archive.read_bytes()),'parent_manifest_files':len(manifest['files']),
            'ancestry_verified_to_J':True,'reference_analytic_jet_sha256':sha(jets[0].read_bytes())}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(record,indent=2)+'\n')
    return dst,zroot,yroot,j,record
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
