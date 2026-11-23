"""Authenticate the byte-preserved v18.49v server sendback and its complete upstream genealogy."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    parent=ROOT/'inputs'/pins['parent_file']
    with parent.open('rb') as fh:digest=hashlib.file_digest(fh,'sha256').hexdigest()
    if digest!=pins['parent_sha256']:raise RuntimeError('Parent v archive SHA256 mismatch')
    name=pins['parent_root'];dest=ROOT/'runtime/parent_v'/name
    with zipfile.ZipFile(parent) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Parent v CRC failed: '+bad)
        man=json.loads(z.read(name+'/SHA256SUMS_OUTPUT.json'))
        if man['version']!='v18.49v' or man['root']!=name or len(man['files'])!=pins['parent_manifest_entries']:
            raise RuntimeError('Unexpected parent manifest/version')
        expected={name+'/'+r for r in man['files']}|{name+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected:raise RuntimeError('Unexpected extra/missing parent members')
        for relative,sha in man['files'].items():
            sub=Path(relative)
            if sub.is_absolute() or '..' in sub.parts:raise RuntimeError('Unsafe source path')
            payload=z.read(name+'/'+relative)
            if hashlib.sha256(payload).hexdigest()!=sha:raise RuntimeError('Parent file hash failure: '+relative)
            target=dest/sub;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(name+'/SHA256SUMS_OUTPUT.json'))
    report=json.loads((dest/'results/report.json').read_text())
    if report['status']!=pins['parent_status']:raise RuntimeError('Unexpected parent status')
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v18_49v_auth_verifier',dest/'scripts/verify_v_parent.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    _,_,chain=module.verify()
    if not chain['upstream_authenticated']:raise RuntimeError('Parent v ancestry failed')
    return dest,report,{'v_sha256':digest,'v_manifest_entries':len(man['files']),
                         'v_status':report['status'],'u_and_upstream_authenticated':True}
