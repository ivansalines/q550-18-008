#!/usr/bin/env python3
"""Generate concise empirical report from numerical outputs and original ancestor hashes."""
import json,csv
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'results/report.json').read_text());a=p['identity_controls']
traces=list(csv.DictReader((R/'results/numerator_gap_pair_traces.csv').open()))
s=[]
s.append('# Q550 v18.49p — Pairwise Handover: Numerator–Gap Competition & Phase-Resolved Transfer Audit')
s.append('\n**Status:** '+p['status']+'\n')
s.append('Original v18.49o server SHA256: `'+p['parent_source_authentication']['sha256']+'`. Its 152 manifest entries and all historical parents were checked. Original physical 11D and 10D tangent dynamics and the fixed kinetic metric are preserved.\n')
s.append('## Phase-resolved event table\n')
s.append('| κ₀ | r | numerical event q | pair shares at equality | top-2 check |')
s.append('|---|---:|---:|---:|---|')
for ev in p['phase_crossing_events']:
 s.append(f"| {ev['kappa_kind']} | {ev['ramp_xi']:.9f} | {ev['phase_q_root']:.12f} | {ev['share_at_root']:.6f} | {'PASS' if ev['six_seven_seven_eight_top_two'] else 'FAIL'} |")
s.append('\nThe numerical roots are found by re-evaluating the integrated physical trajectory and its variational operator, not by fitting the old CSV values. They are not rigorous interval-certified roots.\n')
s.append('## Exact two-factor endpoint accounting\n')
s.append('For each rank pair, raw squared generator contribution is `A_ij=2(N_ij/g_ij)^2`. The pairwise difference satisfies `Δ(A78−A67)=Δ_N+Δ_g` exactly under symmetric endpoint Shapley accounting. This algebraic partition is not causal attribution.\n')
s.append('| κ₀ | r | Δ_N / Δ(A78−A67) | Δ_g / Δ(A78−A67) | endpoint leader |')
s.append('|---|---:|---:|---:|---|')
for c in p['cases']:
 s.append(f"| {c['kappa_kind']} | {c['ramp_xi']:.9f} | {c['numerator_share_of_raw_difference_change']:.4%} | {c['inverse_gap_share_of_raw_difference_change']:.4%} | {c['leading_pair_at_end']} |")
s.append('\n## Numerator and gap of the handover pair at r=0.327375\n')
for kind in p['kappa_kinds']:
 for pair in ('6-7','7-8'):
  vals=[r for r in traces if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.327375)<1e-10 and r['pair']==pair]
  if not vals:continue
  x,y=vals[0],vals[-1]
  n0,n1=float(x['numerator_abs']),float(y['numerator_abs'])
  g0,g1=float(x['gap']),float(y['gap'])
  s.append(f"- **{kind}, pair {pair}:** |N| {n0:.9f} → {n1:.9f} ({n1/n0:.4f}×); gap {g0:.9f} → {g1:.9f} ({g1/g0:.4f}×); raw power {float(x['raw_power']):.8f} → {float(y['raw_power']):.8f}.")
s.append('\n## Controls and limits\n')
for key,val in a.items():s.append(f'- {key}: {val:.12g}')
s.append('\nAll 45 pairs are ranked to determine global leadership; the two compared couples are tracked by eigenvalue rank in one fixed initial kinetic metric. Phase-resolved pair equality is not automatically a material torsion flip or a new physical law. Numerical sampling does not certify uniqueness on the continuous phase interval.\n')
(R/'SCIENTIFIC_REPORT.md').write_text('\n'.join(s)+'\n')
print('Generated scientific report')
