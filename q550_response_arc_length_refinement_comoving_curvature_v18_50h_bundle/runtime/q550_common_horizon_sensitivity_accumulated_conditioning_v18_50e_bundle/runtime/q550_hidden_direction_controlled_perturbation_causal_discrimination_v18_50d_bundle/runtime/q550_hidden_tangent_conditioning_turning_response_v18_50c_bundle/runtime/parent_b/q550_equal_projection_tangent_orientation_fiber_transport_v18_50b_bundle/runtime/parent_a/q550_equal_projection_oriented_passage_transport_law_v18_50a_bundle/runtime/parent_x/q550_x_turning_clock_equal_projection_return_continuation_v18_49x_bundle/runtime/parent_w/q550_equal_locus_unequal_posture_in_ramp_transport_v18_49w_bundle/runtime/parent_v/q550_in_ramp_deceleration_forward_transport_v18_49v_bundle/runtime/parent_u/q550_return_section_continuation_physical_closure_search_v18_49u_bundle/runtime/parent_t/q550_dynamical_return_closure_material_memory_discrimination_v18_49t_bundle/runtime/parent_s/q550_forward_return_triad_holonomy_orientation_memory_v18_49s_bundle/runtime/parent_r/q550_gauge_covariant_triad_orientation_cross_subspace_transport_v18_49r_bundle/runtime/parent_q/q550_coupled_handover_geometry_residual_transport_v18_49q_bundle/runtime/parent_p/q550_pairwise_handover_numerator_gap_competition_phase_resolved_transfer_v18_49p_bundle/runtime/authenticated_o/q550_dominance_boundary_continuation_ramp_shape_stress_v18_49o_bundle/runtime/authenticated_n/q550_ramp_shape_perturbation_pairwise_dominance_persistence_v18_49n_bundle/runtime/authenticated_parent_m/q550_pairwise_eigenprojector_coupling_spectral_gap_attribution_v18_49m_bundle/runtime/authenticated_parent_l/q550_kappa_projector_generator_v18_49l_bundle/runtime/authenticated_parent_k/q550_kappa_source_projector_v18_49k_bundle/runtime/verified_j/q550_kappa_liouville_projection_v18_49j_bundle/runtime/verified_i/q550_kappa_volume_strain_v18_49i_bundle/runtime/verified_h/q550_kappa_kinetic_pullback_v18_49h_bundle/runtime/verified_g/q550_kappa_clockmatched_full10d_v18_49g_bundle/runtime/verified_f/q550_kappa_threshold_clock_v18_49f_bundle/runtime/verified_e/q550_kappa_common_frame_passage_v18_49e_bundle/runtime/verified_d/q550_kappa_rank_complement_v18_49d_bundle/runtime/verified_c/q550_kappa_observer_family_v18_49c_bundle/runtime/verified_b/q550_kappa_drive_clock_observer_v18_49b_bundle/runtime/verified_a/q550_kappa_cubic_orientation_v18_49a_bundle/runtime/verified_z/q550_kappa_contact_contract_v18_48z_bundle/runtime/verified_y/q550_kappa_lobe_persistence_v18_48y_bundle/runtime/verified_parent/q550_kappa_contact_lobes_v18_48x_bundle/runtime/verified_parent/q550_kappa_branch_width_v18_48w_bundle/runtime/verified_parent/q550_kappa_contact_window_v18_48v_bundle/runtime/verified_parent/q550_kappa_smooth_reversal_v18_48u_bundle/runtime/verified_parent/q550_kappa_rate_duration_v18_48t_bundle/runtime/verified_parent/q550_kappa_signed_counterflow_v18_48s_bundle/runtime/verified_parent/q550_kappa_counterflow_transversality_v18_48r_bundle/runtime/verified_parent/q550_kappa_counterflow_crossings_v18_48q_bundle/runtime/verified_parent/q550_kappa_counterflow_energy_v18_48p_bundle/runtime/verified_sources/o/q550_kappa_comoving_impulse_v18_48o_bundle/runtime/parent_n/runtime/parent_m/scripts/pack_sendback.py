#!/usr/bin/env python3
"""Create a reproducible verified output manifest and ZIP, excluding transient runtime."""
from pathlib import Path
import json,hashlib,zipfile,platform,importlib.metadata
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    (ROOT/'ENVIRONMENT.json').write_text(json.dumps({'python':platform.python_version(),'packages':{k:importlib.metadata.version(k) for k in ['numpy','scipy','mpmath','matplotlib']},'version':'v18.48m'},indent=2)+'\n')
    allfiles=sorted(p for p in ROOT.rglob('*') if p.is_file() and 'runtime' not in p.relative_to(ROOT).parts and '__pycache__' not in p.parts and p.name not in ('sendback.zip','SHA256SUMS_OUTPUT.json') and p.suffix!='.pyc')
    manifest={'version':'v18.48m','file_count':len(allfiles),'files':{str(p.relative_to(ROOT)):sha(p) for p in allfiles}}
    (ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(ROOT/'sendback.zip','w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for p in allfiles+[ROOT/'SHA256SUMS_OUTPUT.json']:
            z.write(p,arcname=f'{ROOT.name}/{p.relative_to(ROOT)}')
    with zipfile.ZipFile(ROOT/'sendback.zip') as z:
        assert z.testzip() is None
    print('SENDBACK',ROOT/'sendback.zip','authenticated files',len(allfiles))
if __name__=='__main__':main()
