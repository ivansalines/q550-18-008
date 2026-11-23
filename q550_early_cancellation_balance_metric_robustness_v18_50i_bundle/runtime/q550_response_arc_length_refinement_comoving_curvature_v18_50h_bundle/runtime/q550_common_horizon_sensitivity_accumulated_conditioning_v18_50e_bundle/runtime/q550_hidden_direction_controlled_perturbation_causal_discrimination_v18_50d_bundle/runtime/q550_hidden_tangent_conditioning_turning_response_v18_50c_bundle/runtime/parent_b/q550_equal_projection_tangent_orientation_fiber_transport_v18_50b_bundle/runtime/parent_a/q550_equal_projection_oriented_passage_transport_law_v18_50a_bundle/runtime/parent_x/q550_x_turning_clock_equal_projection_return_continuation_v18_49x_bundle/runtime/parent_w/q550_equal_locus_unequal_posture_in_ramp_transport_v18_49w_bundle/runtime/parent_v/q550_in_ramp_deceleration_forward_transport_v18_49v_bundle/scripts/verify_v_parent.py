"""Verify unmodified authentic v18.49u server archive, then recursively authenticate its parent."""
import hashlib, importlib.util, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    arc=ROOT/'inputs'/pins['parent_file']
    if hashlib.file_digest(arc.open('rb'),'sha256').hexdigest()!=pins['parent_sha256']:
        raise RuntimeError('Authentic v18.49u archive SHA mismatch')
    root=pins['parent_root'];dest=ROOT/'runtime/parent_u'/root
    with zipfile.ZipFile(arc) as z:
        if z.testzip() is not None: raise RuntimeError('v18.49u ZIP CRC failed')
        manifest=json.loads(z.read(root+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49u' or manifest['root']!=root or len(manifest['files'])!=pins['parent_manifest_entries']:
            raise RuntimeError('Unexpected v18.49u manifest')
        expected={root+'/'+name for name in manifest['files']}|{root+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected:raise RuntimeError('Unexpected v18.49u members')
        for rel,digest in manifest['files'].items():
            target=Path(rel)
            if target.is_absolute() or '..' in target.parts:raise RuntimeError('Unsafe archive path')
            data=z.read(root+'/'+rel)
            if hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('v18.49u file mismatch: '+rel)
            out=dest/target;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(root+'/SHA256SUMS_OUTPUT.json'))
    report=json.loads((dest/'results/report.json').read_text())
    if report.get('status')!=pins['parent_status']:raise RuntimeError('Parent status mismatch')
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v_auth_parent_u',dest/'scripts/verify_u_parent.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    _,_,chain=mod.verify()
    if not chain['parent_and_upstream_authenticated']:raise RuntimeError('Nested provenance failed')
    return dest, report, {'source_sha256':pins['parent_sha256'], 'u_files':len(manifest['files']),
                          'upstream_authenticated':True, 'u_classification':report['status']}
