#!/usr/bin/env python3
"""Check cardinalities, phase lock, seed regression and mechanical ledgers."""
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/'results'/name).open(newline='') as f:return list(csv.DictReader(f))
def main():
    rep=json.loads((ROOT/'results/report.json').read_text())
    contacts=rows('protocol_contacts.csv');profiles=rows('common_phase_profiles.csv')
    assert len(contacts)==rep['same_external_phase_minima']
    assert len(profiles)==rep['common_phase_profile_points']
    assert len(contacts)==rep['historical_paths_used']*rep['independent_designs']*len(rep['alpha_values'])
    assert len(profiles)==len(contacts)*rep['controls']['common_phase_nodes']
    assert rep['genuine_11D_integrations']==rep['expected_11D_integrations']
    assert rep['max_original_11D_path_regression']<1e-7
    assert rep['max_reverse_ledger_relative_residual']<1e-8
    assert rep['max_partial_flip_kinetic_jump_error']<1e-9
    assert rep['max_phase_locked_ledger_absolute_residual']<1e-7
    assert rep['max_phase_clock_mismatch']<1e-9
    assert rep['original_v18_48s_control_regression']['max_shape_gap']<1e-8
    assert rep['original_v18_48s_control_regression']['max_signed_drive_power_gap']<1e-7
    assert rep['equal_rate_duration_prefix_test']['max_shape_gap']<1e-9
    assert rep['equal_rate_duration_prefix_test']['max_energy_or_power_difference']<1e-9
    for c in contacts:
        assert abs(float(c['min_external_phase_difference_rad']))<1e-9
        assert abs(float(c['min_energy_ledger_residual']))<1e-7
        assert 0<=float(c['alpha'])<=1
        assert float(c['phase_locked_min_distance'])>=0
        assert float(c['min_full11D_distance'])>=float(c['phase_locked_min_distance'])-1e-8
    print('PASS v18.48t output gates:',len(contacts),'controls;',len(profiles),'matched-phase profile points;',rep['status'])
if __name__=='__main__':main()
