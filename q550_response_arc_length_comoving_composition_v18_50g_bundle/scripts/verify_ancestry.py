"""Read original immutable v18.50f sendback and verify parent manifest and nested v18.50e."""
import zipfile,io,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NAME='q550_vector_cancellation_geometry_response_composition_continuation_v18_50f_authenticated_server_sendback.zip'

def check_zip(z, manifest_suffix, required_version):
    if z.testzip() is not None: raise RuntimeError('ZIP CRC failure')
    entries=[n for n in z.namelist() if n.endswith('/'+manifest_suffix)]
    if len(entries)!=1:raise RuntimeError('manifest count mismatch')
    doc=json.loads(z.read(entries[0])); prefix=doc['root']+'/'
    if doc.get('version')!=required_version:raise RuntimeError('wrong ancestor version')
    for rel,digest in doc['files'].items():
        got=hashlib.sha256(z.read(prefix+rel)).hexdigest()
        if got!=digest:raise RuntimeError('hash mismatch: '+rel)
    return doc,prefix

def load_source():
    p=ROOT/'inputs'/NAME
    dg=hashlib.sha256(p.read_bytes()).hexdigest()
    if dg!='d17d1284fe5ab2db018295307a8e0c283490f3a7c40d5fb2fd87149465760b69':raise RuntimeError('Parent full ZIP sha256 mismatch')
    with zipfile.ZipFile(p) as f:
        m,prefix=check_zip(f,'SHA256SUMS.json','v18.50f')
        csv=f.read(prefix+'results/response_vector_gram_ledger.csv')
        parent_name=prefix+'inputs/q550_common_horizon_sensitivity_accumulated_conditioning_v18_50e_authenticated_server_sendback.zip'
        nested=f.read(parent_name)
        with zipfile.ZipFile(io.BytesIO(nested)) as e:
            em,ep=check_zip(e,'SHA256SUMS_OUTPUT.json','v18.50e')
            e_csv=e.read(ep+'results/common_horizon_direction_responses.csv')
        return csv,e_csv,dict(parent_sha256=dg,v18_50f_verified_entries=len(m['files']),v18_50e_verified_entries=len(em['files']),e_sha256=hashlib.sha256(nested).hexdigest())
