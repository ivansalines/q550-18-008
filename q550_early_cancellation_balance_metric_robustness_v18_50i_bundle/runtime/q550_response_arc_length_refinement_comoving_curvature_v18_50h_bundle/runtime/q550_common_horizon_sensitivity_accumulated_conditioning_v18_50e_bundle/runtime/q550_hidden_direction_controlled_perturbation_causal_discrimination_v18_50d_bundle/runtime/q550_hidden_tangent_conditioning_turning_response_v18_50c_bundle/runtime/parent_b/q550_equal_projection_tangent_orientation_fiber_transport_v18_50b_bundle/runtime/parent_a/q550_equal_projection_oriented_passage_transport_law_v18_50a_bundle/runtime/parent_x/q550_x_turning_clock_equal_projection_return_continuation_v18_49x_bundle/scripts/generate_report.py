#!/usr/bin/env python3
"""Generate scientific report from completed v18.49x true-solver outputs."""
import json,csv
from pathlib import Path
R=Path(__file__).resolve().parents[1];data=json.loads((R/'results/report.json').read_text())
with (R/'results/equal_projection_return_pairs.csv').open() as f:P=list(csv.DictReader(f))
cases=data['cases'];done=[x for x in cases if x['turn_xi'] is not None]
low=min(done,key=lambda x:abs(x['turn_minus_drive_xi'])) if done else None
pp=sorted(P,key=lambda x:float(x['x_residual'])**2)
example=next((p for p in pp if p['triad_projector_frobenius_gap']),None)
L=['# v18.49x — X-Turning Clock & Equal-Projection Return Continuation Audit','',
'## Status',f"`{data['classification']}`",'',
'## Authentic execution',
f"- Reintegrated cases: **{data['counts']['cases_completed']}**; failures: **{data['counts']['failed_cases']}**.",
f"- Sign-bracketed turning roots: **{data['counts']['turning_roots']}**; exact equal-x projection pair roots: **{data['counts']['matching_projections']}**.",
'- The same source physical Q550 11D model and 10D tangent kinetic-frame embedding are used, with upstream SHA-256 ancestry checked.',
'- Event times are *measured* for each trajectory rather than fixed to a common ξ or σ.',
'', '## Physical and projected observables','',
'`x = logistic(y[8])` and `dx/dξ = x(1−x) * f[8]` for the original structural RHS. Zeros of the latter are bracketed and refined with Brent’s method.',
'The prescribed drive zero is a separate control event at σ=1/2 (for the symmetric profiles).',
'In an equal-projection pair, the later intersection is found by a second scalar root solve on the actual dense 11D solution; radial coordinates, angular posture, energy and spectral projectors are evaluated independently.',
'', '## Case events','',
'| κ₀ | ramp r | shape | ξ turn | σ turn | ξturn − ξdrive | matches |',
'|---|---:|---|---:|---:|---:|---:|']
for c in cases:
 def fmt(z):return f'{z:.9f}' if z is not None else 'not observed'
 L.append(f"| {c['kappa_kind']} | {c['ramp_xi']:.6f} | `{c['shape']}` | {fmt(c['turn_xi'])} | {fmt(c['turn_sigma'])} | {fmt(c['turn_minus_drive_xi'])} | {c['matched_projection_pairs']} |")
if low:
 L.extend(['','## Nearness of turning and prescribed drive zero',
 f"The smallest absolute difference among sampled cases occurs at κ₀={low['kappa_kind']}, ramp={low['ramp_xi']}, shape={low['shape']}: `Δξ={low['turn_minus_drive_xi']:.9f}`. This is neither a certified zero nor a universal clock."])
if example:
 L.extend(['','## A genuine equal-projection pair (selected from solved roots)',
 f"- κ₀={example['kappa_kind']}, r={example['ramp_xi']}, shape={example['shape']}",
 f"- ξin={float(example['xi_in']):.10f}; ξout={float(example['xi_out']):.10f}; |Δx|={abs(float(example['x_residual'])):.3e}.",
 f"- Angular posture gap {float(example['posture_theta_pair_gap_rad']):.7f} rad; 3D span-normalized locus gap {float(example['locus_3d_span_scaled_gap']):.7f}.",
 f"- Triad projector Frobenius gap {float(example['triad_projector_frobenius_gap']):.7f}; maximum principal angle {float(example['triad_max_principal_angle_deg']):.7f} degrees."])
L.extend(['','## Numerical controls',
 f"- Original forward-history regression: `{data['controls']['initial_forward_regression']:.3e}`.",
 f"- Max mechanical ledger error: `{data['controls']['maximum_ledger_error']:.3e}`.",
 f"- Max w endpoint regression: `{data['controls']['maximum_parent_regression']:.3e}`.",
 f"- Max event shift after doubling scan grid: `{data['controls']['maximum_turn_grid_shift']:.3e}`.",
'', '## Interpretation constraints'])
for v in data['limitations']: L.append('- '+v)
L.extend(['', 'The scope is a **numerical event-clock diagnostic**, not a physical time law, spatial-volume certificate, material-memory certificate, or proof of Q550 realizing the autonomous cube/quadrant construction.',''])
(R/'SCIENTIFIC_REPORT.md').write_text('\n'.join(L))
print('REPORT_DONE',flush=True)
