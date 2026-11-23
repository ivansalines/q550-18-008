#!/usr/bin/env python3
"""Output cardinality, phase equality, work identity and ancestor regressions."""
from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]
def readcsv(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def main():
    report=json.loads((ROOT/'results/report.json').read_text())
    rows=readcsv(ROOT/'results/phase_locked_contacts.csv')
    phase=readcsv(ROOT/'results/common_phase_profiles.csv')
    assert len(rows)==report['phase_matched_minima']
    assert len(phase)==report['common_phase_profile_points']
    assert report['genuine_11D_integrations']==report['expected_11D_integrations']
    assert len(rows)==report['historical_paths_used']*len(report['alpha_values'])*len(report['drive_designs'])
    assert len(phase)==len(rows)*report['phase_nodes']
    assert report['maximum_original_path_regression']<1e-7
    assert report['maximum_return_energy_relative_residual']<1e-8
    assert report['maximum_phase_matched_ledger_absolute_residual']<1e-7
    assert report['maximum_external_phase_mismatch']<5e-9
    assert report['maximum_original_t_control_regression']<2e-7
    assert report['maximum_preparation_jump_identity_residual']<1e-9
    for row in rows:
        assert abs(float(row['matched_min_phase_difference_rad']))<5e-9
        assert abs(float(row['phase_matched_energy_ledger_residual']))<1e-7
        assert float(row['phase_matched_min_distance_3D'])>=0
    print('PASS v18.48u outputs',len(rows),'phase-locked minima',len(phase),'common-phase rows',report['status'])
if __name__=='__main__':main()
