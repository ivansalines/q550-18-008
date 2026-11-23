#!/usr/bin/env python3
"""Generate a scientific summary strictly from the computed report JSON."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
def yn(x):return 'YES' if x else 'NO'
lines=[f'# v18.49n — Ramp-Shape Perturbation & Pairwise Dominance Persistence Audit',
'',f'Run classification: **{r["status"]}**.',
'','## Main measured decision',
'',f'- Physical controls: {len(r["shape_set"])} shapes, {len(r["ramp_durations"])} ramp durations, {len(r["kappa_choices"])} kappa choices.',
f'- Total Q550 experiments: {r["total_case_count"]}.',
f'- Pair 6–7 is the final leader in every tested case: **{yn(r["all_cases_final_leader_6_7"])}**.',
f'- Pair 6–7 has final majority in every case: **{yn(r["all_cases_final_majority_6_7"])}**.',
f'- Pair 6–7 remains the leader at every tested sample q∈[0.55,0.65] in every case: **{yn(r["all_cases_6_7_leader_at_all_samples_q055_to_065"])}**.',
f'- Lowest final share across tested cases: **{100*r["worst_final_share_6_7"]:.4f}%**.',
f'- Smallest final advantage over strongest rival: **{100*r["worst_final_leader_margin_6_7"]:.4f} percentage points**.',
f'- Minimum advantage at sampled q>=0.55: **{100*r["worst_margin_q055_to_065"]:.4f} percentage points**.',
'', '## What was controlled','',
'The original Q550 11D ODE and 10D analytic variational equations are replayed from the SHA-authenticated parent genealogy. All brake shapes keep the same end values, duration and integral of the clock-reversal completion function (1/2). Thus the registered return clock after the ramp is common, and the shape of the command is the actual intervention.',
'', '## Numerical lineage and quality','',
f'- Physical forward runs: {r["integration_counts"]["physical_forward_11D"]}; physical return runs: {r["integration_counts"]["physical_return_11D"]}; genuine 10D tangent propagators: {r["integration_counts"]["tangent_10D"]}.',
]
for k,v in r['numeric_controls'].items():lines.append(f'- {k}: {v:.6e}')
lines+=['','## Per-case results','','| kappa | ramp | shape | 6–7 final % | first lead (estimated q) | q>=.55 lead? |', '|---|---:|---|---:|---:|---|']
for x in r['case_summary']:
    o=x['first_overall_dominance_q_estimate'];mark=f'{o:.6f}' if o is not None else 'none'
    lines.append(f'| {x["kappa_kind"]} | {x["ramp_xi"]:.6f} | {x["shape"]} | {100*x["pair_67_share_q065"]:.4f} | {mark} | {yn(x["persists_every_sample_q055_to_065"])} |')
lines+=['','## Interpretation boundary','']
lines.extend('- '+x for x in r['limitations'])
lines+=['','Numerical onset markers are sample-bracketed estimates. Claim persistence only for the tested families, ramps, kappa choices, and declared kinetic metric.']
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
print('Wrote SCIENTIFIC_REPORT.md')
if __name__=='__main__':pass
