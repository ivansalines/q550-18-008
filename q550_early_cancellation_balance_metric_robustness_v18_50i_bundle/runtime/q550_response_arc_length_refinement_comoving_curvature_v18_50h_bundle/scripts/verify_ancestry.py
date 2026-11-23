"""Authenticate v18.50g -> f -> e, stage original e solver without changing it."""
from pathlib import Path
import zipfile,hashlib,json,io
ROOT=Path(__file__).resolve().parents[1]
G='q550_response_arc_length_comoving_composition_v18_50g_bundle'
F='q550_vector_cancellation_geometry_response_composition_continuation_v18_50f_bundle'
E='q550_common_horizon_sensitivity_accumulated_conditioning_v18_50e_bundle'
GZIP='q550_response_arc_length_comoving_composition_v18_50g_server_sendback.zip'

def check(z,root,version,manifest_name):
    if z.testzip() is not None:raise RuntimeError('CRC mismatch: '+root)
    m=json.loads(z.read(f'{root}/{manifest_name}'))
    if m['root']!=root or m['version']!=version:raise RuntimeError('Unexpected manifest')
    expected={root+'/'+rel for rel in m['files']}|{f'{root}/{manifest_name}'}
    if set(z.namelist())!=expected:raise RuntimeError('Unexpected archive members: '+root)
    for rel,digest in m['files'].items():
        path=Path(rel)
        if path.is_absolute() or '..' in path.parts:raise RuntimeError('Unsafe input member')
        if hashlib.sha256(z.read(root+'/'+rel)).hexdigest()!=digest:
            raise RuntimeError('SHA256 mismatch: '+rel)
    return m

def stage():
    source=ROOT/'inputs'/GZIP
    sourcehash=hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(source) as z:
        mg=check(z,G,'v18.50g','SHA256SUMS.json')
        fname=next(n for n in z.namelist() if n.startswith(G+'/inputs/') and n.endswith('.zip'))
        fbytes=z.read(fname)
        greport=json.loads(z.read(G+'/results/report.json'))
    with zipfile.ZipFile(io.BytesIO(fbytes)) as z:
        mf=check(z,F,'v18.50f','SHA256SUMS.json')
        ename=next(n for n in z.namelist() if n.startswith(F+'/inputs/') and n.endswith('.zip'))
        ebytes=z.read(ename)
    with zipfile.ZipFile(io.BytesIO(ebytes)) as z:
        me=check(z,E,'v18.50e','SHA256SUMS_OUTPUT.json')
        dest=ROOT/'runtime'/E
        for n in z.namelist():
            rel=Path(n).relative_to(E)
            target=dest/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(z.read(n))
        ereport=json.loads(z.read(E+'/results/report.json'))
        e_csv=z.read(E+'/results/common_horizon_direction_responses.csv').decode()
    return dest,ereport,e_csv,{'g_zip_sha256':sourcehash,'g_members':len(mg['files']),
       'f_sha256':hashlib.sha256(fbytes).hexdigest(),'f_members':len(mf['files']),
       'e_sha256':hashlib.sha256(ebytes).hexdigest(),'e_members':len(me['files']),
       'g_report_source':greport['source'],'e_parent_counts':ereport['counts']}
