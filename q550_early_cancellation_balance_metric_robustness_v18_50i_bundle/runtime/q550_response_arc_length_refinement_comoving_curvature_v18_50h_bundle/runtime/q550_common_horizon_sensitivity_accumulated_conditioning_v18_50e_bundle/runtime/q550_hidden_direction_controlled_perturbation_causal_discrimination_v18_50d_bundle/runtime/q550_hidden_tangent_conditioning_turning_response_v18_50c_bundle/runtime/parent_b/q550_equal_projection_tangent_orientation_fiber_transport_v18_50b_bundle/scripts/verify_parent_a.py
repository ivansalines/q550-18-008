"""Verify entire authentic v18.50a sendback and extract executable v18.49x lineage."""
from pathlib import Path
import hashlib,zipfile,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(buf):return hashlib.sha256(buf).hexdigest()
def verify():
    pin=json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())
    src=ROOT/'inputs'/pin['parent_file']
    if sha(src.read_bytes())!=pin['parent_sha256']:raise RuntimeError('Parent v18.50a ZIP SHA mismatch')
    with zipfile.ZipFile(src) as z:
        if z.testzip() is not None:raise RuntimeError('v18.50a ZIP CRC error')
        pre=pin['parent_root']+'/'
        manifest=json.loads(z.read(pre+'SHA256SUMS_OUTPUT.json'))
        if manifest['version']!='v18.50a' or manifest['root']!=pin['parent_root'] or len(manifest['files'])!=pin['parent_manifest_entries']:
            raise RuntimeError('v18.50a manifest metadata mismatch')
        if set(z.namelist())!={pre+n for n in manifest['files']}|{pre+'SHA256SUMS_OUTPUT.json'}:raise RuntimeError('v18.50a unexpected ZIP members')
        dest=ROOT/'runtime/parent_a'/pin['parent_root']
        for rel,digest in manifest['files'].items():
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts:raise RuntimeError('Unsafe ZIP member')
            buf=z.read(pre+rel)
            if sha(buf)!=digest:raise RuntimeError('v18.50a member SHA mismatch '+rel)
            target=dest/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(buf)
        (dest/'SHA256SUMS_OUTPUT.json').write_bytes(z.read(pre+'SHA256SUMS_OUTPUT.json'))
    report=json.loads((dest/'results/report.json').read_text())
    if report['classification']!=pin['parent_classification'] or report['counts']['matched_passages_replayed']!=34:
        raise RuntimeError('Unexpected parent v18.50a classification/counts')
    sys.path.insert(0,str(dest/'scripts'))
    spec=importlib.util.spec_from_file_location('v18_50b_verified_parent_a',dest/'scripts/verify_parent_x.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    xroot,xreport,ancestry=mod.verify()
    return dest,report,xroot,{'parent_a_sha256':pin['parent_sha256'],'parent_manifest_verified':len(manifest['files']),'all_x_and_older_ancestry_verified':ancestry['upstream_authenticated']}
