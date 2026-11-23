"""Authenticates v18.49q sendback and its v18.49p→v18.48 genealogy."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text()); source=ROOT/'inputs'/pins['parent_file']
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    if sha!=pins['parent_sha256']:raise RuntimeError('The original v18.49q archive was modified')
    base=pins['parent_root'];dst=ROOT/'runtime/parent_q'/base
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:raise RuntimeError('Parent CRC mismatch')
        manifest=json.loads(z.read(base+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49q' or manifest['root']!=base or len(manifest['files'])!=pins['parent_manifest_count']:
            raise RuntimeError('Wrong v18.49q manifest')
        expected={base+'/'+p for p in manifest['files']}|{base+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected:raise RuntimeError('Unexpected parent tree')
        for rel,expected_sha in manifest['files'].items():
            path=Path(rel)
            if path.is_absolute() or '..' in path.parts:raise RuntimeError('Unsafe archive pathname')
            content=z.read(base+'/'+rel)
            if hashlib.sha256(content).hexdigest()!=expected_sha:raise RuntimeError('Parent member mismatch: '+rel)
            fp=dst/path;fp.parent.mkdir(parents=True,exist_ok=True);fp.write_bytes(content)
        (dst/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(base+'/SHA256SUMS_OUTPUT.json'))
    report=json.loads((dst/pins['parent_report_name']).read_text())
    if 'v18.49q' not in report['audit'] or len(report['cases'])!=5 or len(report['handover_events'])!=4:
        raise RuntimeError('Unexpected source audit status')
    sys.path.insert(0,str(dst/'scripts'))
    spec=importlib.util.spec_from_file_location('r_verified_q_parent',str(dst/'scripts/verify_q_parent.py'))
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    pdir,preport,auth=module.verify()
    if not auth['upstream_genealogy_authenticated']:raise RuntimeError('Upstream ancestry failed')
    return dst,report, {'parent_sha256':sha,'parent_manifest_entries':len(manifest['files']),
        'v18_49q_cases':len(report['cases']),'v18_49q_handover_events':len(report['handover_events']),
        'upstream_verified':True}
