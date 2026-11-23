#!/usr/bin/env python3
"""Build immutable-source + per-execution-output sendback, excluding runtime caches."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def check():
    sm=json.loads((R/'SOURCE_MANIFEST.json').read_text())
    for name,digest in sm['files'].items():
        if hashlib.sha256((R/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Source changed since packaging: '+name)
    om=json.loads((R/'SHA256SUMS_OUTPUT.json').read_text())
    for name,digest in om['file_sha256'].items():
        if hashlib.sha256((R/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Execution result changed since manifest: '+name)
    return sm,om

def main():
    sm,om=check()
    target=R.parent/(R.name+'_server_sendback.zip')
    selected=set(sm['files'])|set(om['file_sha256'])|{'SOURCE_MANIFEST.json','SHA256SUMS_OUTPUT.json'}
    with zipfile.ZipFile(target,'w') as z:
        for name in sorted(selected):
            fp=R/name
            z.write(fp,arcname=R.name+'/'+name,compress_type=zipfile.ZIP_STORED if name.endswith('.zip') else zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(target) as z:
        if z.testzip():raise RuntimeError('Sendback ZIP CRC mismatch')
    print('v18.50l packaged',target,'members',len(selected),'MB',round(target.stat().st_size/1e6,2),flush=True)
if __name__=='__main__':main()
