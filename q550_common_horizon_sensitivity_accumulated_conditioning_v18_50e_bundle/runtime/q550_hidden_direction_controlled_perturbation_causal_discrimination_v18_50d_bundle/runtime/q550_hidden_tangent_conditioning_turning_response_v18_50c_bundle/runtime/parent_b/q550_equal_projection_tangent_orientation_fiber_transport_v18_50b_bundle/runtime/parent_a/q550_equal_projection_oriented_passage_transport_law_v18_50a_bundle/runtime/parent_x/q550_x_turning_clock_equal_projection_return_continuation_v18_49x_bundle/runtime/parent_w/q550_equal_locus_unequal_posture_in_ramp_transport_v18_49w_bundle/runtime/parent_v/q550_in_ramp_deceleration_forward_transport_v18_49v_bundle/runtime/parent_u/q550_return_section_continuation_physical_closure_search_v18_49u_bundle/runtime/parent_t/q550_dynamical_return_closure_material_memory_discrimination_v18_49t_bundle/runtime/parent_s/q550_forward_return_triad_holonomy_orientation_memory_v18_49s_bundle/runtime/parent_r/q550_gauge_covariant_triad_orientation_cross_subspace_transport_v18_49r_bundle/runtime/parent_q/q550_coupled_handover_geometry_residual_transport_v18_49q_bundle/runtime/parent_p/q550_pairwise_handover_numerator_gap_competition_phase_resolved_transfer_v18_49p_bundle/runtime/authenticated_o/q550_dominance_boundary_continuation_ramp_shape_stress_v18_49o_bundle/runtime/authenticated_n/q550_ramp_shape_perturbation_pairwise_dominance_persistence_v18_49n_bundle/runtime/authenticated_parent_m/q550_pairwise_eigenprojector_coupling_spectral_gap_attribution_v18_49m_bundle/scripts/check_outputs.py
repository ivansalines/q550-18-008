"""Independent acceptance gates for genuine Q550 v18.49m replay."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'results'
r=json.loads((P/'report.json').read_text())
assert r['version']=='v18.49m' and r['upstream']['parent_version']=='v18.49l'
assert r['upstream']['ancestry_to_v18_48j']
assert r['physical_integrations']==14 and r['tangent_frame_integrations']==12
assert r['pair_count']==45 and len(r['pairwise_case_summary'])==12
assert r['minimum_relative_eigen_gap']>.002
E=r['test_max_errors']
gates={'forward_regression':1e-7,'log_volume_vs_parent':1e-7,
 'generator_vs_fd_projector':.03,'generator_vs_parent_speed':.03,
 'occupation_vs_parent':1e-6,'projector_closure':1e-10,
 'strain_logvolume_identity':1e-9,'c_rate_vs_finite_difference':.03,
 'sigma_rate_vs_finite_difference':.03,'source_vs_material_volume_rate':1e-6,
 'projector_rate_vs_fd':.03,'fixed_orthogonal_gauge':1e-8,
 'pair_frobenius_identity':1e-10,'pair_shapley_closure':1e-10,
 'pair_sign_independence':1e-12,'pair_orthogonal_gauge':1e-9}
for key,limit in gates.items():assert E[key]<limit,(key,E[key],limit)
for name,length in [('covariant_generator_phase_profiles.csv',1452),
 ('principal_strain_projector_phase_profiles.csv',5808),
 ('ramp_kappa_summary.csv',12),('pairwise_generator_phase_profiles.csv',65340),
 ('pairwise_shapley_comparison.csv',540),('pairwise_case_summary.csv',12)]:
 with (P/name).open(newline='') as f:assert len(list(csv.DictReader(f)))==length,name
print('v18.49m AUTHENTIC_Q550_PAIRWISE_GENERATOR_AUDIT_ACCEPTED')
