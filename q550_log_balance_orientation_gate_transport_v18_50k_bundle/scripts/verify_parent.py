"""Authenticate v18.50j *server* sendback.

Server PNGs may differ only by Software tEXt chunks from original manifest;
we pin the exact remaining image byte sequence (including compressed IDAT).
This is stricter than claiming similarity of plots; it is not an independent
physical result. Ignore compiler caches and directory entries.
"""
import hashlib,io,json,struct,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'inputs/q550_early_cancellation_derivative_balance_flow_v18_50j_server_sendback.zip'
PINS=ROOT/'inputs/SOURCE_PINS.json'

def sha(data):return hashlib.sha256(data).hexdigest()

def png_without_software(data):
    if data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Not PNG')
    out=[data[:8]];pos=8
    while pos<len(data):
        length=int.from_bytes(data[pos:pos+4],'big')
        if pos+length+12>len(data):raise ValueError('Truncated PNG')
        typ=data[pos+4:pos+8];payload=data[pos+8:pos+8+length]
        chunk=data[pos:pos+length+12]
        if not (typ==b'tEXt' and payload.startswith(b'Software\0')):
            out.append(chunk)
        pos+=length+12
    return b''.join(out)

def load_parent():
    pins=json.loads(PINS.read_text())
    if sha(SRC.read_bytes())!=pins['parent_server_zip_sha256']:
        raise RuntimeError('Parent ZIP changed')
    with zipfile.ZipFile(SRC) as z:
        if z.testzip() is not None:raise RuntimeError('Parent CRC mismatch')
        root=pins['parent_root']+'/'
        man=json.loads(z.read(root+'SHA256SUMS.json'))
        if man['root']!=pins['parent_root'] or man['version']!='v18.50j':
            raise RuntimeError('Wrong parent manifest')
        if len(man['files'])!=17:raise RuntimeError('Unexpected parent manifest length')
        differences=[]
        for name,expected in man['files'].items():
            if name.startswith('/') or '..' in Path(name).parts:raise RuntimeError('Unsafe name')
            data=z.read(root+name)
            if sha(data)!=expected:
                if not name.endswith('.png') or name not in pins['png_without_software_sha256']:
                    raise RuntimeError('Unapproved parent mismatch '+name)
                if sha(png_without_software(data))!=pins['png_without_software_sha256'][name]:
                    raise RuntimeError('Parent PNG non-Software bytes changed '+name)
                differences.append(name)
        if sorted(differences)!=sorted(pins['png_without_software_sha256']):
            raise RuntimeError('Unexpected parent metadata differences '+repr(differences))
        rows=z.read(root+'results/derivative_balance_phase_ledger.csv').decode('utf8')
        events=z.read(root+'results/derivative_balance_events.csv').decode('utf8')
        report=json.loads(z.read(root+'results/report.json'))
    return rows,events,report, len(man['files']),len(differences)
if __name__=='__main__':
    *_,count,diffs=load_parent()
    print('v18.50k parent verified: ',count,'original manifest members; ',diffs,'known Matplotlib metadata differences')
