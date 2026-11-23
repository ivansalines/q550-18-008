#!/usr/bin/env python3
"""Scientific gates for threshold and orientation analyses; no false cycle claims."""
import csv,math,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'results'
r=json.loads((R/'report.json').read_text())
assert r['version']=='v18.49f' and r['original_e_an_ancestry_verified_to_j']
for key,maximum in [('max_original_e_regression_error',1e-7),('max_original_11d_history_error',1e-7),
 ('max_energy_ledger_residual',1e-8),('max_clock_phase_mismatch_rad',1e-8),
 ('max_threshold_crossing_residual',1e-8),('max_coarse_fine_marker_difference_q',1e-7),
 ('max_orientation_quadrature_difference_deg',.02)]:
 assert r[key]<maximum,(key,r[key])
def read(file):
 with (R/file).open(newline='') as f:return list(csv.DictReader(f))
events=read('threshold_marker_events.csv');spans=read('threshold_passage_orientation.csv')
summary=read('threshold_contact_summary.csv');extrema=read('threshold_extrema.csv')
profiles=read('clock_registered_orientation_profiles.csv')
assert len(events)==r['count_oriented_crossings']==2*len(spans)
assert len(spans)==r['count_complete_passages']
assert len(extrema)==r['count_extrema']
assert len(profiles)==r['count_clock_registered_samples']
for row in events:
 assert row['orientation'] in ('entry','exit') and abs(float(row['residual']))<1e-8
for row in spans:
 assert row['true_material_cycle_proven']=='False'
 assert float(row['phase_span_q'])>0
 assert -1.00001<=float(row['entry_exit_cosine'])<=1.00001
 assert 0<=float(row['plane_leakage_max'])<1.00001
 assert float(row['path_total_turn_deg'])+1e-6>=float(row['entry_exit_angle_deg'])
counts=defaultdict(list)
for row in summary:counts[(row['kappa_kind'],row['ramp_xi'])].append((float(row['threshold']),int(row['connected_contact_components'])))
for arr in counts.values():
 arr=sorted(arr)
 assert all(b[1]<=a[1] for a,b in zip(arr[:-1],arr[1:])),('Nestedness of contact count violated',arr)
 assert len(arr)==7
if len(r['kappas'])==2:
 assert r['physical_integrations']==14 and r['frame_integrations']==12
 assert len(summary)==84 and len(profiles)==1212
 # Distinct E prediction: at 0.296333 original already merged, autonomous has 2 pieces.
 def get(kind):
  return next(int(x['connected_contact_components']) for x in summary if x['kappa_kind']==kind and x['ramp_xi']=='0.296333' and x['threshold']=='0.01')
 assert get('original')==1 and get('autonomous')==2
print('v18.49f PASS:',len(spans),'threshold passages;',len(events),'oriented markers;',len(profiles),'clock samples')
