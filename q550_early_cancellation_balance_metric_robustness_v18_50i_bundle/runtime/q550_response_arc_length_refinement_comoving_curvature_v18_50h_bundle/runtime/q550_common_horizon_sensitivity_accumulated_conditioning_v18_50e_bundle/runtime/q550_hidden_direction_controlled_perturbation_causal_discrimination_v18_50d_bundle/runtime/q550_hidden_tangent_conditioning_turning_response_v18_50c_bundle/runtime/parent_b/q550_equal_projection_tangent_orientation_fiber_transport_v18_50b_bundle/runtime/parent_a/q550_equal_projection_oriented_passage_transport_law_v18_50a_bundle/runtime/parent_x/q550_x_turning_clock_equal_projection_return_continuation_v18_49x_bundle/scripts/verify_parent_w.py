"""Verify the authentic v18.49w server sendback, and retain upstream verification."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    source=ROOT/'inputs'/pins['parent_file']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=pins['parent_sha256']:
        raise RuntimeError('Authenticated v18.49w archive digest mismatch')
    name=pins['parent_root']; dest=ROOT/'runtime/parent_w'/name
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:raise RuntimeError('Parent w CRC mismatch')
        manifest=json.loads(z.read(name+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49w' or manifest['root']!=name or len(manifest['files'])!=pins['parent_manifest_entries']:
            raise RuntimeError('Unexpected v18.49w manifest')
        expected={name+'/'+x for x in manifest['files']}|{name+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected: raise RuntimeError('Unexpected archive members')
        for relative,sha in manifest['files'].items():
            path=Path(relative)
            if path.is_absolute() or '..' in path.parts: raise RuntimeError('Unsafe ancestry member')
            data=z.read(name+'/'+relative)
            if hashlib.sha256(data).hexdigest()!=sha:raise RuntimeError('v18.49w member digest mismatch: '+relative)
            target=dest/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(name+'/SHA256SUMS_OUTPUT.json'))
    report=json.loads((dest/'results/report.json').read_text())
    if report['classification']!=pins['parent_classification'] or report['counts']['successes']!=8:
        raise RuntimeError('Unexpected v18.49w report')
    sys.path.insert(0,str(dest/'scripts'))
    module_path=dest/'scripts/verify_w_parent.py'
    spec=importlib.util.spec_from_file_location('authenticated_w_genealogy',module_path)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    _root,_v_report,chain=mod.verify()
    if not chain['u_and_upstream_authenticated']:raise RuntimeError('Upstream ancestry verification failed')
    return dest,report,{'w_sha256':pins['parent_sha256'],'w_manifest_entries':len(manifest['files']),
                        'w_and_all_upstream_authenticated':True}
