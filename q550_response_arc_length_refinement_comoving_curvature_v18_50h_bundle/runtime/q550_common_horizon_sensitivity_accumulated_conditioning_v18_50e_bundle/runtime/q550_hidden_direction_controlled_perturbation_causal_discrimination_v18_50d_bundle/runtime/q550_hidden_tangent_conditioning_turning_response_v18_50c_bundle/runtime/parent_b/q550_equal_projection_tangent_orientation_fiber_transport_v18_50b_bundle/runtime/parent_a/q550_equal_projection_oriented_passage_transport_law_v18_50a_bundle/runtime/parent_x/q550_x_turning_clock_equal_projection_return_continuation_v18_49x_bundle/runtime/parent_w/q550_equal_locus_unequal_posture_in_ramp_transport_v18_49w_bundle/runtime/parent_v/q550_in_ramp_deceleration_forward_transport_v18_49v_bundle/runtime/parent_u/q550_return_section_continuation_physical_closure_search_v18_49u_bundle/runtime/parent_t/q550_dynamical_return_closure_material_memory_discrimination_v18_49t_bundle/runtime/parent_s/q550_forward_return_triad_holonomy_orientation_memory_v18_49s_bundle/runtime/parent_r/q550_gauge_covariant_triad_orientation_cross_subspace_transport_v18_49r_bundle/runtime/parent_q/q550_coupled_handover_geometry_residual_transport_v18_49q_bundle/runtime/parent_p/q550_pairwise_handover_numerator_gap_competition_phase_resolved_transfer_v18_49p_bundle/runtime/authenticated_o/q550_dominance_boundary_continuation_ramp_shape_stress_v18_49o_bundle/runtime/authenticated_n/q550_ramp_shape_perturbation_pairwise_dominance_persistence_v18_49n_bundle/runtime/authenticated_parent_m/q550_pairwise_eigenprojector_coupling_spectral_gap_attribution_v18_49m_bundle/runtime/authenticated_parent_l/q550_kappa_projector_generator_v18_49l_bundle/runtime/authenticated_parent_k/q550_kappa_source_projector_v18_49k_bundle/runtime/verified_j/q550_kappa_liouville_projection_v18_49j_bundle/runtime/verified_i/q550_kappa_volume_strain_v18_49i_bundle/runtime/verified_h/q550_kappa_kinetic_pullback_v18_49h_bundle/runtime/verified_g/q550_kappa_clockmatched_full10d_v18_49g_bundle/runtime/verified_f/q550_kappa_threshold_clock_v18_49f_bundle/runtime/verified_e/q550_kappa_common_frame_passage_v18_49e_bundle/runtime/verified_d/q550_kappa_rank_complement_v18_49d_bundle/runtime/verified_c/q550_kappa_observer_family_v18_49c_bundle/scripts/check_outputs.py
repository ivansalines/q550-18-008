#!/usr/bin/env python3
"""Check scientific boundary conditions and parent regression before packaging."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
with (ROOT/'results/observer_family_envelopes.csv').open(newline='') as f:rows=list(csv.DictReader(f))
assert r['status']=='AUTHENTIC_11D_REPLAY_AND_TRANSPORTED_FINITE_COVECTOR_FAMILY'
assert r['physical_11D_integrations']==14 and r['new_10D_five_covector_transport_IVPs']==12
assert len(rows)==576
assert r['genealogy']['nested_original_genealogy_authenticated_to_J']
for key,lim in [('max_relative_chart_covariance_residual',1e-7),('max_relative_basis_mixing_residual',1e-7),
 ('max_parent_B_probe_regression',1e-7),('max_tangent_cotangent_duality_residual',1e-7),
 ('max_11D_historical_forward_regression',1e-7),('max_observer_readout_envelope_violation',1e-7)]:
 assert r[key]<lim,(key,r[key])
# Same physical root, same metric: larger family never reduces envelope.
by={}
for row in rows:
 key=(row['kappa_kind'],row['ramp_xi'],row['delta_B_minus_threshold'],row['root_position'],row['metric'])
 by.setdefault(key,{})[int(row['family_size'])]=float(row['envelope_abs_max'])
assert all(2 in group and 5 in group and group[5]>=group[2]-1e-9 for group in by.values())
print('v18.49c scientific gates PASS; 144 root/barrier events x 2 families x 2 metrics')
