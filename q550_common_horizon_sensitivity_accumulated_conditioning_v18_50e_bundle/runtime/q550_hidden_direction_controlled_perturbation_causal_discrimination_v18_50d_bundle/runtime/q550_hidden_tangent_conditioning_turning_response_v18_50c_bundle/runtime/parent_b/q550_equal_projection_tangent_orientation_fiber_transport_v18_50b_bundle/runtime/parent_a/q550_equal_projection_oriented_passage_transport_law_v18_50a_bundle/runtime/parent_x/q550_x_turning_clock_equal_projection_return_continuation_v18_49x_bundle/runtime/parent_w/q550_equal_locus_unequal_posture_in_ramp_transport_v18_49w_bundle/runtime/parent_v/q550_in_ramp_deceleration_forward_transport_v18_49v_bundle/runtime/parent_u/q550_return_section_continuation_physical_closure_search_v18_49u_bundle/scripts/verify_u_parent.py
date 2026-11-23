"""Authenticate exact v18.49t sendback and its nested ancestral provenance."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    arc=ROOT/'inputs'/pins['parent_file']
    digest=hashlib.sha256(arc.read_bytes()).hexdigest()
    if digest!=pins['parent_sha256']:raise RuntimeError('v18.49t parent archive SHA mismatch')
    dest=ROOT/'runtime/parent_t'/pins['parent_root']
    with zipfile.ZipFile(arc) as z:
        if z.testzip() is not None:raise RuntimeError('Parent ZIP CRC failure')
        m=json.loads(z.read(pins['parent_root']+'/SHA256SUMS_OUTPUT.json'))
        if m['version']!='v18.49t' or m['root']!=pins['parent_root'] or len(m['files'])!=pins['parent_manifest_entries']:
            raise RuntimeError('Parent metadata unexpected')
        allowed={pins['parent_root']+'/'+f for f in m['files']}|{pins['parent_root']+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=allowed:raise RuntimeError('Parent ZIP unexpected members')
        for f,digest_member in m['files'].items():
            path=Path(f)
            if path.is_absolute() or '..' in path.parts:raise RuntimeError('Unsafe member')
            buf=z.read(pins['parent_root']+'/'+f)
            if hashlib.sha256(buf).hexdigest()!=digest_member:raise RuntimeError('Member SHA mismatch: '+f)
            dst=dest/path;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(buf)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pins['parent_root']+'/SHA256SUMS_OUTPUT.json'))
    report=json.loads((dest/'results/report.json').read_text())
    if report['status']!=pins['parent_status']:raise RuntimeError('Parent classification unexpected')
    # Native v18.49t ancestry verification authenticates s, r, q, p ... originals.
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('u_authentic_parent_t',dest/'scripts/verify_t_parent.py')
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    _,_,chain=m.verify()
    if not chain['upstream_authenticated']:raise RuntimeError('Nested genealogy failed')
    return dest,report,{'parent_sha256':pins['parent_sha256'],
        'parent_manifest_entries':len(json.loads((dest/'SHA256SUMS_OUTPUT.json').read_text())['files']),
        'parent_status':report['status'],'parent_and_upstream_authenticated':True}
