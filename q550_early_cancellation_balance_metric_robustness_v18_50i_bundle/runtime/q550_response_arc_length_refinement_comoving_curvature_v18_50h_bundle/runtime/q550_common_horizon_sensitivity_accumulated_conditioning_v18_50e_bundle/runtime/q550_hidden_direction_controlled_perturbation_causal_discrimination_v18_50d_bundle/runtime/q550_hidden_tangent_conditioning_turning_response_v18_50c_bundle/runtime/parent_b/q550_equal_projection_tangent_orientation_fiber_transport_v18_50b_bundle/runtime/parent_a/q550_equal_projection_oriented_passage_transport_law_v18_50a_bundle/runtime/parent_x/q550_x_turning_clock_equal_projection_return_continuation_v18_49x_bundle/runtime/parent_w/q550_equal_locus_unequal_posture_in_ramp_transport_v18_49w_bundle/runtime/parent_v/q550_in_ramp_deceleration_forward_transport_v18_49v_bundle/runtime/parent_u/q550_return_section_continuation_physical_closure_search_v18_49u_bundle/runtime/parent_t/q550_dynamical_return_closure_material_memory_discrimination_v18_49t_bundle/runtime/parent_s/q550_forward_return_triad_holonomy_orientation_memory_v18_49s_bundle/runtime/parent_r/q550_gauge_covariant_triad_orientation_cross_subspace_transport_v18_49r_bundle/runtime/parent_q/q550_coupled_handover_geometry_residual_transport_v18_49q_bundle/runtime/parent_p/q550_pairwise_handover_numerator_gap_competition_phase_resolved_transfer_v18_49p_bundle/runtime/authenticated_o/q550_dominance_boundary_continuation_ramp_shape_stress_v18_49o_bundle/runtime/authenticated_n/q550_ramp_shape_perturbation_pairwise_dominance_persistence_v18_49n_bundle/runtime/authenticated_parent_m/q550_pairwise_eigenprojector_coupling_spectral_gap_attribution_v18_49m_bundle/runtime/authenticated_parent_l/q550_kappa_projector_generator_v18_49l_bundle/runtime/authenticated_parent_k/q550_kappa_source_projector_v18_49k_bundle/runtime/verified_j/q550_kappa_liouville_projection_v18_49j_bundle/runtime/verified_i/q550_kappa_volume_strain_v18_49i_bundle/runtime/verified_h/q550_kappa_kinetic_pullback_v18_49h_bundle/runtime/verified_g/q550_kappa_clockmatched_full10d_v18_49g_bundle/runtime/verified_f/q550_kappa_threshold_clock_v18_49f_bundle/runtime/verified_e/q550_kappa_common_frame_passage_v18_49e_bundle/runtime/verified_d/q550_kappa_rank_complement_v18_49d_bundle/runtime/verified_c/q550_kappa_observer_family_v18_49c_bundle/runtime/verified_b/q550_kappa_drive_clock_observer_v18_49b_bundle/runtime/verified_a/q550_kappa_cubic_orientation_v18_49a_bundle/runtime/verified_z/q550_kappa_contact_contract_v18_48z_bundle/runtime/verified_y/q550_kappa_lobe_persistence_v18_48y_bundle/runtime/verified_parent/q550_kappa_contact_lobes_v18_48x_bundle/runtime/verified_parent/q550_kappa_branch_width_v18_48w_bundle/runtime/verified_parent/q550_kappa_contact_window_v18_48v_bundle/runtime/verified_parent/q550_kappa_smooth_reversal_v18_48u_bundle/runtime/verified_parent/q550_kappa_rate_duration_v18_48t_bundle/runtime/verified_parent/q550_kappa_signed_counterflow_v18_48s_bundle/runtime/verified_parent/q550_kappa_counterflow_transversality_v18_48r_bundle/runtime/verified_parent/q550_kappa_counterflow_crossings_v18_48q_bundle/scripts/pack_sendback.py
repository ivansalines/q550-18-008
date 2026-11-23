#!/usr/bin/env python3
"""Build a SHA-verified portable original 18.48q server sendback."""
from __future__ import annotations
import hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    folders=('inputs','reference','scripts','tests','results')
    includes=[ROOT/'README.md',ROOT/'SCIENTIFIC_DECISION_RULES.md',ROOT/'run_on_server.sh',ROOT/'requirements.txt']
    for folder in folders:
        includes.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    includes=sorted(set(includes))
    manifest={'version':'v18.48q','files':{str(p.relative_to(ROOT)):digest(p) for p in includes}}
    manifestpath=ROOT/'SHA256SUMS_OUTPUT.json';manifestpath.write_text(json.dumps(manifest,indent=2)+'\n')
    dst=ROOT/'sendback.zip'
    with zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for p in includes+[manifestpath]:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
    print(f'Packed {dst}, {len(includes)} SHA-256-verified members')
if __name__=='__main__':main()
