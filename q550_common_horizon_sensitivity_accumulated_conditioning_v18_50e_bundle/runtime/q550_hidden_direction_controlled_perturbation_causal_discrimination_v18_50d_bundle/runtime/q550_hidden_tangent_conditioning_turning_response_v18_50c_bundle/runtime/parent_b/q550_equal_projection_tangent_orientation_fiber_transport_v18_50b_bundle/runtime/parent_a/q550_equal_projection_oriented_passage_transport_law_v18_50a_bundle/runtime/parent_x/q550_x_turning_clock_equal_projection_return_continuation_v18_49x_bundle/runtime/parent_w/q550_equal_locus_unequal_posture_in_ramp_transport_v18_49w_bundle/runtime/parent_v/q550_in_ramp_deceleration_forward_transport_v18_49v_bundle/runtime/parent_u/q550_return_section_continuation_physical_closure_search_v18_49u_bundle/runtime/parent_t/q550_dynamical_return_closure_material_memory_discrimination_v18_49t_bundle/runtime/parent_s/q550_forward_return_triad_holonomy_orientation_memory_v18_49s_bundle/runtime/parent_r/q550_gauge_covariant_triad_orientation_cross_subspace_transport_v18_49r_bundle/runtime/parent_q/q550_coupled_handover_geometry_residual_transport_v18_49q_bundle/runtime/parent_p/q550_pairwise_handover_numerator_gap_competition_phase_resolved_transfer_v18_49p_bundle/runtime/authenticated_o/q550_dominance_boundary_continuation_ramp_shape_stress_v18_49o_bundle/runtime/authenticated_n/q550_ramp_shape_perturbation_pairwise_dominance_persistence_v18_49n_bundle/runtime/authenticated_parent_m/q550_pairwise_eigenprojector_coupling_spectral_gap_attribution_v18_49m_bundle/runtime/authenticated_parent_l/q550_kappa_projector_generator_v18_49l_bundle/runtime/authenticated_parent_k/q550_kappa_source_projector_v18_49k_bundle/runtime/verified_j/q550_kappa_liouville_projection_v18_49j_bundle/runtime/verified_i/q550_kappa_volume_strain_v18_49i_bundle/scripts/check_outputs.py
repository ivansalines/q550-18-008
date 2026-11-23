#!/usr/bin/env python3
"""Scientific consistency checks of the generated numeric data."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
assert r['history_authenticated_to_J']
assert r['physical_integrations']==14 and r['frame_integrations']==12
for key,lim in [('max_liouville_log_volume_residual',1e-7),('max_tau_volume_log_spread',1e-8),('max_chart_metric_volume_residual',1e-8),('max_nonlinear_chart_strain_error',1e-8),('max_H_strain_regression',1e-7),('max_history_error',1e-7)]:
 assert math.isfinite(r[key]) and r[key]<lim,(key,r[key])
for f,n in [('strain_axes_phase_profiles.csv',84),('all_ten_principal_stretches.csv',840),('liouville_volume_identity.csv',12),('strain_axis_vs_material_curvature.csv',36)]:
 with (ROOT/'results'/f).open() as fd:actual=len(list(csv.DictReader(fd)))
 assert actual==n,(f,actual,n)
print('SCIENTIFIC_GATES_PASS',json.dumps({k:r[k] for k in ('max_liouville_log_volume_residual','max_H_strain_regression','max_tau_volume_log_spread')},indent=2))
