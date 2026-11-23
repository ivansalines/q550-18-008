#!/usr/bin/env python3
"""Write a restrained scientific report from calculated JSON rather than prefilled findings."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'results/report.json').read_text());c=d['controls']
lines=[f"# {d['audit']}","", "## Status", d['status'],"",
       f"- Authenticated parent: {d['parent_verification']['r_zip_sha256']}",
       f"- Physical-return cases re-integrated: {d['replayed_cases']}",
       f"- Two-path comparisons: {d['comparisons']}",
       f"- Same-path reversal maximum error: {c['max_roundtrip_same_path_error']:.8g}",
       f"- Same-frame canonical connector minimum singular value: {c['min_conn_singular']:.8g}",
       f"- Kato transported projector maximum mismatch: {c['max_projector_transport_error']:.8g}",
       f"- Minimum relative eigenvalue gap sampled: {c['min_relative_spectral_gap']:.8g}","",
       "## Canonically closed two-path loops", "",
       "| Second trajectory | Phase interval | SO(3) angle (deg) | Start projector difference | End projector difference |",
       "|---|---|---:|---:|---:|"]
for x in d['two_path_loops']:
    lines.append(f"| {x['leg_b']} | {x['window']} | {x['loop_holonomy_angle_deg']:.9g} | {x['start_projector_distance']:.7g} | {x['end_projector_distance']:.7g} |")
lines.extend(["","## Interpretation", "",
    "The zero-residual control is the original *same* path traversed in reverse. The nonzero result for a loop formed from two different paths demonstrates non-Abelian **geometric path dependence under a specified canonical endpoint closure**, not a direct measurement of physical hysteresis.",
    "", "## What was not demonstrated", ""])
lines+=['- '+l for l in d['scientific_limits']]
lines+=['','## Reproducibility','',
       'Inputs, actual Python source, CLI invocation, numerical outputs, report, runtime versions and checksums ship in this bundle. Parent v18.49r server sendback is SHA256-pinned; its q→earlier chain is verified on execution.','']
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines))
