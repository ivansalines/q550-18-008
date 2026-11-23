#!/usr/bin/env python3
"""Versioned SHA-256 output, with executable source and byte-pinned parent."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'SHA256SUMS_OUTPUT.json';archive=ROOT/'sendback.zip'
    fs=sorted(f for f in ROOT.rglob('*') if f.is_file() and f not in (manifest,archive)
        and 'runtime' not in f.relative_to(ROOT).parts
        and '__pycache__' not in f.relative_to(ROOT).parts and f.suffix!='.pyc')
    hashes={str(f.relative_to(ROOT)):digest(f) for f in fs}
    manifest.write_text(json.dumps({'version':'v18.48t','files':hashes},indent=2)+'\n')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in [*fs,manifest]:z.write(f,ROOT.name+'/'+str(f.relative_to(ROOT)))
    print('PACKED',archive,'members',len(fs)+1,'SHA256',digest(archive))
if __name__=='__main__':main()
