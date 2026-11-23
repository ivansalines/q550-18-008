"""Produce self-contained sendback ZIP for the server without recursive self-inclusion."""
import zipfile,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
  output=ROOT/'q550_response_arc_length_comoving_composition_v18_50g_server_sendback.zip'
  files=[p for p in ROOT.rglob('*') if p.is_file() and p!=output and p.name!='SHA256SUMS.json' and '__pycache__' not in str(p)]
  entries={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}
  (ROOT/'SHA256SUMS.json').write_text(json.dumps({'root':ROOT.name,'version':'v18.50g','files':entries},indent=2)+'\n')
  with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
    for p in files+[ROOT/'SHA256SUMS.json']:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
  with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    for rel,sha256 in entries.items():assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==sha256
  print('PACKED',output,'manifest entries',len(entries))
if __name__=='__main__':run()
