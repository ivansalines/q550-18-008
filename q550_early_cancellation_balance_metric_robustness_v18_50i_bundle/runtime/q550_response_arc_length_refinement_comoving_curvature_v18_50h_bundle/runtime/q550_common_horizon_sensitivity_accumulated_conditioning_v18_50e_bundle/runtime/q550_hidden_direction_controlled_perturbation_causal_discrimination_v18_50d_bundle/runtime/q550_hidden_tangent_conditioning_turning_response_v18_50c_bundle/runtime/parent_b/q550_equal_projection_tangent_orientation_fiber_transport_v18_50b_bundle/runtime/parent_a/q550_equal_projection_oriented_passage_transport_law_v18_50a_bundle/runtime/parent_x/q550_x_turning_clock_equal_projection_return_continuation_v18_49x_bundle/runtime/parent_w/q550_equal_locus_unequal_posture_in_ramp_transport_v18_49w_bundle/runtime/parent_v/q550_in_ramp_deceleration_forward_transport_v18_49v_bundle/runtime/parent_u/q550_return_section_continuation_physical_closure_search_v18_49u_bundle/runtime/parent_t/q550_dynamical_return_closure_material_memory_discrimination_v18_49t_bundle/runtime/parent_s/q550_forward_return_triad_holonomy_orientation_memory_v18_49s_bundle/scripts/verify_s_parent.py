"""Read and SHA-256-authenticate the genuine v18.49r sendback, including its ancestry."""
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    fn=ROOT/'inputs'/pin['parent_file']
    digest=hashlib.sha256(fn.read_bytes()).hexdigest()
    if digest!=pin['parent_sha256']:raise RuntimeError('v18.49r parent ZIP SHA mismatch')
    base=pin['parent_root']; dest=ROOT/'runtime/parent_r'/base
    with zipfile.ZipFile(fn) as z:
        if z.testzip() is not None:raise RuntimeError('v18.49r ZIP CRC mismatch')
        manifest=json.loads(z.read(base+'/SHA256SUMS_OUTPUT.json'))
        if (manifest['root'],manifest['version'],len(manifest['files']))!=(base,'v18.49r',pin['parent_manifest_entries']):
            raise RuntimeError('Wrong v18.49r manifest')
        expected={base+'/'+p for p in manifest['files']}|{base+'/SHA256SUMS_OUTPUT.json'}
        if set(z.namelist())!=expected:raise RuntimeError('Unexpected parent members')
        for rel,digestfile in manifest['files'].items():
            safe=Path(rel)
            if safe.is_absolute() or '..' in safe.parts:raise RuntimeError('Unsafe archive member')
            blob=z.read(base+'/'+rel)
            if hashlib.sha256(blob).hexdigest()!=digestfile:raise RuntimeError('Parent member digest mismatch '+rel)
            destpath=dest/safe;destpath.parent.mkdir(parents=True,exist_ok=True);destpath.write_bytes(blob)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(base+'/SHA256SUMS_OUTPUT.json'))
    rreport=json.loads((dest/pin['parent_report_name']).read_text())
    if len(rreport.get('cases',[]))!=5 or len(rreport.get('handover_events',[]))!=4:
        raise RuntimeError('Unexpected r report genealogy')
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('s_r_verified_parent',str(dest/'scripts/verify_r_parent.py'))
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    _,qreport,rauth=mod.verify()
    if not rauth.get('upstream_verified'):raise RuntimeError('Deep ancestry failed')
    return dest,rreport,{'r_zip_sha256':digest,'r_manifest_entries':len(manifest['files']),
                         'r_cases':len(rreport['cases']),'r_events':len(rreport['handover_events']),
                         'q_and_earlier_authenticated':True}
