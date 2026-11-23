"""Write per-execution byte checksums separately from immutable source checksums."""
import json,hashlib,pathlib,sys
r=pathlib.Path(__file__).resolve().parents[1]
files={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((r/'results').glob('*')) if p.is_file()}
(r/'SHA256SUMS_OUTPUT.json').write_text(json.dumps({'version':'v18.50m','mode':'execution outputs','file_sha256':files},indent=2)+'\n')
print('OUTPUT MANIFEST WRITTEN',len(files))
