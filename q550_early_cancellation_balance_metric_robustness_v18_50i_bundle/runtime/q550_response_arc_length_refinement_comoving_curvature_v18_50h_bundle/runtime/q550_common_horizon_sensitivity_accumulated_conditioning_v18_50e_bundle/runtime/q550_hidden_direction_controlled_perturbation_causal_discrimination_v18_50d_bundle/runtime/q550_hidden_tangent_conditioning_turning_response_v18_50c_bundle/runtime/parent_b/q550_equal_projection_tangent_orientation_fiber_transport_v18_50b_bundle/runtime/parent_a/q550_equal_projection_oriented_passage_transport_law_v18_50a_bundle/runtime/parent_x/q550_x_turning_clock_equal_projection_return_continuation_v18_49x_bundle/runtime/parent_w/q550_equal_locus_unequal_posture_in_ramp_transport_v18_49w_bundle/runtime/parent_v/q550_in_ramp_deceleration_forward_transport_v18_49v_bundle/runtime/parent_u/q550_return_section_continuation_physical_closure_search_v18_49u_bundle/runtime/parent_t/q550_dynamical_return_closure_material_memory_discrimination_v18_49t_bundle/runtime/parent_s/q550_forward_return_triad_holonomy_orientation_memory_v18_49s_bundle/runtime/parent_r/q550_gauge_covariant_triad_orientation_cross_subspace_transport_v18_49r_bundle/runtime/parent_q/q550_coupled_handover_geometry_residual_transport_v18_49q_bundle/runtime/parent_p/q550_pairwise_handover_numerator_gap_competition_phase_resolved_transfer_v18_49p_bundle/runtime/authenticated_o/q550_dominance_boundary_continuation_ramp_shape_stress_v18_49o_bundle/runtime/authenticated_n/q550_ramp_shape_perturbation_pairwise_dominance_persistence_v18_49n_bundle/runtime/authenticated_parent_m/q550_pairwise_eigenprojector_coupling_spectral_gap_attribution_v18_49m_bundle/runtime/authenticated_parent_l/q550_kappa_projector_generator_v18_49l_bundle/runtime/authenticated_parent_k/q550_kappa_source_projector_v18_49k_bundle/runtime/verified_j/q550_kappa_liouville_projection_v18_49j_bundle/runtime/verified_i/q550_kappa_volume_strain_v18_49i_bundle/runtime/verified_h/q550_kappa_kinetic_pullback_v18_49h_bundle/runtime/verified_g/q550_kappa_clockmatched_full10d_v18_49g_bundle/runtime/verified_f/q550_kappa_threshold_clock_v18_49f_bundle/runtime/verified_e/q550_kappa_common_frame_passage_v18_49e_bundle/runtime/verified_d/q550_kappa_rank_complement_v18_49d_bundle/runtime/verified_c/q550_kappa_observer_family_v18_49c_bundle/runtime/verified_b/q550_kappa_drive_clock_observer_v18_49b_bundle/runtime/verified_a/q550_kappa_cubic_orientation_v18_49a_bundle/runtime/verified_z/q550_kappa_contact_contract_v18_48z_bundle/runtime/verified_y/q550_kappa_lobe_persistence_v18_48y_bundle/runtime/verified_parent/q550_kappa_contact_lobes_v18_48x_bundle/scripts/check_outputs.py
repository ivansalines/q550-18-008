#!/usr/bin/env python3
"""Scientific acceptance gates: fail rather than overwrite unsupported claims."""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'results'
def read(n):
    with (R/n).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
r=json.loads((R/'report.json').read_text())
p=read('focus_lobe_profiles.csv');c=read('phase_lobe_summary.csv')
xx=read('extended_lobe_intervals.csv');rr=read('original_w_width_regression.csv')
a=read('candidate_two_to_one_brackets.csv');b=read('critical_barrier_refinement.csv')
assert r['version']=='v18.48x' and r['status']=='FULL_EIGHT_PATH_FLOATING_POINT_AUDIT'
assert r['historical_paths']==8
assert r['actual_new_11D_integrations']==72
assert len(c)==42 and len(xx)==168 and len(p)==2*18*1601 and len(rr)==16
assert len(a)==2 and len(b)==2*(2+9+1)
assert r['maximum_original_11D_replay_error']<1e-7
assert r['maximum_energy_ledger_relative_error']<1e-8
assert r['maximum_w_width_regression_error']<3e-5
for row in c:
    assert 0<=float(row['minimum_grid_gap'])<=float(row['minimum_grid_full11D_gap'])+1e-8
    assert abs(float(row['minimum_grid_energy_gap']))<10.
    assert int(row['components_extended'])>=1
for row in a:
    assert row['event_classification']=='INTERIOR_TWO_TO_ONE_NUMERICAL_MERGER'
    assert float(row['left_ramp_xi'])<float(row['right_ramp_xi'])
for row in b:
    if row['is_final_bracket']=='1':
        assert float(row['critical_bracket_width_xi'])<5e-7
        assert .2962<float(row['critical_bracket_left'])<.29675
    else:
        for x in ('barrier_minus_threshold','barrier_distance_3D','barrier_full_11D_gap'):
            assert math.isfinite(float(row[x]))
            assert float(row['barrier_full_11D_gap'])>1.
assert all(float(row['absolute_width_error'])<3e-5 for row in rr)
print('v18.48x scientific gates passed: 8 paths, 72 original 11D integrations, two subthreshold mergers, full 11D remains distinct')
