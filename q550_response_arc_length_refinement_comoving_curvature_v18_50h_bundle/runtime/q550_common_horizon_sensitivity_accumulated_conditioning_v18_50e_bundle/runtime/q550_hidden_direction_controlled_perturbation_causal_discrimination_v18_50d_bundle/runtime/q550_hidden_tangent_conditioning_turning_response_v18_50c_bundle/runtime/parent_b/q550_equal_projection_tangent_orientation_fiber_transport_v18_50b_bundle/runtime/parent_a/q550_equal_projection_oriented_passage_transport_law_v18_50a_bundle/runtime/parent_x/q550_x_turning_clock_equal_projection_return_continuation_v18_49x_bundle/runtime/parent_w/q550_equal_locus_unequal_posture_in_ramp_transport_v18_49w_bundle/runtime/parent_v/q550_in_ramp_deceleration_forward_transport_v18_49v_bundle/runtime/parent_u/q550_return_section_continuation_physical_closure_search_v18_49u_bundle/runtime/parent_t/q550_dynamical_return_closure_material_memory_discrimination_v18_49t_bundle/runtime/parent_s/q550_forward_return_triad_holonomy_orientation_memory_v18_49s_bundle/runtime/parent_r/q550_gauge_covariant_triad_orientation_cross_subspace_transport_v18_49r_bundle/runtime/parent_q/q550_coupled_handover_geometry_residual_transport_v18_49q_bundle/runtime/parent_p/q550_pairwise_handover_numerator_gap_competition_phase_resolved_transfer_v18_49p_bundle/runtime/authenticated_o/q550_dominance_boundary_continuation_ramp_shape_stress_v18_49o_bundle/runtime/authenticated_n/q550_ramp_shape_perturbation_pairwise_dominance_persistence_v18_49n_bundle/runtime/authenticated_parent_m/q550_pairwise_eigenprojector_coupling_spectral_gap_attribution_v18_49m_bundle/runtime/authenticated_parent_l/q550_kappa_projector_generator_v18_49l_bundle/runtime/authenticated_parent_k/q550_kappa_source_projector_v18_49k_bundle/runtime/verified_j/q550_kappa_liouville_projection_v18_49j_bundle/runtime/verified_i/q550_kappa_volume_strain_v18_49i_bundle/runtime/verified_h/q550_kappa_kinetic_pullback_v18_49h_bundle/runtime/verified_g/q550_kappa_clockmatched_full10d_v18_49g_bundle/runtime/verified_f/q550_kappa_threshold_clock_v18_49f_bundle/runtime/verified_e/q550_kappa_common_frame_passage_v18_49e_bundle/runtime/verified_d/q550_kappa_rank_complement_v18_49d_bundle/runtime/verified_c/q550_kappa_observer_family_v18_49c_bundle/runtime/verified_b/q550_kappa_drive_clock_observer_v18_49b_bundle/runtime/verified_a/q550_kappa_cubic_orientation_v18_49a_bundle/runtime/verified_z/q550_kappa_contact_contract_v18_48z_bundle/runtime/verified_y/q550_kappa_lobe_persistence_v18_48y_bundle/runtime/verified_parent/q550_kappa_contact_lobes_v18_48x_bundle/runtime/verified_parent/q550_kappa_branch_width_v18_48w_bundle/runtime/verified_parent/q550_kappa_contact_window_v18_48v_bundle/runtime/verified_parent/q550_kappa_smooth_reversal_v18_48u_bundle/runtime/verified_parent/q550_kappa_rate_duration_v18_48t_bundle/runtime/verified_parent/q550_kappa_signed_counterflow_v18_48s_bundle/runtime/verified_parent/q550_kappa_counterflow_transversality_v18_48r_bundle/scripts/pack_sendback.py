#!/usr/bin/env python3
"""Pack fully check-summed outputs and complete runnable genealogy."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def checksum(f):return sha256(f.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'SHA256SUMS_OUTPUT.json'
    archive=ROOT/'sendback.zip'
    files=[p for p in ROOT.rglob('*') if p.is_file() and p not in (manifest,archive)
           and 'runtime' not in p.relative_to(ROOT).parts
           and '__pycache__' not in p.relative_to(ROOT).parts and p.suffix!='.pyc']
    payload={str(f.relative_to(ROOT)):checksum(f) for f in sorted(files)}
    manifest.write_text(json.dumps({'version':'v18.48r','files':payload},indent=2)+'\n')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files)+[manifest]:z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
    print('PACKED',archive,'members',len(files),'SHA-256',checksum(archive))
if __name__=='__main__':main()
