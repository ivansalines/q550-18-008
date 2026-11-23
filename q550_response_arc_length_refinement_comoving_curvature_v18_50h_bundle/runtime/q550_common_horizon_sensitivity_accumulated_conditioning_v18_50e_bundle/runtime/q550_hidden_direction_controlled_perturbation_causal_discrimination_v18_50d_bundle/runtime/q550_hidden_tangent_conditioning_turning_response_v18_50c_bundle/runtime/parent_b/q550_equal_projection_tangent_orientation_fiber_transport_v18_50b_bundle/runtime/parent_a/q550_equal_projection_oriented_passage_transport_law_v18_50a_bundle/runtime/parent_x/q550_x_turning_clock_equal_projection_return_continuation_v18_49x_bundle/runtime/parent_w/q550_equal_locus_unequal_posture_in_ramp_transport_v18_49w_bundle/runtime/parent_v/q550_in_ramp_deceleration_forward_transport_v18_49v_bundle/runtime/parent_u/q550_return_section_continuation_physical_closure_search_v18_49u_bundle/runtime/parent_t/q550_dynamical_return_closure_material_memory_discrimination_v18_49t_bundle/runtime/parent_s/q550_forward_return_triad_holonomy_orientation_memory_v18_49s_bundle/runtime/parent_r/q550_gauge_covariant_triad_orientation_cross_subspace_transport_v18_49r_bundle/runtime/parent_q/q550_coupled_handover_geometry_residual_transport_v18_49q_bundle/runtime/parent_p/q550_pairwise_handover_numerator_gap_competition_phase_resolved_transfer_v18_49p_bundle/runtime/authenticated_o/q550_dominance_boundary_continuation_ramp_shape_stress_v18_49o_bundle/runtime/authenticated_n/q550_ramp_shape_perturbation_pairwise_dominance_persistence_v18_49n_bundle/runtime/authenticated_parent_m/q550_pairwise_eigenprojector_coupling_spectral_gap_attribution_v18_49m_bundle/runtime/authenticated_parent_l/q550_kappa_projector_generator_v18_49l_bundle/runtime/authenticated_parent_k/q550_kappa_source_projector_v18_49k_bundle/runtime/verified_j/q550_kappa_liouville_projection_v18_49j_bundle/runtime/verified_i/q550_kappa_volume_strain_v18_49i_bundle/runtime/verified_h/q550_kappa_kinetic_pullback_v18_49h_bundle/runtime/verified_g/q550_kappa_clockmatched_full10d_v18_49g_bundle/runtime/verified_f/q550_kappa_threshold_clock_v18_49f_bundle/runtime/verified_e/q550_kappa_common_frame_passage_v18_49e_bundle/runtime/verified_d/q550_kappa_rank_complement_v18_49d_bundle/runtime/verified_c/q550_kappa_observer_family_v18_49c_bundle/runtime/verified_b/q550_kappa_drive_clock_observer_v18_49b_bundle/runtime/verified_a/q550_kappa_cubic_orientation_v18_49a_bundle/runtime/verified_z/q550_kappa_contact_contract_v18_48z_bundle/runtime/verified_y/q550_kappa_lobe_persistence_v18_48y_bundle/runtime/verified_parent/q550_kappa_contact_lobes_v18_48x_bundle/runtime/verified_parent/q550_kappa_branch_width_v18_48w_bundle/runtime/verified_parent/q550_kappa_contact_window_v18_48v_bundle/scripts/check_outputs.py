#!/usr/bin/env python3
"""Mechanical, genealogy and cardinality output gates."""
import json,csv
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'results'
report=json.loads((R/'report.json').read_text())
def rows(name):
    with (R/name).open(newline='') as f:return list(csv.DictReader(f))
contact=rows('fine_ramp_contacts.csv');fixed=rows('fixed_phase_energy_history.csv')
summary=rows('ramp_window_summary.csv');best=rows('per_path_window_optima.csv')
n=report['historical_paths']
assert report['genuine_material_11D_integrations']==n*26,(report['genuine_material_11D_integrations'],n)
assert len(contact)==n*25
assert len(fixed)==n*25*3
assert len(summary)==17 and len(best)==n
assert report['maximum_relative_mechanical_ledger_residual']<1e-8
assert report['maximum_phase_matched_energy_ledger_abs_residual']<1e-7
assert report['maximum_historical_11D_regression']<1e-7
assert report['maximum_parent_u_profile_regression']<2e-7
assert report['maximum_command_phase_difference_rad']<1e-8
assert report['maximum_preparation_energy_jump_error']<1e-8
assert all(float(r['minimum_3D_gap'])>=0 for r in contact)
assert all(float(r['minimum_11D_gap'])>=0 for r in contact)
if n==8:assert report['status']=='FULL_EIGHT_PATH_NUMERICAL_AUDIT'
else:assert report['status']=='PARTIAL_PREFLIGHT_ONLY'
print('v18.48v output gates passed:',n,'paths',len(contact),'optimized phase contacts')
