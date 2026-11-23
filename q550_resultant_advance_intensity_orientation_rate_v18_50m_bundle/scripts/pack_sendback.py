"""Package only pinned sources and output files; never include a runtime tree."""
import hashlib,json,pathlib,zipfile
r=pathlib.Path(__file__).resolve().parents[1]
s=json.loads((r/'SOURCE_MANIFEST.json').read_text())['files'];o=json.loads((r/'SHA256SUMS_OUTPUT.json').read_text())['file_sha256']
for rel,expect in list(s.items())+list(o.items()):
 p=r/rel
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expect:raise RuntimeError('File hash mismatch: '+rel)
archive=r.parent/(r.name+'_server_sendback.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for rel in sorted(set(s)|set(o)|{'SOURCE_MANIFEST.json','SHA256SUMS_OUTPUT.json'}):
  z.write(r/rel,arcname=r.name+'/'+rel)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
print('SENDBACK READY',archive,archive.stat().st_size,'bytes; members',len(s)+len(o)+2)
