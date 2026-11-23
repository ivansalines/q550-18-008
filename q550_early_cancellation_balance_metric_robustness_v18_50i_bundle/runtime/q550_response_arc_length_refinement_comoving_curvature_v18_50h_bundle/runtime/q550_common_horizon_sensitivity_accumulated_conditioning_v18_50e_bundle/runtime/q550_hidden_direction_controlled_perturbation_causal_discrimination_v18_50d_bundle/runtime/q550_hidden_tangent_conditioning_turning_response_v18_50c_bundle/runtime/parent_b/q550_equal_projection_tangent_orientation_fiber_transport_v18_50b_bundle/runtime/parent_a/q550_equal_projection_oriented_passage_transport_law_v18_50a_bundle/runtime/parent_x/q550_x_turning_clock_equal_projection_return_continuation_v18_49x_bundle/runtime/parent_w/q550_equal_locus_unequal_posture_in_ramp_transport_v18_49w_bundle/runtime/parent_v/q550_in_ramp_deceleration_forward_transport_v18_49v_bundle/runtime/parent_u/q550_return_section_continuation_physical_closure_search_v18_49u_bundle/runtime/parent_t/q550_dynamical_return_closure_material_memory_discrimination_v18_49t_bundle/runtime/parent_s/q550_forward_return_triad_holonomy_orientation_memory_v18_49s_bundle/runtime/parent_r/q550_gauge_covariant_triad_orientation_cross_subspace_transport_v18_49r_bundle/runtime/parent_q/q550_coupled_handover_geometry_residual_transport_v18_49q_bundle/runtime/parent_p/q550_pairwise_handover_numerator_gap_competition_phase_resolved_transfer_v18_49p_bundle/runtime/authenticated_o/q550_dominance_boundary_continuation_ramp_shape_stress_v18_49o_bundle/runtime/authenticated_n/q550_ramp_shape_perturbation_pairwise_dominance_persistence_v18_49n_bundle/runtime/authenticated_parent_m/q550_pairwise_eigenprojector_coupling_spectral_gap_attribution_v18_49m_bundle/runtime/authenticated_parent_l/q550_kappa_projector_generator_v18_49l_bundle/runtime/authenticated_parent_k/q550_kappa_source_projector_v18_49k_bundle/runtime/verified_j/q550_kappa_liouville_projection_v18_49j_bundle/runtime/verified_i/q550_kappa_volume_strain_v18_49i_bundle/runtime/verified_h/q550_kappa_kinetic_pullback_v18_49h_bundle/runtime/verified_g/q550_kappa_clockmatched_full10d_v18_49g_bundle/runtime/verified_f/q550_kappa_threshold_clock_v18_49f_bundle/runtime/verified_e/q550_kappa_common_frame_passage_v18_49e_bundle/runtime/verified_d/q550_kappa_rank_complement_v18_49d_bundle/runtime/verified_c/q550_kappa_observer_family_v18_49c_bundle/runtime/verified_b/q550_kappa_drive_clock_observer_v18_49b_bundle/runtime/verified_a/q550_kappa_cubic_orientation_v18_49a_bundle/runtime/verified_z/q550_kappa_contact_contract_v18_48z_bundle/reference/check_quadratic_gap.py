#!/usr/bin/env python3
"""Independent check of the near-saddle square-root split of two lobes.

From the observed local maximum B with negative curvature C, the near-critical
excluded gap around that maximum is 2*sqrt(2*(B-epsilon)/abs(C)) + higher-order
terms. The check uses ACTUAL dense-IVP threshold roots in the CSV, not image
pixels or a new claimed constitutive physical law.
"""
from __future__ import annotations
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def read(name):
    with (R/name).open(newline='') as f:return list(csv.DictReader(f))
B={(r['kappa_kind'],r['ramp_duration_xi']):r for r in read('barrier_height_curvature.csv')}
rows=[]
for contact in read('threshold_persistence_components.csv'):
    if int(contact['components'])!=2:continue
    bar=B[(contact['kappa_kind'],contact['ramp_duration_xi'])]
    threshold=float(contact['threshold_d3']);height=float(bar['barrier_distance_3D'])
    surplus=height-threshold
    if not 0<surplus<.0004:continue
    intervals=json.loads(contact['lobe_intervals_json'])
    if len(intervals)!=2:continue
    observed=float(intervals[1][0]-intervals[0][1])
    curvature=float(bar['barrier_curvature_q2_richardson'])
    estimated=2*math.sqrt(2*surplus/abs(curvature))
    relative=abs(estimated-observed)/observed
    rows.append({'kappa_kind':contact['kappa_kind'],
                 'ramp_duration_xi':contact['ramp_duration_xi'],
                 'threshold_d3':threshold,'barrier_minus_threshold':surplus,
                 'barrier_curvature':curvature,'observed_between_lobes_gap_q':observed,
                 'quadratic_predicted_gap_q':estimated,'absolute_relative_error':relative})
assert len(rows)>=10,len(rows)
maxrel=max(r['absolute_relative_error'] for r in rows)
assert maxrel<0.001,maxrel
path=R/'quadratic_gap_scaling_check.csv'
with path.open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
(R/'quadratic_gap_scaling_report.json').write_text(json.dumps({
    'near_threshold_pairs':len(rows),'maximum_relative_prediction_error':maxrel,
    'claim':'Second-order Taylor approximation of projected gap near local barrier maximum; not physical material recurrence or certified scaling theorem.'},indent=2)+'\n')
print(f'PASS projected lobe-gap quadratic check: {len(rows)} pairs, max relative deviation {maxrel:.7%}')
