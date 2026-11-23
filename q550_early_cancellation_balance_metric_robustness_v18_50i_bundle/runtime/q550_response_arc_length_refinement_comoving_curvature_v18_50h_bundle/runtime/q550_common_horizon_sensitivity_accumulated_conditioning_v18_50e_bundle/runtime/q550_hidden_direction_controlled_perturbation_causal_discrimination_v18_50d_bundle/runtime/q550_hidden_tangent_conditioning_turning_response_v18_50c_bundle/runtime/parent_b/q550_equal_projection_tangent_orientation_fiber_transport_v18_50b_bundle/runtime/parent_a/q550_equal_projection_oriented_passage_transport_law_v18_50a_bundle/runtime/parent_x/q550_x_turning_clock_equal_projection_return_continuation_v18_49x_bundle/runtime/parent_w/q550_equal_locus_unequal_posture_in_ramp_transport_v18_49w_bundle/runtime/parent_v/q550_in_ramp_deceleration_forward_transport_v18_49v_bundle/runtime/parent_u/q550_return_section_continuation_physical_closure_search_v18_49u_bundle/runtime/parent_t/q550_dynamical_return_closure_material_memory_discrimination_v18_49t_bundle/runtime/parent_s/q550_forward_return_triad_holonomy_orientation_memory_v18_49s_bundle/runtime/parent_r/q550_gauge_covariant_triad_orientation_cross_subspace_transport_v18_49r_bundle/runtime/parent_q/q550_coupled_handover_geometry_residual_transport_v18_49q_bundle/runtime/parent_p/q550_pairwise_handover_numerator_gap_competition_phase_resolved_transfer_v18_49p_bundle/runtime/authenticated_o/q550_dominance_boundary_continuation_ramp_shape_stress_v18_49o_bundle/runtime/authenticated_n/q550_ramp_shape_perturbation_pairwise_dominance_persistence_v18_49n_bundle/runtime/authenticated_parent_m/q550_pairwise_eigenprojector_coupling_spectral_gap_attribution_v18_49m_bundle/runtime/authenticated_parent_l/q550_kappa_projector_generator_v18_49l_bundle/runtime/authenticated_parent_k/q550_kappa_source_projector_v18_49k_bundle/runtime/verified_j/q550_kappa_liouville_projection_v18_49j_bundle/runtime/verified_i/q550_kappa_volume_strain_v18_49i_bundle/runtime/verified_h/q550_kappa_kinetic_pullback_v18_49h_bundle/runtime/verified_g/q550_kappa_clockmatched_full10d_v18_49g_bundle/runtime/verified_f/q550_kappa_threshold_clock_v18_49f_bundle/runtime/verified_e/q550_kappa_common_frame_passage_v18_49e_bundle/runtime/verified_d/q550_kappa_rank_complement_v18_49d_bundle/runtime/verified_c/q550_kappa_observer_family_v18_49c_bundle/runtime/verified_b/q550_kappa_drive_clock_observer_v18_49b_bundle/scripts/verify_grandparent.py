#!/usr/bin/env python3
"""Fail-closed SHA provenance for user-server Z, plus exact recursive Z->Y->...->J."""
from pathlib import Path
import zipfile,json,hashlib,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
NAME='q550_kappa_contact_contract_v18_48z_bundle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for rel,digest in pins['files'].items():
        if sha(ROOT/rel)!=digest:raise RuntimeError('Historical source pin failed: '+rel)
    file=ROOT/'inputs/v18_48z_original_server_sendback.zip'
    dest=ROOT/'runtime/verified_z'/NAME
    with zipfile.ZipFile(file) as arc:
        assert arc.testzip() is None,'Historical Z corrupt CRC'
        manifest=json.loads(arc.read(NAME+'/SHA256SUMS_OUTPUT.json'))
        assert manifest['version']=='v18.48z','Unexpected parent version'
        members={x for x in arc.namelist() if not x.endswith('/')}
        expected={NAME+'/'+rel for rel in manifest['files']}|{NAME+'/SHA256SUMS_OUTPUT.json'}
        if members!=expected:raise RuntimeError('Original Z ZIP hierarchy/payload mismatch')
        for rel,digest in manifest['files'].items():
            rp=Path(rel)
            if rp.is_absolute() or '..' in rp.parts or '__pycache__' in rp.parts or 'runtime' in rp.parts:
                raise RuntimeError('Unsafe archive member: '+rel)
            content=arc.read(NAME+'/'+rel)
            if hashlib.sha256(content).hexdigest()!=digest:
                raise RuntimeError('Original Z SHA failed: '+rel)
            target=dest/rp;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(arc.read(NAME+'/SHA256SUMS_OUTPUT.json'))
    for src,dst in [('scripts/normal_form_math.py','reference/parent_normal_form_math.py'),('reference/parent_ramp_math.py','reference/parent_ramp_math.py')]:
        if (dest/src).read_bytes()!=(ROOT/dst).read_bytes():raise RuntimeError('Historical math source mismatch: '+src)
    p=dynamic(dest/'scripts/verify_parent.py','original_z_verifier_49a')
    yroot,xroot,j,prov=p.verify()
    report=json.loads((dest/'results/report.json').read_text())
    assert report['status']=='FULL_AUTHENTIC_11D_NORMAL_FORM_DIAGNOSTIC'
    assert report['fresh_continuous_root_comparisons']==48
    record={'parent_z_sha256':sha(file),'parent_z_manifest_files':len(manifest['files']),
            'nested_histories_verified_to_j':True,'source_model':'original authentic Z/Y source',
            'source_direct_11D_root_pairs':48}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/parent_verification.json').write_text(json.dumps(record,indent=2)+'\n')
    return dest,yroot,j,record
if __name__=='__main__':
    print(json.dumps(verify()[-1],indent=2))
