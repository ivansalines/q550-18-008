"""Strict verification of authentic v18.49p server sendback and nested ancestry."""
import hashlib,json,zipfile,importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify():
    p=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs'/p['parent_file']
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if digest!=p['parent_sha256']:raise RuntimeError('v18.49p ZIP SHA256 mismatch')
    top=p['parent_root']
    dest=ROOT/'runtime/parent_p'/top
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:raise RuntimeError('Parent CRC failure')
        manifest=json.loads(z.read(top+'/SHA256SUMS_OUTPUT.json'))
        if (manifest['root'],manifest['version'],len(manifest['files']))!=(top,'v18.49p',p['parent_manifest_count']):
            raise RuntimeError('v18.49p manifest failed')
        expected={top+'/'+f for f in manifest['files']}|{top+'/SHA256SUMS_OUTPUT.json'}
        if {i.filename for i in z.infolist() if not i.is_dir()}!=expected:
            raise RuntimeError('Parent member mismatch')
        for f,sha in manifest['files'].items():
            rel=Path(f)
            if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Unsafe member')
            b=z.read(top+'/'+f)
            if hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError('Parent SHA mismatch '+f)
            target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(top+'/SHA256SUMS_OUTPUT.json'))
    preport=json.loads((dest/p['parent_report_name']).read_text())
    if preport['audit'].find('v18.49p')<0 or len(preport['cases'])!=10 or len(preport['phase_crossing_events'])!=4 or preport['failed_cases']:
        raise RuntimeError('Unexpected parent scientific status')
    parent_scripts=dest/'scripts'
    sys.path.insert(0,str(parent_scripts))
    spec=importlib.util.spec_from_file_location('q_49p_verify_parent',str(parent_scripts/'verify_parent.py'))
    v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
    nested=v.verify()[-1]
    if not nested['n_m_l_k_j_genealogy_authenticated']:raise RuntimeError('Nested chain incomplete')
    return dest,preport,{'parent_zip_sha256':digest,'parent_manifest_entries':len(manifest['files']),
        'original_v18_49p_cases':len(preport['cases']),'original_v18_49p_roots':len(preport['phase_crossing_events']),
        'upstream_genealogy_authenticated':True}
