#!/usr/bin/env python3
"""Reproducible source/input/results manifest and server sendback ZIP."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'SHA256SUMS_OUTPUT.json';archive=ROOT/'sendback.zip'
    fs=sorted(f for f in ROOT.rglob('*') if f.is_file() and f not in (manifest,archive)
       and not any(p in ('runtime','__pycache__','.pytest_cache') for p in f.relative_to(ROOT).parts)
       and f.suffix!='.pyc' and not f.name.endswith('.log'))
    manifest.write_text(json.dumps({'version':'v18.48u','files':{str(f.relative_to(ROOT)):sha(f) for f in fs}},indent=2)+'\n')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in [*fs,manifest]:z.write(f,ROOT.name+'/'+str(f.relative_to(ROOT)))
    print('PACKED',archive,'files',len(fs)+1,'SHA',sha(archive))
if __name__=='__main__':main()
