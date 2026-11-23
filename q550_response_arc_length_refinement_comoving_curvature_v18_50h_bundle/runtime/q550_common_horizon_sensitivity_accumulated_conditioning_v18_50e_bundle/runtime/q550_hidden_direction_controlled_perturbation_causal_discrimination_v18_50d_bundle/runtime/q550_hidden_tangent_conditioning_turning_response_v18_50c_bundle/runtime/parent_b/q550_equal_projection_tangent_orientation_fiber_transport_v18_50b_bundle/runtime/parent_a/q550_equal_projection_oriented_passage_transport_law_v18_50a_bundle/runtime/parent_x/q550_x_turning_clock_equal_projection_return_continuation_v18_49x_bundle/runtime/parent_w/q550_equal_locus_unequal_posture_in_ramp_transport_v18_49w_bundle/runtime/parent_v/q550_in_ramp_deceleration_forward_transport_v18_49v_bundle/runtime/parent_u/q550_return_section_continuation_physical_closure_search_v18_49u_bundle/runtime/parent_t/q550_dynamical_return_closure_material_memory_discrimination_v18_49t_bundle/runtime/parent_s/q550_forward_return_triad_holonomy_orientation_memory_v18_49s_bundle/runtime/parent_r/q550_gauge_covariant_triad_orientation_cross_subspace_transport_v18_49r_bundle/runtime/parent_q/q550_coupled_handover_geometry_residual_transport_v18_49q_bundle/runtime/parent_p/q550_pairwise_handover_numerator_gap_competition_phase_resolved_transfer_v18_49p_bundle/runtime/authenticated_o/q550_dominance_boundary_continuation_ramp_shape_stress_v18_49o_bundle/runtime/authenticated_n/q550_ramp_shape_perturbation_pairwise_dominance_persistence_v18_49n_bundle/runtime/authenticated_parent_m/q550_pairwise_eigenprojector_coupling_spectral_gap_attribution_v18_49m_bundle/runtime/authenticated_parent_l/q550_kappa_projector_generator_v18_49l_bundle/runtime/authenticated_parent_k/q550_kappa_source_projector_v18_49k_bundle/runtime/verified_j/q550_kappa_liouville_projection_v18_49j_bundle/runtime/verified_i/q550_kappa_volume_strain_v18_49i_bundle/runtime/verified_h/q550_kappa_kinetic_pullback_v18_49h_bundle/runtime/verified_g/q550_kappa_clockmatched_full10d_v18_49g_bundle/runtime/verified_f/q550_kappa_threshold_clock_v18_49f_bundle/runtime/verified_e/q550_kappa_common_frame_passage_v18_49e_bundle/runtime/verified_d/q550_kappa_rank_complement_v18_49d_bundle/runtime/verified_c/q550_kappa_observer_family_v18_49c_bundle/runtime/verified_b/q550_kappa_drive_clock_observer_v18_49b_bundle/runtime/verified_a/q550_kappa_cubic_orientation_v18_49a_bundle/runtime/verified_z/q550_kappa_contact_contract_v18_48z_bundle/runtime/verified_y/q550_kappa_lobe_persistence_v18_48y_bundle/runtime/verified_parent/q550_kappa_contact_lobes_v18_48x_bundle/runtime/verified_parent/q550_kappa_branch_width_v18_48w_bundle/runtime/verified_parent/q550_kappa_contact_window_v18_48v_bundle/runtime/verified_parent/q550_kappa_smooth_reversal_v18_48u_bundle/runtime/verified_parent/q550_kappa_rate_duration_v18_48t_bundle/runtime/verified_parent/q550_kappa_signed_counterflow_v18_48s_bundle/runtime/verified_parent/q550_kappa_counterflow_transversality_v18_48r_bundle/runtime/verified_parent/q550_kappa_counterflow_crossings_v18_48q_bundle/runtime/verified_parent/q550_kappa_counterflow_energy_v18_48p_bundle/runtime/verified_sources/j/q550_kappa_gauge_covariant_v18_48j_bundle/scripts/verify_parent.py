#!/usr/bin/env python3
"""Authenticate unmodified v18.48i server sendback and nested v18.48h sources."""
from __future__ import annotations
import hashlib, io, json, pathlib, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]

