#!/usr/bin/env python3
"""Explicit scientific/cardinality gates for v18.48w. No hidden defaults."""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'results'
def read(n):
    with (R/n).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
r=json.loads((R/'report.json').read_text())
n=int(r['historical_paths'])
c=read('combined_branch_contacts.csv');f=read('combined_branch_fixed_phase_energy.csv')
a=read('new_refined_contacts.csv');z=read('new_refined_fixed_phase_energy.csv')
w=read('branch_resolved_work_signs.csv');b=read('branch_resolved_window_summary.csv')
assert r['genuine_new_material_integrations']==n*10
assert len(c)==n*25 and len(f)==n*25*3
assert len(a)==n*8 and len(z)==n*9*3
assert len(w)==n*3 and len(b)==n
assert len(read('original_center_regression.csv'))==n
assert r['maximum_v18_48v_center_regression']<2e-7
assert r['maximum_11D_original_replay_error']<1e-7
assert r['maximum_mechanical_ledger_relative_error']<1e-8
assert r['maximum_equal_phase_energy_ledger_absolute_error']<1e-7
assert r['maximum_drive_phase_mismatch_rad']<1e-8
for x in c:
    assert math.isfinite(float(x['minimum_3D_gap']))
    assert 0<=float(x['minimum_3D_gap'])<=float(x['minimum_11D_gap'])+1e-8
    for t in ('0p0025','0p005','0p01'):
        assert 0<=float(x['contact_total_q_'+t])<=.408
        assert 0<=float(x['contact_longest_q_'+t])<=float(x['contact_total_q_'+t])+1e-9
for x in w:
    assert int(x['ramp_grid_count'])==25
    assert sum(int(x[k]) for k in ('positive_work','negative_work','numerical_zero'))==25
for x in b:
    assert int(x['ramps_count'])==25
    assert float(x['best_sampled_3D_gap'])>0
if n==8:assert r['status']=='FULL_EIGHT_PATH_NUMERICAL_AUDIT'
else:assert r['status']=='PARTIAL_PREFLIGHT_ONLY'
print('v18.48w output gates passed:',n,'authentic original paths; 25 ramp values each; three matched phases')
