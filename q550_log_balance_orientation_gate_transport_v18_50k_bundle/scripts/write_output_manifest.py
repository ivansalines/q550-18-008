#!/usr/bin/env python3
"""Generate an execution-specific SHA256 manifest; NO original-source hash edits."""
import hashlib,json,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    resultdir=ROOT/'results'
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(resultdir.iterdir()) if p.is_file()}
    if not files:raise RuntimeError('No output files')
    report={'version':'v18.50k','mode':'execution-specific output manifest',
            'python':platform.python_version(), 'file_sha256':files}
    (ROOT/'SHA256SUMS_OUTPUT.json').write_text(json.dumps(report,indent=2)+'\n')
    print('v18.50k execution manifest written:',len(files),'result files')
if __name__=='__main__':main()