def sha(data):return hashlib.sha256(data).hexdigest()

def archive(z,expected_version):
    names=z.namelist()
    mf=[n for n in names if n.endswith('/SHA256SUMS_OUTPUT.json')]
    if len(mf)!=1:raise ValueError(f'ambiguous {expected_version} manifest')
    manifest=json.loads(z.read(mf[0]))
    if manifest['version']!=expected_version:raise ValueError('Unexpected manifest version')
    root=mf[0].rsplit('/',1)[0]+'/'
    for n in names:
        pp=pathlib.PurePosixPath(n)
        if n.startswith('/') or '..' in pp.parts or not n.startswith(root):raise ValueError('unsafe member: '+n)
    members=set(root+n for n in manifest['files'])
    actual={n for n in names if not n.endswith('/') and n!=mf[0]}
    if members!=actual:raise ValueError('Extra/missing manifest members')
    for path,digest in manifest['files'].items():
        if sha(z.read(root+path))!=digest:raise ValueError('SHA drift: '+path)
    return root,manifest

def verify():
    pins=json.loads((ROOT/'inputs/PARENT_SHA256.json').read_text())
    src=(ROOT/'inputs/v18_48i_original_server_sendback.zip').read_bytes()
    if sha(src)!=pins['parent_zip_sha256']:raise ValueError('parent ZIP SHA drift')
    with zipfile.ZipFile(io.BytesIO(src)) as z:
        if z.testzip():raise ValueError('corrupt parent ZIP')
        prefix,m=archive(z,'v18.48i')
        refined=prefix+'inputs/refined_v18_48h/'
        phys=z.read(refined+'physical_paths.npz')
        report=z.read(refined+'report.json')
        repi=json.loads(z.read(prefix+'results/report.json'))
        rep=json.loads(report)
        if repi['version']!='v18.48i' or rep['version']!='v18.48h':raise ValueError('Wrong source reports')
        if not rep['preserved_seed_branch_identity'] or rep['max_clock_section_absolute_error']>2e-10:
            raise ValueError('Parent data not valid')
        pin=(repi['parent'])
        if sha(phys)!=pin['actual_parent_paths_sha256'] or sha(report)!=pin['actual_parent_report_sha256']:
            raise ValueError('Original refined IVP data SHA drift')
        parent_h=z.read(prefix+'inputs/v18_48h_original_server_sendback.zip')
        if sha(parent_h)!=pin['v18_48h_original_server_zip_sha256']:
            raise ValueError('Nested v18.48h SHA drift')
        with zipfile.ZipFile(io.BytesIO(parent_h)) as h:
            if h.testzip():raise ValueError('Nested ZIP corrupted')
            hroot,hm=archive(h,'v18.48h')
            files={'structural_jet.py':hroot+'scripts/structural_jet.py',
                   'generated_base_jet.py':hroot+'scripts/generated_base_jet.py',
                   'test_support_mobius_monodromy_audit.py':hroot+'reference/test_support_mobius_monodromy_audit.py'}
            for name,path in files.items():
                if sha(h.read(path))!=pins['original_sources'][name] or sha((ROOT/'reference'/name).read_bytes())!=pins['original_sources'][name]:
                    raise ValueError('Structural math source SHA drift '+name)
        if sha(z.read(prefix+'scripts/factorial_math.py'))!=pins['original_sources']['factorial_math.py'] or sha((ROOT/'reference/factorial_math.py').read_bytes())!=pins['original_sources']['factorial_math.py']:
            raise ValueError('Factorial source SHA drift')
        dest=ROOT/'runtime'
        dest.mkdir(exist_ok=True)
        (dest/'physical_paths.npz').write_bytes(phys)
        (dest/'report_v18_48h.json').write_bytes(report)
        (dest/'report_v18_48i.json').write_bytes(z.read(prefix+'results/report.json'))
        provenance={'archive_i_sha256':sha(src),'archive_i_verified_members':len(m['files']),
                    'archive_h_sha256':sha(parent_h),'archive_h_verified_members':len(hm['files']),
                    'physical_paths_sha256':sha(phys),'report_h_sha256':sha(report),
                    'historical_source_sha256':pins['original_sources']}
        (dest/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
        return provenance
if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
