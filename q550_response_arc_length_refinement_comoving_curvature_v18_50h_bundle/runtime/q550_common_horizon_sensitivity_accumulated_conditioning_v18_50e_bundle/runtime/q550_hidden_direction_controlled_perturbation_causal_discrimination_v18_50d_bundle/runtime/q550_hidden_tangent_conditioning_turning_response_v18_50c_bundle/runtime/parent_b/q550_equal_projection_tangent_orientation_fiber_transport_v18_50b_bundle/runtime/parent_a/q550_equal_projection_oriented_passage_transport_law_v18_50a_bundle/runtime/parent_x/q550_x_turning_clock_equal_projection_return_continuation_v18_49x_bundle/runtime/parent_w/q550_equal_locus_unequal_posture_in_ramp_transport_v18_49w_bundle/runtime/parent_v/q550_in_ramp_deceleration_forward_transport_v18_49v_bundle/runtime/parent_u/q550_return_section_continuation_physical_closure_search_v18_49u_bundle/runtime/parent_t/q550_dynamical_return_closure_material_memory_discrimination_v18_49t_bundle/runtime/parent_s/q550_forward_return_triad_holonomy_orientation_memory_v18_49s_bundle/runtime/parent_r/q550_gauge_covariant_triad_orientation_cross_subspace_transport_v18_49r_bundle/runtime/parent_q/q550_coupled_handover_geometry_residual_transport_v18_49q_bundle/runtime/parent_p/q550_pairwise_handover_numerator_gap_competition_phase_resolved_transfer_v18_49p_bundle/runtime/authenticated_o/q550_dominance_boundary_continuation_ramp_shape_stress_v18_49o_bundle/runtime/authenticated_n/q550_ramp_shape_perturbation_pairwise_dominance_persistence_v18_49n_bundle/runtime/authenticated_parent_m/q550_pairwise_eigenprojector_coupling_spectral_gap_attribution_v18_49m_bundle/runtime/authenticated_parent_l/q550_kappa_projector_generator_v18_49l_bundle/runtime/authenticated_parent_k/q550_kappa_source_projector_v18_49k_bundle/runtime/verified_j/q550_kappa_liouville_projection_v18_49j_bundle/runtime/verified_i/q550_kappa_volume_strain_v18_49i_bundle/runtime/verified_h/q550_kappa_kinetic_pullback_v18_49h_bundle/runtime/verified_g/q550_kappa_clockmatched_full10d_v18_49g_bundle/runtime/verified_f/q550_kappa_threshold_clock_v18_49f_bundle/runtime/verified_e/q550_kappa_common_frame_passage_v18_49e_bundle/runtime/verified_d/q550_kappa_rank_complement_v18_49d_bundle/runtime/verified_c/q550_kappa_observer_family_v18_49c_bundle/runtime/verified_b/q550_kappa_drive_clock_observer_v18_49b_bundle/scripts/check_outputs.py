#!/usr/bin/env python3
"""Fail-closed scientific and archival output consistency gates for full run."""
from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def read(path):
 with (OUT/path).open(newline='') as f:return list(csv.DictReader(f))
def check():
 r=json.loads((OUT/'report.json').read_text());assert r['version']=='v18.49b'
 assert r['ancestry_verified_to_J'] and r['physical_11D_integrations']==14
 assert r['genuine_new_10D_cotangent_IVPs']==12
 points=read('observer_probe_at_physical_roots.csv');assert len(points)==288
 gauges=read('physical_clock_chart_recovery.csv');assert len(gauges)==240
 assert all(float(g['physical_cubic_recovery_abs_error'])<1e-10 for g in gauges)
 dual=read('transport_duality.csv');assert len(dual)==1128
 jac=read('analytic_jacobian_checks.csv');assert len(jac)==72
 barrier=[x for x in points if x['root_position']=='barrier']
 assert len(barrier)==96
 actual_distinct={(x['kappa_kind'],x['ramp_duration_xi']) for x in barrier}
 assert len(actual_distinct)==12
 assert all(abs(float(x['original_physical_clock_gap_rad']))<1e-10 for x in points)
 assert all(float(x['geometric_distance_3D'])>0 for x in points)
 assert all(float(x['historical_at_turn_fixed_probe'])*float(x['genuinely_transported_probe'])<0 for x in barrier)
 for name,limit in [('maximum_duality_relative_residual',1e-7),('maximum_11D_parent_replay_error',1e-7),('maximum_directional_Jacobian_FD_residual',1e-5),('maximum_original_root_distance_regression',2e-7),('maximum_diagonal_chart_pairing_residual',1e-10)]:
  val=float(r[name]);assert math.isfinite(val) and val<limit,(name,val)
 for x in points:
  assert abs(float(x['gauge_pairing_diagonal_residual']))<1e-10
 print('PASS: 12 physical return observer histories / 48 continuous root pairs / 2 observer channels / pairings & gauges')
if __name__=='__main__':check()
