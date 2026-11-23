"""Check only immutable source bytes; generated results never enter this manifest."""
import json,hashlib,pathlib
r=pathlib.Path(__file__).resolve().parents[1]
m=json.loads((r/'SOURCE_MANIFEST.json').read_text())
for filename,expected in m['files'].items():
 p=r/filename
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
  raise RuntimeError('Source drift: '+filename)
print('SOURCE IDENTITY VERIFIED',len(m['files']))
