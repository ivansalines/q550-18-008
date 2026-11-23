"""Authenticate x sendback and its full executable genealogical ancestry."""
from pathlib import Path
import hashlib,zipfile,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs'/pin['parent_file']
    if hashlib.sha256(src.read_bytes()).hexdigest()!=pin['parent_sha256']:
        raise RuntimeError('v18.49x parent SHA-256 mismatch')
    dest=ROOT/'runtime/parent_x'/pin['parent_root']
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:raise RuntimeError('Parent x ZIP CRC failed')
        manifest=json.loads(z.read(pin['parent_root']+'/SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.49x' or manifest['root']!=pin['parent_root'] or len(manifest['files'])!=pin['parent_manifest_entries']:
            raise RuntimeError('Unexpected x manifest')
        expected={pin['parent_root']+'/'+n for n in manifest['files']}|{pin['parent_root']+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected:raise RuntimeError('Unexpected x ZIP member list')
        for rel,digest in manifest['files'].items():
            rp=Path(rel)
            if rp.is_absolute() or '..' in rp.parts:raise RuntimeError('Unsafe path')
            data=z.read(pin['parent_root']+'/'+rel)
            if hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('x member mismatch '+rel)
            target=dest/rp;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pin['parent_root']+'/SHA256SUMS_OUTPUT.json'))
    report=json.loads((dest/'results/report.json').read_text())
    if report['classification']!=pin['parent_classification'] or report['counts']['matching_projections']!=34:
        raise RuntimeError('Unexpected authenticated x counts/classification')
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('verified_parent_x_genealogy',dest/'scripts/verify_parent_w.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    _,_,chain=mod.verify()
    if not chain['w_and_all_upstream_authenticated']:raise RuntimeError('x upstream ancestry incomplete')
    return dest,report,{'parent_x_sha256':pin['parent_sha256'],'parent_x_manifest_members':len(manifest['files']),'upstream_authenticated':True}
