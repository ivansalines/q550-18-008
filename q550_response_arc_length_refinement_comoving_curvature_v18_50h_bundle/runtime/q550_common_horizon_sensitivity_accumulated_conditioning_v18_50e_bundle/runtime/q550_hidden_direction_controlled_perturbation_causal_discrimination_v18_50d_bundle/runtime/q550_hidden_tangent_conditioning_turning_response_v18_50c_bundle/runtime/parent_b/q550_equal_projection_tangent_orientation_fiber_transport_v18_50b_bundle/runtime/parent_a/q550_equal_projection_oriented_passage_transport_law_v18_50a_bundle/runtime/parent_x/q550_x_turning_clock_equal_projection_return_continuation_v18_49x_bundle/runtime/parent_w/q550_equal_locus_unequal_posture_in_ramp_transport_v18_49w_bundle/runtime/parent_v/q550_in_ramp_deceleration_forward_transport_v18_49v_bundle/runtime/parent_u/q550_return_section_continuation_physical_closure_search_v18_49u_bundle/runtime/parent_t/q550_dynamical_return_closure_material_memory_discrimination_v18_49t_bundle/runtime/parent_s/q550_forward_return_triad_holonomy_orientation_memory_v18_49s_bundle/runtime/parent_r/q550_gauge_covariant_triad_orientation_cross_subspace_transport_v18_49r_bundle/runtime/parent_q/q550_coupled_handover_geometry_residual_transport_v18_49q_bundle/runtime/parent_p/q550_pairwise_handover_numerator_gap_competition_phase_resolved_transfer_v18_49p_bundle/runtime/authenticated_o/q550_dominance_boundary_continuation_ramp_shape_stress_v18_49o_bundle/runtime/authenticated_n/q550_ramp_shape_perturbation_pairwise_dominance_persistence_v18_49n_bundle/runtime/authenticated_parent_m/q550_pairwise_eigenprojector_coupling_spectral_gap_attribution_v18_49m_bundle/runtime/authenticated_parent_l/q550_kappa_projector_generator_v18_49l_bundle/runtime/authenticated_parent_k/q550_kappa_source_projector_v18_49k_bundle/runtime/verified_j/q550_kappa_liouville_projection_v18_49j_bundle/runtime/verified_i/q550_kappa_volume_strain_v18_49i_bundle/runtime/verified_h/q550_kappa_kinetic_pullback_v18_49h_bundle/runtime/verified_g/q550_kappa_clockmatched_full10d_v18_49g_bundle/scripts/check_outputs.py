#!/usr/bin/env python3
"""Independent scientific gates on saved numerical results and F ancestry."""
import csv,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def csvrows(name):
 with (ROOT/'results'/name).open(newline='') as f:return list(csv.DictReader(f))
def check():
 r=json.loads((ROOT/'results/report.json').read_text())
 f=csvrows('threshold_free_extrema_orientation.csv')
 p=csvrows('clock_matched_threshold_passages.csv')
 t=csvrows('full10d_clock_profiles.csv')
 smoke=(r['kappa_set']==['original'] and r['ramp_set']==[.3])
 assert len(f)==(1 if smoke else 12)
 assert len(p)==r['number_threshold_passages']
 assert len(t)==r['clock_grid_samples']
 assert len(p)==(9 if smoke else 121)
 assert all(float(row['full10d_extrema_path_turn_deg'])+1e-7>=float(row['full10d_extrema_endpoint_angle_deg']) for row in f)
 assert all(float(row['full10d_path_turn_deg'])+1e-7>=float(row['full10d_endpoint_angle_deg']) for row in p)
 assert all(row['observational_cycle_proven']=='False' for row in p)
 assert all(row['full10d_angle_max_at_window_boundary']=='True' for row in f)
 assert r['max_parent_extrema_shape_error']<1e-7
 assert r['max_full10d_chart_covariance_error_deg']<2e-5
 assert r['max_full10d_arc_49_vs_97_refinement_deg']<.02
 assert r['max_tangent_cotangent_duality_residual']<1e-8
 assert r['nested_ancestry_authenticated_to_J'] is True
 if not smoke:
  assert r['count_passages_within_1_percent_of_6_over_5']==2
  assert r['threshold_free_extrema_ratio_max']<1.0
 print('v18.49g checks PASS',len(f),'extrema /',len(p),'passages /',len(t),'clock samples')
if __name__=='__main__':check()
