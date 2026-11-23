#!/usr/bin/env python3
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=json.loads((root/'SOURCE_MANIFEST.json').read_text())
output=json.loads((root/'SHA256SUMS_OUTPUT.json').read_text())
if source['root']!=root.name or output['root']!=root.name:raise RuntimeError('Incorrect manifest root')
for group in (source['files'],output['file_sha256']):
    for rel,expect in group.items():
        if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=expect:raise RuntimeError('Manifest hash mismatch: '+rel)
names=sorted(set(source['files'])|set(output['file_sha256'])|{'SOURCE_MANIFEST.json','SHA256SUMS_OUTPUT.json'})
output_path=root.parent/(root.name+'_server_sendback.zip')
with zipfile.ZipFile(output_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for rel in names:z.write(root/rel,root.name+'/'+rel)
with zipfile.ZipFile(output_path) as z:
    if z.testzip():raise RuntimeError('Created archive has bad CRC')
    if set(z.namelist())!={root.name+'/'+x for x in names}:raise RuntimeError('Bad archive member set')
print('v18.50n SERVER SENDBACK PACKAGED:',output_path,'members',len(names),'bytes',output_path.stat().st_size)
