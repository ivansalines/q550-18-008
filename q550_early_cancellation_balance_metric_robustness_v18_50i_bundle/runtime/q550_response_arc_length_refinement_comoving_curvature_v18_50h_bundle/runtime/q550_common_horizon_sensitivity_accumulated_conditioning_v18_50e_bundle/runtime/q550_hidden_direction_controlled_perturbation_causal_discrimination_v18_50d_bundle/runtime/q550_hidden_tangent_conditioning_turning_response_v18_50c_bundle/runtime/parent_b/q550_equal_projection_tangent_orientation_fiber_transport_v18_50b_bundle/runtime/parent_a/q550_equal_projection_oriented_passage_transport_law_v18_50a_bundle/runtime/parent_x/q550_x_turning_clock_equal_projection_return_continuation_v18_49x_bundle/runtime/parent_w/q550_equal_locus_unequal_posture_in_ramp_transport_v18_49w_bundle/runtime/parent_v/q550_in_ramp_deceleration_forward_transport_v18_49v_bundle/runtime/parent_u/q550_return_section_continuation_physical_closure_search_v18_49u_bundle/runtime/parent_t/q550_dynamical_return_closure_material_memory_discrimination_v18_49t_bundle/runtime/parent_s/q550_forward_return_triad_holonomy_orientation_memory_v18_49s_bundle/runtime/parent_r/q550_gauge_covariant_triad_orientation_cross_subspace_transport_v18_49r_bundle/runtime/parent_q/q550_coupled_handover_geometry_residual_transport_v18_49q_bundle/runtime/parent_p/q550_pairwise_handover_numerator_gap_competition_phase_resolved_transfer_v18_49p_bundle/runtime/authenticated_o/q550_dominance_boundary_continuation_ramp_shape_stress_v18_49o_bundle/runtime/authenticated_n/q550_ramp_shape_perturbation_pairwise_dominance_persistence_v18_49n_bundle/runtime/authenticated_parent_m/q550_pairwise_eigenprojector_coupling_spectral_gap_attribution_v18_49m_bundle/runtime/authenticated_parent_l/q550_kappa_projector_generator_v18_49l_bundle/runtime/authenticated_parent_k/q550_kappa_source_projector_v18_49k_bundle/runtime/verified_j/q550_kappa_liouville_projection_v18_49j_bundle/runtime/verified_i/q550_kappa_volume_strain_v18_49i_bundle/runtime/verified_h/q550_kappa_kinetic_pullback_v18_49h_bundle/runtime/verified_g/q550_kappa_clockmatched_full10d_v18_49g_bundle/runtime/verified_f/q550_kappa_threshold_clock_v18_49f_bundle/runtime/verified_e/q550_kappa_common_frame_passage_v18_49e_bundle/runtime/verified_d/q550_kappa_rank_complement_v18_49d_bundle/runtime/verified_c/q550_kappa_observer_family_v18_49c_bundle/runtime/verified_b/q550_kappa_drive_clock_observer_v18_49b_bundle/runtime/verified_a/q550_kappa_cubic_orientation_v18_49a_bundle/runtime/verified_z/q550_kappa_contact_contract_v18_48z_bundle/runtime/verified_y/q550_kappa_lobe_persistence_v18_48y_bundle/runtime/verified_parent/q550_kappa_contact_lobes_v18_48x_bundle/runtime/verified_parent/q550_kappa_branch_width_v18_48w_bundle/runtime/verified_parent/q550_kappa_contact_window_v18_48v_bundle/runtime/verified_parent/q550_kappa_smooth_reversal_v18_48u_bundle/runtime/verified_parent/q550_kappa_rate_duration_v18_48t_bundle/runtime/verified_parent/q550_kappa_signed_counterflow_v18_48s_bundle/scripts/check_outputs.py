#!/usr/bin/env python3
"""Independent CSV-level scientific gates for v18.48s output."""
from pathlib import Path
import csv,json,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open(newline='') as f:return list(csv.DictReader(f))
def main():
    rep=json.loads((ROOT/'results/report.json').read_text())
    contacts=read('signed_contacts.csv');root=read('signed_projected_crossings.csv')
    one=read('phase_locked_one_coordinate_roots.csv')
    phase=[r for r in contacts if r['contact_kind']=='phase_locked_min']
    assert len(contacts)==160 and len(phase)==80 and len(root)==58 and rep['genuine_11D_integrations']==88
    assert len(one)==rep['phase_locked_one_coordinate_roots']
    assert max(abs(float(r['Theta_delta_rad'])) for r in phase)<1e-9
    assert max(abs(float(r['energy_gap_ledger_residual'])) for r in contacts)<1e-8
    assert max(abs(float(r['chronological_angle_deg'])+float(r['phase_corresponding_angle_deg'])-180.) for r in contacts)<1e-8
    assert max(abs(float(r['shape_distance'])-float(r['shape_distance'])) for r in root)==0
    assert sum(int(r['phase_matched_within_1e_9']) for r in root)==rep['projected_crossings_clock_matched']
    coords={'logrho1':'shape_gap_logrho1','logrho2':'shape_gap_logrho2','x':'shape_gap_x'}
    for r in one:
        assert abs(float(r[coords[r['matched_coordinate']]]))<1e-9
        assert abs(float(r['Theta_delta_rad']))<1e-9
    for r in phase:
        assert abs(float(r['phase_locked_forward_progress_mismatch']))<1e-9
    for r in root:
        assert float(r['r_projected_root_residual'])<1e-8
    assert rep['max_historical_11D_replay_error']<1e-7
    assert rep['max_integrated_energy_balance_relative_error']<1e-8
    print('PASS: v18.48s CSV scientific gates on 88 integrations, 160 contacts, 58 projected roots,',len(one),'component roots')
if __name__=='__main__':main()
