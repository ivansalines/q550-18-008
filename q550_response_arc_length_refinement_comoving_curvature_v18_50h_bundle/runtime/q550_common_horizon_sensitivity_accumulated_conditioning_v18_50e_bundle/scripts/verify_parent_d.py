"""Verify v18.50d source byte-for-byte and recursively authenticate its ancestry."""
from pathlib import Path
import hashlib,zipfile,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
PARENT='q550_hidden_direction_controlled_perturbation_causal_discrimination_v18_50d_bundle'
NAME='q550_hidden_direction_controlled_perturbation_causal_discrimination_v18_50d_authenticated_server_sendback.zip'
PIN='abbbdc73e4711b555dd6f2af002c452a93d1e9403a06c04dbf382d64dd1a6dfb'
def verify():
    source=ROOT/'inputs'/NAME
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if PIN and digest!=PIN:raise RuntimeError('v18.50d source SHA256 mismatch')
    dest=ROOT/'runtime'/PARENT
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:raise RuntimeError('v18.50d ZIP CRC failure')
        pre=PARENT+'/'
        manifest=json.loads(z.read(pre+'SHA256SUMS_OUTPUT.json'))
        if manifest['root']!=PARENT or manifest['version']!='v18.50d':raise RuntimeError('v18.50d manifest mismatch')
        expected={pre+k for k in manifest['files']}|{pre+'SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected:raise RuntimeError('v18.50d member set mismatch')
        for rel,sha in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe ancestor path')
            b=z.read(pre+rel)
            if hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError('Ancestor member mismatch: '+rel)
            target=dest/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pre+'SHA256SUMS_OUTPUT.json'))
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v1850e_verified_d',dest/'scripts/verify_parent_c.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    _c,creport,ancestors=mod.verify()
    report=json.loads((dest/'results/report.json').read_text())
    if report['counts']['cases']!=10 or report['counts']['controlled_ivps']!=180 or report['counts']['failed_cases']!=0:
        raise RuntimeError('v18.50d parent counts unexpected')
    return dest,report, {'v18_50d_sha256':digest,'v18_50d_members':len(manifest['files']),'v18_50c_ancestry':ancestors}
