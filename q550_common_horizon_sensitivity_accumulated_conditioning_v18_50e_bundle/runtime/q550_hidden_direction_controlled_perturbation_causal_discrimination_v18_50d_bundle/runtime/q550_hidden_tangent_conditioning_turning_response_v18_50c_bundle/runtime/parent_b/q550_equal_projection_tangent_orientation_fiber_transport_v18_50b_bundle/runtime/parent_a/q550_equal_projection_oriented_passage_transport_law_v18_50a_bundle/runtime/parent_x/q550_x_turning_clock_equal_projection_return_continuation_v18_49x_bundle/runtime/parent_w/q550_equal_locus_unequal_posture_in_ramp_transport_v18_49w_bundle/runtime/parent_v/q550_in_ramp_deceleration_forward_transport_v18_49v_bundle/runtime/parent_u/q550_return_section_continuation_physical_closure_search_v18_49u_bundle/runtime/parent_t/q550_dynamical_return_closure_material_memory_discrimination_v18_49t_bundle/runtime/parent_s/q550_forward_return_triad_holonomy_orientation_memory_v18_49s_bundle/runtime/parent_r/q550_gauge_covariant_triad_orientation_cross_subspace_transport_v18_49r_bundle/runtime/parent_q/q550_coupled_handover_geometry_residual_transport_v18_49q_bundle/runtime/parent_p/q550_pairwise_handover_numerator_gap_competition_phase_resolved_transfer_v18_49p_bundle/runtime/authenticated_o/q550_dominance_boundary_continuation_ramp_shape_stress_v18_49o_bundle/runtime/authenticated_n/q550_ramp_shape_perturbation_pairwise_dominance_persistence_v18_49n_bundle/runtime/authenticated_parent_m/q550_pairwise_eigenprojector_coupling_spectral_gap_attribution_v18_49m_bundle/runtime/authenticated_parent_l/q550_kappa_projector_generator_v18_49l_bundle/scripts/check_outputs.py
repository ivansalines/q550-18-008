"""Numerical decision gates for authenticated Q550 v18.49l audit."""
import json,csv
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'results'
r=json.loads((p/'report.json').read_text())
assert r['version']=='v18.49l' and r['upstream']['ancestry_to_v18_48j']
assert r['physical_integrations']==14 and r['tangent_frame_integrations']==12
assert len(r['case_summary'])==12
assert r['minimum_relative_eigen_gap']>.002
E=r['test_max_errors']
for label,tol in {'forward_regression':1e-7,'log_volume_vs_parent':1e-7,
 'generator_vs_fd_projector':.03,'generator_vs_parent_speed':.03,
 'occupation_vs_parent':1e-6,'projector_closure':1e-10,
 'strain_logvolume_identity':1e-9,'c_rate_vs_finite_difference':.03,
 'sigma_rate_vs_finite_difference':.03,'source_vs_material_volume_rate':1e-6,
 'projector_rate_vs_fd':.03,'fixed_orthogonal_gauge':1e-8}.items():
 assert E[label]<tol,(label,E[label],tol)
for name,minlines in [('covariant_generator_phase_profiles.csv',1450),('principal_strain_projector_phase_profiles.csv',5800),('ramp_kappa_summary.csv',12)]:
 with (p/name).open() as f:assert sum(1 for _ in csv.DictReader(f))>=minlines
print('v18.49l AUTHENTIC_Q550_PROJECTOR_GENERATOR_ACCEPTANCE_PASSED')
