"""Authenticate v18.49s server sendback before any physical recomputation."""
import hashlib, importlib.util, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    fn=ROOT/'inputs'/pin['parent_file']
    digest=hashlib.sha256(fn.read_bytes()).hexdigest()
    if digest != pin['parent_sha256']:raise RuntimeError('Authenticated v18.49s input SHA256 mismatch')
    dest=ROOT/'runtime/parent_s'/pin['parent_root']
    with zipfile.ZipFile(fn) as z:
        if z.testzip() is not None:raise RuntimeError('v18.49s ZIP CRC failed')
        manifest=json.loads(z.read(pin['parent_root']+'/SHA256SUMS_OUTPUT.json'))
        if (manifest['version'],manifest['root'],len(manifest['files'])) != ('v18.49s',pin['parent_root'],pin['parent_manifest_entries']):
            raise RuntimeError('Unexpected authentic parent manifest')
        allowed={pin['parent_root']+'/'+name for name in manifest['files']}|{pin['parent_root']+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=allowed:raise RuntimeError('Unexpected source ZIP members')
        for name,h in manifest['files'].items():
            rel=Path(name)
            if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Unsafe source member')
            data=z.read(pin['parent_root']+'/'+name)
            if hashlib.sha256(data).hexdigest()!=h:raise RuntimeError('Incorrect source SHA '+name)
            output=dest/rel;output.parent.mkdir(exist_ok=True,parents=True);output.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pin['parent_root']+'/SHA256SUMS_OUTPUT.json'))
    src_report=json.loads((dest/pin['parent_report_name']).read_text())
    if src_report['status'] != 'NUMERICAL_TWO_PATH_DIAGNOSTIC_NOT_MATERIAL_MEMORY_CERTIFICATE':
        raise RuntimeError('Unexpected v18.49s scientific classification')
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v18_49t_parent_s_verifier',str(dest/'scripts/verify_s_parent.py'))
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    _,r_report,chain=mod.verify()
    if not chain['q_and_earlier_authenticated']:raise RuntimeError('Earlier source chain unauthenticated')
    return dest,src_report,{'parent_sha256':digest,'parent_manifest_members':len(manifest['files']),
                            'parent_status':src_report['status'],'upstream_authenticated':True}
