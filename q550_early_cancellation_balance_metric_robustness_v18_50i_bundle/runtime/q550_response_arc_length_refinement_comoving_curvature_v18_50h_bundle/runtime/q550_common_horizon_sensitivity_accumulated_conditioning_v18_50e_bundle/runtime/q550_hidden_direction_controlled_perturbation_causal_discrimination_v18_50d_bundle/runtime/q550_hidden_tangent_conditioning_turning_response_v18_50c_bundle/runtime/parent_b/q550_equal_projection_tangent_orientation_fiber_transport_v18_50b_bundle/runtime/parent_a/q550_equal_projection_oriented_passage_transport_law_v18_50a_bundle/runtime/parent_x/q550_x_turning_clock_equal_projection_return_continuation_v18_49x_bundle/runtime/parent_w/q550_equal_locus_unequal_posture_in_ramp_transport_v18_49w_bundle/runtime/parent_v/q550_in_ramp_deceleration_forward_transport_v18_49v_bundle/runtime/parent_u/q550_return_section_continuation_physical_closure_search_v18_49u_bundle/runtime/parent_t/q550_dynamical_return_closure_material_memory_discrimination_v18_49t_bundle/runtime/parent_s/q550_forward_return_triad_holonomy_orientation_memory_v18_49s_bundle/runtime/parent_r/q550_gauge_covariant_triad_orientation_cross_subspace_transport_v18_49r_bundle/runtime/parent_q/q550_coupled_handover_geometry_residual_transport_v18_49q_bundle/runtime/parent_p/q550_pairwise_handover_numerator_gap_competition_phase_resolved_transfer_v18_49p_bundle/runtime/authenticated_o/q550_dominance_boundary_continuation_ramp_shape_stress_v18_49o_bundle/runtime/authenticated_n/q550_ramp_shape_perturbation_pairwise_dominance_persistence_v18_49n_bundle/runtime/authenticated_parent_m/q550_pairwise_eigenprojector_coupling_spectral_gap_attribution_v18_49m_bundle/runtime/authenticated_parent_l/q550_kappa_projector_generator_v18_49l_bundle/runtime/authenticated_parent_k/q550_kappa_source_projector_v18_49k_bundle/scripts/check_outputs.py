#!/usr/bin/env python3
"""Quantitative acceptance criteria for complete server output."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];res=ROOT/'results'
r=json.loads((res/'report.json').read_text())
assert r['version']=='v18.49k' and r['authentic_ancestry_to_v18_48j']
assert r['physical_integrations']==14 and r['tangent_frame_integrations']==12
assert len(r['alpha_zero_source_roots'])==6
err=r['max_regression_or_identity_errors']
assert err['historical_forward']<1e-7
assert err['parent_source']<1e-7 and err['parent_occupation']<1e-7
assert err['projector_sum']<1e-9 and err['source_identity']<1e-11
assert err['explicit_kappa_trace']<1e-12 and err['occupation_derivative_balance']<.02
assert err['projector_halfturn_coarse_grid_difference_q']<.002
with (res/'source_zero_counterfactual_roots.csv').open(newline='') as f:zz=list(csv.DictReader(f))
for rv in r['ramp_set']:
    root0=next(x for x in zz if float(x['ramp_xi'])==rv and float(x['alpha'])==0.)
    rootneg=next(x for x in zz if float(x['ramp_xi'])==rv and float(x['alpha'])==-.001)
    rootpos=next(x for x in zz if float(x['ramp_xi'])==rv and float(x['alpha'])==.001)
    assert int(root0['root_count'])==1 and int(rootneg['root_count'])==1
    assert abs(float(rootneg['clock_source_zero_q'])-float(root0['clock_source_zero_q']))>.02
    assert int(rootpos['root_count'])==0
with (res/'principal_projector_halfturn_markers.csv').open(newline='') as f:markers=list(csv.DictReader(f))
assert len(markers)==60 and all(.35<float(x['half_turn_clock_q'])<.65 for x in markers)
print('v18.49k ACCEPTANCE_GATE_PASSED; 14 original 11D paths, 12 tangent frames, 6 source zeros, gauge-free rank-one projectors.')
