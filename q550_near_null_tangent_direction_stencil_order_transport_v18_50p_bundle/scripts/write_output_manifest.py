#!/usr/bin/env python3
"""Digest only generated results, distinct from immutable inputs/sources."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'results').glob('*')) if p.is_file()}
(root/'SHA256SUMS_OUTPUT.json').write_text(json.dumps({'root':root.name,'file_sha256':files},indent=2)+'\n')
print('v18.50p OUTPUT MANIFEST WRITTEN',len(files))
