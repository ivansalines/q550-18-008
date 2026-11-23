#!/usr/bin/env python3
"""Fail closed on unverified replay, scalar-geometry and SHA ancestry gates."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'results'
def rd(name):
    with (RES/name).open() as f:return list(csv.DictReader(f))
report=json.loads((RES/'report.json').read_text())
assert report['status']=='FULL_FLOATING_POINT_11D_AUDIT',report['status']
assert report['historical_authentication']['recursive_ancestry_verified']
assert report['genuine_new_11D_integrations']==48
assert report['original_states_authenticated']==328
assert report['return_ramps_per_kappa']==23
assert len(rd('barrier_height_curvature.csv'))==46
assert len(rd('dense_contact_profiles.csv'))==46*1601
assert len(rd('threshold_persistence_components.csv'))==46*5
assert len(rd('critical_threshold_curve.csv'))==14
assert len(rd('barrier_ramp_sensitivity.csv'))==44
assert report['max_original_x_profile_reproduction_error']<1e-7
assert report['max_original_11D_replay_error']<1e-7
assert report['maximum_energy_ledger_relative_error']<1e-8
assert report['maximum_curvature_step_variation']<1e-4
for r in rd('barrier_height_curvature.csv'):
    assert -8<float(r['barrier_curvature_q2_richardson'])<-2
    assert float(r['barrier_full11d_distance'])>1
    assert -0.01<float(r['barrier_energy_difference'])<-0.002
    assert .46<float(r['barrier_phase_q'])<.51
for r in rd('threshold_persistence_components.csv'):
    assert int(r['components']) in (1,2)
    assert int(r['touches_left'])==0 and int(r['touches_right'])==0
for kind in ('original','autonomous'):
    rows=[r for r in rd('critical_threshold_curve.csv') if r['kappa_kind']==kind]
    rows.sort(key=lambda a:float(a['threshold']))
    assert all(float(a['secant_interpolated_ramp'])>float(b['secant_interpolated_ramp']) for a,b in zip(rows[:-1],rows[1:]))
    # Compare with separately executed original X critical barrier refinements.
    x=[r for r in rows if abs(float(r['threshold'])-.01)<1e-9][0]
    expect=.2963328 if kind=='original' else .29652905
    assert abs(float(x['secant_interpolated_ramp'])-expect)<1e-5
print('PASS v18.48y full Q550 numerical gates: 48 IVPs, 46 contact profiles, 14 threshold brackets, curvature and ledger.')
