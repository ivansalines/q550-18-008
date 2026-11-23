#!/usr/bin/env python3
"""Refuse misleading/incomplete v18.49a output."""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'results'
def load(name):
    with (R/name).open() as f:return list(csv.DictReader(f))
s=json.loads((R/'report.json').read_text())
assert s['version']=='v18.49a'
assert s['status'] in ('FULL_FRESH_11D_CHART_AUDIT','AUTHENTIC_PARENT_11D_REANALYSIS')
assert len(load('physical_phase_skew.csv'))==48
assert len(load('chart_counterfactuals.csv'))==240
assert len(load('independent_chart_jet_refits.csv'))==60
assert len(load('physical_drive_phase_clock.csv'))==36
assert len(load('topological_contact_control.csv'))==6
assert s['monotone_chart_raw_cubic_sign_reversals']==12
assert s['all_parent_physical_midpoint_shifts_positive']
assert s['all_physical_sextic_fitted_skews_positive']
assert s['maximum_root_chart_roundtrip_error']<1e-12
assert s['maximum_clock_calibration_residual']<1e-12
assert s['max_independent_chart_jet_discrepancy']<.02
assert s['minimum_full_11D_distance_at_barrier']>1.
if s['status']=='FULL_FRESH_11D_CHART_AUDIT':
    assert s['new_integrations_in_current_run']==14
    assert s['maximum_parent_reintegration_difference']<1e-9
    assert s['max_new_mechanical_ledger_residual']<1e-8
for row in load('topological_contact_control.csv'):
    assert int(row['original_number_of_components'])==int(row['mapped_number_of_components'])
for row in load('chart_counterfactuals.csv'):
    assert float(row['max_root_roundtrip_error'])<1e-12
    assert abs(float(row['recovered_physical_cubic'])-float(next(x['physical_phase_local_fitted_cubic'] for x in load('physical_phase_skew.csv') if x['kappa_kind']==row['kappa_kind'] and x['ramp_duration_xi']==row['ramp_duration_xi'] and x['delta']==row['delta'])))<1e-10
print('PASS v18.49a: authentic Z genealogy, positive clock-calibrated skew, negative monotone-chart cubic, 48 direct roots and consistent component counts.')
