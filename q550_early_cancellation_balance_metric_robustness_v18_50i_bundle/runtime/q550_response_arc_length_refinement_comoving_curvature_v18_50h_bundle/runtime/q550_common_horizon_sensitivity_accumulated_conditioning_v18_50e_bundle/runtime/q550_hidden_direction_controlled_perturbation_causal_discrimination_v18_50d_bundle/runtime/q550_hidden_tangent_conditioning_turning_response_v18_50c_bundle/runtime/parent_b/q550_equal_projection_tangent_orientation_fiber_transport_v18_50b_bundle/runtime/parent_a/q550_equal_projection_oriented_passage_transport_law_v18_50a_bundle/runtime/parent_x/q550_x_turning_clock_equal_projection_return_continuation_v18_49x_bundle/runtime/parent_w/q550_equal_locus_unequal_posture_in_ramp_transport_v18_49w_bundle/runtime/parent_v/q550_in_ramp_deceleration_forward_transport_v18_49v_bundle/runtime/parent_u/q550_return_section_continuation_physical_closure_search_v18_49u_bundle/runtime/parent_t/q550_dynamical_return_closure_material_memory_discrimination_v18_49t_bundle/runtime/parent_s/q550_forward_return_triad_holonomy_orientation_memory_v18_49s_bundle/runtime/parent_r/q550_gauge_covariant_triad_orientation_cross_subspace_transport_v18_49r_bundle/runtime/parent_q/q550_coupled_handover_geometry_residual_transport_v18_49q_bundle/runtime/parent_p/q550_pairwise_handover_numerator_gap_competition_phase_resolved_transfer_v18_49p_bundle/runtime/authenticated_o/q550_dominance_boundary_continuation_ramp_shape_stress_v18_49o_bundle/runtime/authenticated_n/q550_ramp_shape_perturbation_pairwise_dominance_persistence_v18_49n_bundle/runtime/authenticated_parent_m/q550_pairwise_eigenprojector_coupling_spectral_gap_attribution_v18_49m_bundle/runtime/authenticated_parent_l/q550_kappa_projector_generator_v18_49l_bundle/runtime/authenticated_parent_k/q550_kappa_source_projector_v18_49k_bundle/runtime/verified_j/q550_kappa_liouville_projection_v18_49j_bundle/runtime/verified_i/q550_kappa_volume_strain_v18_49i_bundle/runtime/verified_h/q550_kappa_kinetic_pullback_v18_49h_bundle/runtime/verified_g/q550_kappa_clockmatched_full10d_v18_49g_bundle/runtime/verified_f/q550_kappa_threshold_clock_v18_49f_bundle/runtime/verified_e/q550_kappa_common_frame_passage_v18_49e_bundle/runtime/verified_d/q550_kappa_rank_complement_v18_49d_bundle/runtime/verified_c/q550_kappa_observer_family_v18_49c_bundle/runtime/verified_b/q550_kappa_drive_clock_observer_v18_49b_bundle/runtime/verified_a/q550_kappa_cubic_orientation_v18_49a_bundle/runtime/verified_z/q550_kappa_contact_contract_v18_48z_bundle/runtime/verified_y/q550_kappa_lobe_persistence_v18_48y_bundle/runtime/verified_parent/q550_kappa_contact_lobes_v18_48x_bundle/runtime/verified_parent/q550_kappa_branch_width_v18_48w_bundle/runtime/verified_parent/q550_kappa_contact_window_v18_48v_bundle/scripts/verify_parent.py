#!/usr/bin/env python3
"""Authenticate exact v18.48u server sendback and its recursively pinned ancestry."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m
def verify():
    pins=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    for rel,h in pins['files'].items():
        if sha(ROOT/rel)!=h:raise RuntimeError('Source pin mismatch: '+rel)
    rootname='q550_kappa_smooth_reversal_v18_48u_bundle'
    parent=ROOT/'runtime/verified_parent'/rootname
    src=ROOT/'inputs/v18_48u_original_server_sendback.zip'
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:raise RuntimeError('Parent CRC failure')
        prefix=rootname+'/'
        manifest_name=prefix+'SHA256SUMS_OUTPUT.json'
        manifest=json.loads(z.read(manifest_name))
        if manifest['version']!='v18.48u':raise RuntimeError('Unexpected parent version')
        expected={prefix+rel for rel in manifest['files']}|{manifest_name}
        if {x for x in z.namelist() if not x.endswith('/')}!=expected:raise RuntimeError('Parent file list mismatch')
        for rel,h in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe archived filename')
            content=z.read(prefix+rel)
            if hashlib.sha256(content).hexdigest()!=h:raise RuntimeError('Parent source mismatch '+rel)
            dest=parent/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
        (parent/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(manifest_name))
    pverify=load(parent/'scripts/verify_parent.py','q550_u_parent_verify')
    t,s,r,j,ancestry=pverify.verify()
    for name in ('physical_math.py','transversality_math.py'):
        if (ROOT/'reference'/name).read_bytes()!=(parent/'reference'/name).read_bytes():
            raise RuntimeError('Physical reference source mismatch: '+name)
    if (ROOT/'reference/original_drive_math.py').read_bytes()!=(parent/'scripts/drive_math.py').read_bytes():
        raise RuntimeError('Original drive history implementation changed')
    meta={'parent_u_server_sha256':sha(src),'parent_u_manifest_files':len(manifest['files']),
          'parent_u_report_sha256':sha(parent/'results/report.json'),
          'physical_paths_sha256':sha(j/'runtime/physical_paths.npz'),
          'recursive_ancestry_sha_verified':True}
    (ROOT/'runtime').mkdir(exist_ok=True)
    (ROOT/'runtime/provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    return parent,t,s,r,j,meta
if __name__=='__main__':print(json.dumps(verify()[-1],indent=2))
