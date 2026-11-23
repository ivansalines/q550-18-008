#!/usr/bin/env python3
"""Cross-check exported numerical data against the frozen scientific criteria."""
from pathlib import Path
import json,csv,math
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'results/report.json').read_text())
a=p['identity_controls']
assert a['maximum_pair_generator_norm_sq_residual']<1e-7
assert a['maximum_log_ratio_identity_residual']<1e-9
assert a['maximum_parent_o_pair67_share_difference']<2e-6
assert a['minimum_relative_eigen_gap']>1e-7
assert a['maximum_11D_mechanical_ledger_error']<1e-8
assert a['maximum_11D_forward_replay_error']<1e-7
assert not p['failed_cases'],p['failed_cases']
read=lambda name:list(csv.DictReader((R/'results'/name).open(newline='')))
rows=read('phase_resolved_pair_67_vs_78.csv');traces=read('numerator_gap_pair_traces.csv');sh=read('endpoint_shapley_pair_attribution.csv')
assert len(rows)==sum(c['sample_count'] for c in p['cases'])
assert len(traces)==2*len(rows)
assert len(sh)==2*len(p['cases'])
for x in rows:
    assert abs(float(x['share_78'])-float(x['share_67'])-float(x['share_78_minus_67']))<1e-12
    assert abs(float(x['log_power_ratio_78_over_67'])-float(x['log_numerator_ratio_term'])-float(x['log_inverse_gap_ratio_term']))<1e-9
for c in p['cases']:
    assert abs(c['numerator_shapley_difference']+c['inverse_gap_shapley_difference']-c['delta_raw_difference'])<1e-7
    assert abs(c['shapley_closure_error'])<1e-7
for e in p['phase_crossing_events']:
    assert e['six_seven_seven_eight_top_two'],'Pair equality must also be a leading pair handover'
    assert abs(e['crossing_residual'])<1e-9
    assert e['phase_bracket_low']<=e['phase_q_root']<=e['phase_bracket_high']
print('PASS v18.49p numeric controls, pairwise identity, leading-pair root and two-factor Shapley closure')
