#!/usr/bin/env python3
"""Generate scientific report strictly from the current audit's CSV and JSON."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'results/report.json').read_text())
with (ROOT/'results/turning_clock_hidden_response.csv').open() as f:records=list(csv.DictReader(f))
cs=[r for r in records if r['metric']=='common']
base=[r for r in cs if r['kind']=='original' and r['shape']=='beta:2:2']
nedge=sum(r['local_peak_boundary_flag']=='True' for r in cs)
lines=['# Q550 v18.50c — Hidden-Tangent Conditioning & Turning-Response Audit',
 '',f"**Classification:** `{report['classification']}`",'',
 '## Status and input lineage',
 f"- Complete authentic source verification: v18.50b SHA `{report['genealogy']['whole_zip_sha256']}` and {report['genealogy']['parent_manifest_verified']} v18.50b members. Recursive ancestry verified.",
 f"- Q550 return trajectories: {report['statistics']['cases']}; equal-x passage pairs: {report['statistics']['pairs']}; failed cases: {report['statistics']['failures']}.",
 f"- Fixed hidden-coordinate metric scale: `{report['common_scale_4d']}`. This metric is common to all cases, not refitted per trajectory.",
 '', '## Event-centered response — original kappa, cubic ramp',
 '', '| Ramp r | x-turn xi | Direction turning rate at x-turn | Hidden tangent deflection (deg) | Windowed peak lag xi | At window boundary? |',
 '|---:|---:|---:|---:|---:|---|']
for r in sorted(base,key=lambda x:float(x['ramp_xi'])):
 lines.append(f"| {float(r['ramp_xi']):.6f} | {float(r['turn_xi']):.9f} | {float(r['hidden_turn_rate_at_x_turn']):.6f} | {float(r['hidden_direction_change_across_turn_deg']):.6f} | {float(r['peak_minus_x_turn_xi']):+.6f} | {r['local_peak_boundary_flag']} |")
lines.extend(['','## Main findings',
 f"- Hidden direction is positively aligned at all {report['statistics']['pairs']} authenticated equal-x returns under the fixed common metric: `{report['statistics']['all_hidden_tangent_pairs_positive_common_metric']}`.",
 f"- Angle of hidden 4D direction between equal-x passages ranges {report['statistics']['hidden_angle_range_deg'][0]:.3f}–{report['statistics']['hidden_angle_range_deg'][1]:.3f} degrees in the common metric.",
 f"- At measured x-turns, hidden direction turning rate is {report['statistics']['turning_curvature_range'][0]:.4f}–{report['statistics']['turning_curvature_range'][1]:.4f} per xi.",
 f"- {nedge} of {len(cs)} local peak locations lie on the chosen event window boundary and must **not** be interpreted as independently measured peak clocks.",
 f"- Fine-grid vs coarse-grid difference in event turning rate: <= {report['statistics']['max_refinement_turn_rate_difference']:.3e} per xi. Total direction-arc integral differs <= {report['statistics']['max_refinement_arc_difference']:.3e} rad.",
 '', '## Decision and limitations',
 '- The tangent of the hidden sector bends continuously during the x turning. The x projected rate can reverse while the hidden tangent retains an acute angle between the two matched passages.',
 '- This is a numerical association in the full co-driven Q550 system. No direct causal intervention of x on the hidden sector was performed. It is inappropriate to conclude that x **caused** hidden bending.',
 '- The hidden-tangent metric is a common, fixed 4D state-space chart. Reweighting coordinates changes numerical deflection values. The bivector coefficients retain their signs only relative to chosen orientation conventions.',
 '- Peaks at the event-window boundary are censored by the search design; their lags are not physical clocks. Continuous-time/interval certification is not provided.',
 '- Equal x is not equal complete spatial locus or equal physical state. The observed hidden chart is not proof of a physical fiber bundle, cube/octant geometry, material memory, or physical torsion.',
 '- Detailed per-phase dynamics, pairwise diagnostics, four metrics, refined convergence checks and the parent provenance are in the CSV/JSON files.',
 '', '## Suggested next controlled test',
 'Compare one shared drive perturbation at equal starting material states, measuring the first-order hidden-direction response to a controlled variation that demonstrably affects x. Separate common-input correlations from intervention effects before claiming causal coupling.',
 ''])
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines))
print('Generated scientific report.')
