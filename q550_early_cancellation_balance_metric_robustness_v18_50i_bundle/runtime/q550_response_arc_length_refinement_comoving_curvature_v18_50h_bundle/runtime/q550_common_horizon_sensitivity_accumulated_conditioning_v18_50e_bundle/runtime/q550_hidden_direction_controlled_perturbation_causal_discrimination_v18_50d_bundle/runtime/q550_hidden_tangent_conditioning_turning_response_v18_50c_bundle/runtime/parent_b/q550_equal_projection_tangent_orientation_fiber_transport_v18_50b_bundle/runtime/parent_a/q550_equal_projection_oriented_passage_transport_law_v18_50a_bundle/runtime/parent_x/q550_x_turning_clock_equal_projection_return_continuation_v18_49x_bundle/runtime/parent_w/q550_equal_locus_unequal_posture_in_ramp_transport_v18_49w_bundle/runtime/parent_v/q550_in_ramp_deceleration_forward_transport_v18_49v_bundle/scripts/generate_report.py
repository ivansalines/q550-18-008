#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
r=json.loads((R/'results/report.json').read_text())
ref_file=R/'results/sampling_refinement.json'
ref=json.loads(ref_file.read_text()) if ref_file.exists() else None
lines=['# Q550 v18.49v — In-Ramp Deceleration & Forward Transport Audit','',
'**Classification:** `'+r['status']+'`','',
'All results below are obtained from the authentic model and an externally prescribed, finite-duration drive ramp.','',
'## Measurements','',
'| κ₀ | r | speed at drive-zero | material path through ramp | θ net change | valid triad / samples |',
'|---|---:|---:|---:|---:|---:|']
for c in r['cases']:
 lines.append(f"| {c['kappa_kind']} | {c['ramp_xi']:.6f} | {c['rate_at_zero_drive']:.9g} | {c['full_10d_coordinate_path']:.9g} | {c['theta_ramp_net_change']:.3g} | {c['defined_triad_samples']}/{c['defined_triad_samples']+c['undefined_triad_samples']} |")
lines+=['','## Interpretation','',
'The imposed drive reaches zero at σ=0.5 while material degrees of freedom may still move. This is a **drive-zero**, not a mechanical stop. The original 11D mechanical balance is audited on every phase sample.',
'', 'The material path norm is coordinate-defined, and the triad uses the historical initial kinetic material frame. No physical length, time or volume is inferred.',
'', '## Controls','', '```json',json.dumps(r['controls'],indent=2),'```','',
'## Fixed-reference sampling refinement','',
 'All reported triad angles use the SAME σ=0.1 orientation reference, not the first grid point.','',
 (json.dumps(ref,indent=2) if ref else 'Refinement not run. Use --samples 121 for comparison.'),
 '', '## Boundaries and limitations','']
lines+=['- '+s for s in r['limitations']]
(R/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
