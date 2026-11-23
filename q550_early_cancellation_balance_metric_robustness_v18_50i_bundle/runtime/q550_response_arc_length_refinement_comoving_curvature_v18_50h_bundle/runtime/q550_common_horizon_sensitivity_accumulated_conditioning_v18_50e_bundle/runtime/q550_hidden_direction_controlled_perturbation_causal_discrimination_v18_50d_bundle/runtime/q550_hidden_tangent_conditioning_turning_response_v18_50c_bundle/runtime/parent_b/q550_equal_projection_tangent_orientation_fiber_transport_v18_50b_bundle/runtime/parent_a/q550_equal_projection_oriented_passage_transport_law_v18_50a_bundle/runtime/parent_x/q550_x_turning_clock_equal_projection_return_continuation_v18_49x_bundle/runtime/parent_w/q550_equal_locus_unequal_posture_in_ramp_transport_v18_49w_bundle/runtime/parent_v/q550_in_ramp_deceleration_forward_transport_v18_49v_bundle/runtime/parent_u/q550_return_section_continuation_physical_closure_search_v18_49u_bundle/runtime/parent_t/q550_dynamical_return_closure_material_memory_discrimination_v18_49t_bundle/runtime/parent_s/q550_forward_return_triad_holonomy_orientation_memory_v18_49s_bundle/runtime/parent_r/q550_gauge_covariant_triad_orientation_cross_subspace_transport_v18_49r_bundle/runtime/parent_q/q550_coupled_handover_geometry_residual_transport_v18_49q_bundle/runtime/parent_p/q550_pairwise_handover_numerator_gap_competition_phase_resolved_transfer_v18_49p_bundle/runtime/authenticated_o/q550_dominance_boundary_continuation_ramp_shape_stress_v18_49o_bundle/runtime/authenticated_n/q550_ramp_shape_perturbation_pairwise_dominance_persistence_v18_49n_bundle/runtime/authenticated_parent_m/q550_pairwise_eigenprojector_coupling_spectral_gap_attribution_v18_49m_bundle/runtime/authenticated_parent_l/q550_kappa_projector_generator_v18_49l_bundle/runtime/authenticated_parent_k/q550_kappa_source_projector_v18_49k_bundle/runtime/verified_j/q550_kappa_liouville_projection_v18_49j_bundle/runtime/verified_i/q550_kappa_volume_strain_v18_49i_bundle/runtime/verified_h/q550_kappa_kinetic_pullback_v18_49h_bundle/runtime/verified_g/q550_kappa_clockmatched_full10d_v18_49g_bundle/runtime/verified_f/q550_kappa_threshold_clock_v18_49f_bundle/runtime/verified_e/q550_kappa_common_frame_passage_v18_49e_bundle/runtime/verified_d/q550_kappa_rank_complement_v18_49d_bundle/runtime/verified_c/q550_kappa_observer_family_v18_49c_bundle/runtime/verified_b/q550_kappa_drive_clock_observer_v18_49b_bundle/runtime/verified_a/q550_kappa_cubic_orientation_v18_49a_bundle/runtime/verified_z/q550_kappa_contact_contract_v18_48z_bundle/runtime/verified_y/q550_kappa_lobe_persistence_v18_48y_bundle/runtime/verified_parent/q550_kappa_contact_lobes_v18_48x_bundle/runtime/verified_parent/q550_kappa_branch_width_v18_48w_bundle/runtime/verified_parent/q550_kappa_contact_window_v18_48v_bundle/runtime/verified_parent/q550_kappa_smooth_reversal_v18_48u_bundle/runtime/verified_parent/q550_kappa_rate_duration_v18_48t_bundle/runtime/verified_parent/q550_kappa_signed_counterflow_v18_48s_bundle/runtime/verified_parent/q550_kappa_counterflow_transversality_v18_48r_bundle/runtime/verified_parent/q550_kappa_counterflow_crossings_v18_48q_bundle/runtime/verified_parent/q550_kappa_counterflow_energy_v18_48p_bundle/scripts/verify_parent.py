#!/usr/bin/env python3
"""SHA authenticate v18.48o + v18.48j original server sendbacks and ancestors."""
from __future__ import annotations
import hashlib,json,pathlib,subprocess,sys,zipfile
R=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def extract_verified(zip_path,expected,dest):
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip():raise RuntimeError('Corrupt ZIP '+str(zip_path))
        mf=[n for n in z.namelist() if n.endswith('/SHA256SUMS_OUTPUT.json')]
        if len(mf)!=1:raise RuntimeError('Ambiguous archive root')
        root=mf[0].split('/')[0]+'/'
        if mf[0]!=root+'SHA256SUMS_OUTPUT.json':raise RuntimeError('Nested/incorrect manifest')
        m=json.loads(z.read(mf[0]));
        if m['version']!=expected:raise RuntimeError('wrong archive version')
        expected_members={root+r for r in m['files']}|{root+'SHA256SUMS_OUTPUT.json'}
        actual={n for n in z.namelist() if not n.endswith('/')}
        if actual!=expected_members:raise RuntimeError('Unexpected members in '+expected)
        for rel,hashvalue in m['files'].items():
            dst=pathlib.PurePosixPath(rel)
            if '..' in dst.parts or dst.is_absolute():raise RuntimeError('unsafe member')
            if sha(z.read(root+rel))!=hashvalue:raise RuntimeError('member SHA mismatch '+rel)
        for name in sorted(expected_members):
            path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
    return dest/root[:-1],len(m['files'])
def verify():
    pins=json.loads((R/'inputs/SOURCE_PINS.json').read_text())['files']
    for rel,digest in pins.items():
        p=R/rel
        if not p.is_file() or sha(p.read_bytes())!=digest:raise RuntimeError('Source pin mismatch '+rel)
    base=R/'runtime'/'verified_sources'
    o,no=extract_verified(R/'inputs/v18_48o_original_server_sendback.zip','v18.48o',base/'o')
    j,nj=extract_verified(R/'inputs/v18_48j_original_server_sendback.zip','v18.48j',base/'j')
    for ancestor in (o,j):
        subprocess.run([sys.executable,str(ancestor/'scripts/verify_parent.py')],cwd=ancestor,check=True,
                       stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    hp=j/'runtime'/'physical_paths.npz';rh=j/'runtime'/'report_v18_48h.json'
    if sha(hp.read_bytes())!='3d78ce41378b3ce0fb955a281baae1d4bb6f8d107ab17c718cbbdb2a6696405a':
        raise RuntimeError('Genuine full-11D state SHA drift')
    # Confirm the user-supplied current sendback matches its original ancestry.
    import importlib.util
    for n in ('structural_jet.py','generated_base_jet.py','test_support_mobius_monodromy_audit.py'):
        if (R/'reference'/n).read_bytes()!=(j/'reference'/n).read_bytes():raise RuntimeError('Original math mismatch '+n)
    meta=dict(version='v18.48p',o_original_archive_sha256=pins['inputs/v18_48o_original_server_sendback.zip'],
          j_original_archive_sha256=pins['inputs/v18_48j_original_server_sendback.zip'],
          verified_members_o=no,verified_members_j=nj,physical_paths_sha256=sha(hp.read_bytes()),
          verified_h_report_sha256=sha(rh.read_bytes()))
    (R/'runtime'/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
    return hp,rh,meta
if __name__=='__main__':
    hp,rh,meta=verify();print(json.dumps(meta,indent=2))
