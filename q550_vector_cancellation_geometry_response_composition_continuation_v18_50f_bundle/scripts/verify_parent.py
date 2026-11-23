"""Pin the authentic v18.50e server sendback and verify its file manifest."""
from pathlib import Path
import hashlib,zipfile,json
ROOT=Path(__file__).resolve().parents[1]
NAME='q550_common_horizon_sensitivity_accumulated_conditioning_v18_50e_authenticated_server_sendback.zip'
SHA='21d9f910c14148746853bd211c873a77ae965ec8cf386baff2ec2b8f0cdb8a2f'

def verify():
    path=ROOT/'inputs'/NAME
    h=hashlib.sha256()
    with path.open('rb') as f:
        for buf in iter(lambda:f.read(1024*1024),b''):h.update(buf)
    if h.hexdigest()!=SHA:raise RuntimeError('Immutable parent ZIP checksum mismatch')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise RuntimeError('Parent ZIP CRC failure')
        names=z.namelist();man=[x for x in names if x.endswith('/SHA256SUMS_OUTPUT.json')]
        if len(man)!=1:raise RuntimeError('Ambiguous parent manifest')
        info=json.loads(z.read(man[0]));prefix=info['root']+'/'
        for name,digest in info['files'].items():
            if hashlib.sha256(z.read(prefix+name)).hexdigest()!=digest:
                raise RuntimeError('Parent manifest mismatch: '+name)
        csvbytes=z.read(prefix+'results/common_horizon_direction_responses.csv')
        report=json.loads(z.read(prefix+'results/report.json'))
        return csvbytes,report,dict(zip_sha256=SHA,verified_entries=len(info['files']),version=info['version'])
