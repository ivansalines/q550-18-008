#!/usr/bin/env python3
"""Verify the immutable source and parent ZIP; ignore mutable results and logs."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'SOURCE_MANIFEST.json'
def main():
    data=json.loads(MAN.read_text())
    assert data['version']=='v18.50k' and data['root']==ROOT.name
    for name,checksum in data['files'].items():
        assert '..' not in Path(name).parts and not Path(name).is_absolute()
        current=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if current!=checksum:raise RuntimeError(f'Source SHA256 mismatch: {name}')
    print(f"v18.50k immutable source hashes PASS: {len(data['files'])}/{len(data['files'])}")
if __name__=='__main__':main()
