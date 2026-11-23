from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];d=json.loads((R/'results/report.json').read_text())
lines=['# Q550 v18.49t — Dynamical Return Closure & Material-Memory Discrimination Audit','',
'## Status',d['status'],'',
'Authentic 11D forward and 11D return with external velocity reversal and finite drive reversal. No connector-enforced loop closure.','',
'## Evidence',f"- Physical cases: {d['counts']['cases']}", f"- Optimized geometric comparisons: {d['counts']['sections']}",
 f"- Strictly closed comparisons: {d['counts']['strict_closed_sections']}",
 f"- Failed spectral evaluations: {d['counts']['spectral_failed_sections']}",
 f"- Maximum continuous mechanical ledger error: {d['controls']['max_physical_ledger_error']:.8g}",
 f"- Maximum turnaround energy jump: {d['controls']['max_turning_energy_jump']:.8g}",'',
 '## Best geometric matches (not asserted physical closure)','',
 '| κ₀ / ramp | Forward anchor | Return t | Configuration gap | Velocity reversal gap | Δ mechanical E | Common-frame projector gap | Strict match |',
 '|---|---:|---:|---:|---:|---:|---:|---|']
for x in d['physical_sections']:
 pg=x['spectral_projector_distance_common_frame']
 pstr=f'{pg:.6g}' if pg is not None else 'unresolved'
 lines.append(f"| {x['kappa_kind']} / {x['ramp_xi']:.9f} | {x['forward_anchor_time']:.3f} | {x['return_match_time']:.8f} | {x['configuration_distance']:.6g} | {x['reverse_velocity_gap']:.6g} | {x['energy_difference']:.6g} | {pstr} | {bool(x['strict_return_closed'])} |")
lines+=['','## Interpretation','',
  'The best return sections are selected by a stated six-coordinate geometry metric with periodic phases. Such selection is not an identification of the complete 11D state.',
  'The physically integrated return may not close at the same configuration, velocity and energy. A nonzero difference without matched endpoints **cannot** certify hysteretic material memory or a closed-loop holonomy.',
  'Energy is the original mechanical energy with exact explicit work/dissipation ledger, NOT an assumed conserved total energy.',
  'The common-frame spectral comparison includes the exact velocity-flip tangent Jacobian. It is a diagnostic, not a holonomy angle in an actually closed physical loop.','',
  '## Scope and limitations','']
lines+=['- '+x for x in d['limitations']]
lines+=['','## Reproduction','','All measured values come from actual Python integrations and generated CSV/JSON, not predetermined figures. An unchanged pinned v18.49s sendback retains the executable ancestry.','']
(R/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines))
