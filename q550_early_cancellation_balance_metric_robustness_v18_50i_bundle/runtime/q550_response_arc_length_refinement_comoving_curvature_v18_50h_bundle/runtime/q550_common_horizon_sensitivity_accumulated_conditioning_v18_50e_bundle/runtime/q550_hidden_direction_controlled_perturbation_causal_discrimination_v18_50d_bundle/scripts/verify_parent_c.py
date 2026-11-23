"""Authenticate the byte-pinned v18.50c sendback and its recursive ancestry."""
from pathlib import Path
import hashlib, importlib.util, json, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
NAME='q550_hidden_tangent_conditioning_turning_response_v18_50c_authenticated_server_sendback.zip'
PIN='fee1f596db2d63de8a0278240e65c273dd0a337c00f7e8df688ce24b78d0142f'
PARENT='q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle'
def hash_bytes(b):return hashlib.sha256(b).hexdigest()
def verify():
    zfile=ROOT/'inputs'/NAME
    if hash_bytes(zfile.read_bytes())!=PIN:raise RuntimeError('v18.50c whole ZIP SHA-256 mismatch')
    dest=ROOT/'runtime'/PARENT
    with zipfile.ZipFile(zfile) as z:
        if z.testzip() is not None:raise RuntimeError('v18.50c CRC error')
        pre=PARENT+'/'
        manifest=json.loads(z.read(pre+'SHA256SUMS_OUTPUT.json'))
        if manifest['root']!=PARENT or manifest['version']!='v18.50c':raise RuntimeError('Unexpected parent manifest')
        if set(z.namelist())!={pre+n for n in manifest['files']}|{pre+'SHA256SUMS_OUTPUT.json'}:
            raise RuntimeError('Unexpected parent members')
        for rel,expected in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe path')
            b=z.read(pre+rel)
            if hash_bytes(b)!=expected:raise RuntimeError('v18.50c member mismatch '+rel)
            out=dest/p;out.parent.mkdir(exist_ok=True,parents=True);out.write_bytes(b)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pre+'SHA256SUMS_OUTPUT.json'))
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v1850d_verified_c',dest/'scripts/verify_parent_b.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    b,breport,ancestry=module.verify()
    report=json.loads((dest/'results/report.json').read_text())
    if report['statistics']['cases']!=10 or report['statistics']['pairs']!=34 or report['statistics']['failures']!=0:
        raise RuntimeError('Unexpected v18.50c parent results')
    return dest,report,{'v18_50c_sha256':PIN,'v18_50c_files':len(manifest['files']), 'ancestry_verified':ancestry}
