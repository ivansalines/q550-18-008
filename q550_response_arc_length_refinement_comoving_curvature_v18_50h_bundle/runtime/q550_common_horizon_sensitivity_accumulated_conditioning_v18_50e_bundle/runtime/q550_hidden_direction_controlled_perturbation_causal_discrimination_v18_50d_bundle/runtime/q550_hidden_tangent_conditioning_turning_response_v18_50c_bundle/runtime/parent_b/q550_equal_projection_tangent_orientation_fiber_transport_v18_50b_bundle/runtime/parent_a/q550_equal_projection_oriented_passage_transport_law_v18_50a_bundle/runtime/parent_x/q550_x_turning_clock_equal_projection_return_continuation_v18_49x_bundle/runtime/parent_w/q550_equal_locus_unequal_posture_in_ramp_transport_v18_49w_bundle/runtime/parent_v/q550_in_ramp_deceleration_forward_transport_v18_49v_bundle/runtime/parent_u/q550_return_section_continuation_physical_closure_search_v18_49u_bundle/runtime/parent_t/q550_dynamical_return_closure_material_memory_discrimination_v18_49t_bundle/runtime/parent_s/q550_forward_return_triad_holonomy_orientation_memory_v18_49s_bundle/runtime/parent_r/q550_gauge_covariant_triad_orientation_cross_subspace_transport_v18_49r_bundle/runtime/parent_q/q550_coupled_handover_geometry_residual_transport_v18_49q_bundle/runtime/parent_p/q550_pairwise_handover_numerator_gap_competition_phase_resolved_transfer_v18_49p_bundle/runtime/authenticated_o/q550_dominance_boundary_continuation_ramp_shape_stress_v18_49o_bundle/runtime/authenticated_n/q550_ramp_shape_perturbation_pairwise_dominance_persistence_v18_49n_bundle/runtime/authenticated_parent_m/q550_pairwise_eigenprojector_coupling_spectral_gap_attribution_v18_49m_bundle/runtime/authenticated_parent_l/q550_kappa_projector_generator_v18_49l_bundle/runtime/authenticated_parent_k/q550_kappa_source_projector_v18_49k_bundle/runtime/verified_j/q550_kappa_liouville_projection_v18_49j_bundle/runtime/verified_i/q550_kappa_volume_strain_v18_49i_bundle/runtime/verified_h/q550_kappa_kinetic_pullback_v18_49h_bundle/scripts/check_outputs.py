#!/usr/bin/env python3
"""Check scientific gates of the actual completed v18.49h report and datasets."""
import json,csv,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
if r['physical_integrations']!=14 or r['frame_integrations']!=12:raise AssertionError('Incomplete genuine Q550 full audit')
assert r['history_authenticated_to_J']
for key,limit in [('max_original_history_error',1e-7),('max_kinetic_energy_identity_error',1e-10),
                  ('max_clock_mismatch_rad',1e-8),('max_nonlinear_chart_generalized_eigen_error',1e-8),
                  ('max_curvature_arc_refinement_deg',.03)]:
 if not math.isfinite(r[key]) or r[key]>limit:raise AssertionError(f'Failed {key}')
counts={'kinetic_deformation_eigenvalues.csv':108,'kinetic_sphere_curvature.csv':36,
        'kinetic_orientation_profiles.csv':12*(2*121-1), 'metric_comparison_with_G.csv':12}
for name,n in counts.items():
 with (ROOT/'results'/name).open() as f:rows=list(csv.DictReader(f))
 if len(rows)!=n:raise AssertionError(f'{name}: {len(rows)} != {n}')
print('SCIENTIFIC_CHECKS_PASS',json.dumps({k:r[k] for k in ('max_original_history_error','max_kinetic_energy_identity_error','max_nonlinear_chart_generalized_eigen_error','max_curvature_arc_refinement_deg')},indent=2))
