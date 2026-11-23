"""Scientific gates and explicit interpretation checks for v18.49e."""
from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parents[1]/'results'
r=json.loads((R/'report.json').read_text())
assert r['version']=='v18.49e' and r['historical_source_authenticated_to_J']
expected=2 if len(r['kappas_tested'])==1 else 14
assert r['physical_integrations']==expected
assert r['adjoint_integrations']==r['frame_integrations']==r['physical_integrations']-len(r['kappas_tested'])
for key,cap in [('max_forward_history_error',1e-7),('max_parent_d_regression',1e-7),
  ('max_energy_ledger_residual',1e-8),('max_clock_mismatch_rad',1e-8),
  ('max_cotangent_frame_identity_residual',1e-7),('max_finite_pairing_pullback_error',1e-7),
  ('max_metric_decomposition_error',1e-8),('max_chart_covariance_error',1e-8)]:
 assert r[key]<cap,(key,r[key])
def read(name):
 with (R/name).open(newline='') as f:return list(csv.DictReader(f))
points=read('common_frame_profiles.csv');scales=read('kappa0_marker_scale_tests.csv');events=read('oriented_passage_events.csv');pairs=read('subthreshold_passage_pairs.csv')
assert len(points)==r['count_finite_material_profiles']
assert len(events)==r['count_oriented_threshold_markers']
assert len(scales)==r['count_kappa0_interval_probes']
if pairs[0].get('status')!='no_event':assert len(pairs)==r['count_completed_subthreshold_intervals']
for a in points:
 assert 0<=float(a['common_fraction'])<=1+1e-10
 assert 0<=float(a['instantaneous_fraction'])<=1+1e-10
 assert abs(float(a['common_total'])**2-float(a['common_hidden'])**2-float(a['common_observed'])**2)<1e-8
 assert float(a['frame_condition_number'])<1e5
for a in events:
 assert a['orientation'] in ('entry','exit') and abs(float(a['residual']))<1e-8
for a in scales:
 assert a['true_physical_cycle_proven'] in ('False','0')
 assert math.isfinite(float(a['hidden_cosine_common_frame']))
print(f'v18.49e scientific checks PASS: {len(points)} common-frame profiles, '
      f'{len(events)} oriented markers, {len(scales)} kappa/0.2 probes')
