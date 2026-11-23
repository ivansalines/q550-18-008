#!/usr/bin/env python3
"""Numerical decision gates: reject incomplete or scientifically misleading replay."""
from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def table(name):
    with (R/name).open() as f:return list(csv.DictReader(f))
s=json.loads((R/'report.json').read_text())
assert s['version']=='v18.48z'
assert s['status']=='FULL_AUTHENTIC_11D_NORMAL_FORM_DIAGNOSTIC'
assert s['fresh_11D_integration_count']==14
assert s['fresh_continuous_root_comparisons']==48
assert s['parent_authenticated_11D_profiles']==46
assert s['high_order_jet_fits']==276
assert s['archived_grid_root_comparisons']==184
assert s['cross_branch_W_screen_rows']==8
assert len(table('normal_form_jets.csv'))==276
assert len(table('parent_grid_gap_screen.csv'))==184
assert len(table('continuous_11D_root_validation.csv'))==48
assert len(table('historical_W_cross_branch_screen.csv'))==8
assert s['max_full_11D_replay_error']<1e-7
assert s['maximum_mechanical_ledger_relative_error']<1e-8
assert s['minimum_full_11D_separation_direct']>1.0
assert s['max_quadratic_relative_gap_error_direct']<.002
assert s['max_quartic_relative_gap_error_direct']<.0001
assert s['max_sextic_relative_gap_error_direct']<.00001
assert s['max_affine_parameterization_ratio_error']<1e-12
all_data=table('continuous_11D_root_validation.csv')
for row in all_data:
    assert float(row['dense_IVP_left_root_q'])<float(row['barrier_phase'])<float(row['dense_IVP_right_root_q'])
    assert float(row['true_dense_IVP_gap_q'])>0
    assert float(row['barrier_full_11D_distance'])>1
    assert abs(float(row['barrier_energy_gap']))>1e-5
    assert 0.99<float(row['ratio_I_dense_IVP'])<1.02
    assert abs(float(row['parent_barrier_replay_abs_error']))<2e-7
for row in table('normal_form_jets.csv'):
    assert float(row['parent_dense_curvature'])<-1.
    assert float(row['fitted_curvature'])<-1.
print('PASS v18.48z: 14 genuine 11D IVPs, 48 direct root pairs, Y 46 profiles, 8 W branch screens, precise historical SHA genealogy.')
