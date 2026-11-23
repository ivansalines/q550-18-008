#!/usr/bin/env python3
"""Pack every distributed executable input and result, with SHA-256 provenance."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'SHA256SUMS_OUTPUT.json';archive=ROOT/'sendback.zip'
    fs=[f for f in ROOT.rglob('*') if f.is_file() and f not in (archive,manifest)
        and 'runtime' not in f.relative_to(ROOT).parts
        and '__pycache__' not in f.relative_to(ROOT).parts and f.suffix!='.pyc']
    hashes={str(f.relative_to(ROOT)):sha(f) for f in sorted(fs)}
    manifest.write_text(json.dumps({'version':'v18.48s','files':hashes},indent=2)+'\n')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(fs)+[manifest]:z.write(f,ROOT.name+'/'+str(f.relative_to(ROOT)))
    print('PACKED',archive,'manifest_files',len(fs),'SHA256',sha(archive))
if __name__=='__main__':main()
