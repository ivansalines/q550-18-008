#!/usr/bin/env python3
"""Authenticate the exact v18.48x user server sendback and recursive ancestors."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for f,h in pins['files'].items():
        if sha((ROOT/f).read_bytes())!=h:raise RuntimeError('Historical source SHA-256 mismatch: '+f)
    src=ROOT/'inputs/v18_48x_original_server_sendback.zip'
    root='q550_kappa_contact_lobes_v18_48x_bundle'
    dest=ROOT/'runtime/verified_parent'/root
    with zipfile.ZipFile(src) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Parent ZIP CRC error: '+bad)
        m=json.loads(z.read(root+'/SHA256SUMS_OUTPUT.json'))
        if m['version']!='v18.48x':raise RuntimeError('Unexpected parent version')
        entries={n for n in z.namelist() if not n.endswith('/')}
        expected={root+'/'+n for n in m['files']}|{root+'/SHA256SUMS_OUTPUT.json'}
        if entries!=expected:raise RuntimeError('Parent file hierarchy changed')
        for name,digest in m['files'].items():
            rel=Path(name)
            if rel.is_absolute() or '..' in rel.parts or any(x in {'runtime','__pycache__'} for x in rel.parts):
                raise RuntimeError('Unsafe historical entry '+name)
            data=z.read(root+'/'+name)
            if sha(data)!=digest:raise RuntimeError('Historical payload differs '+name)
            target=dest/rel;target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(data)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(root+'/SHA256SUMS_OUTPUT.json'))
    # Recursive SHA and source authenticity of x -> w -> v -> u -> t -> s -> r -> q -> p -> o -> j.
    old=load(dest/'scripts/verify_parent.py','historical_x_parent_verifier')
    w,v,u,t,s,r,j,provenance=old.verify()
    for name in ('physical_math.py','transversality_math.py','original_drive_math.py','parent_ramp_math.py'):
        if (dest/'reference'/name).read_bytes()!=(ROOT/'reference'/name).read_bytes():
            raise RuntimeError('Original mathematical source differs '+name)
    if (dest/'scripts/lobe_math.py').read_bytes()!=(ROOT/'reference/parent_lobe_math.py').read_bytes():
        raise RuntimeError('Parent contact definitions changed')
    record={'parent_server_zip_sha256':sha(src.read_bytes()),'parent_verified_files':len(m['files']),
            'source_11D_path_sha256':sha((j/'runtime/physical_paths.npz').read_bytes()),
            'recursive_ancestry_verified':True}
    runtime=ROOT/'runtime';runtime.mkdir(exist_ok=True)
    (runtime/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    return dest,j,record
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
