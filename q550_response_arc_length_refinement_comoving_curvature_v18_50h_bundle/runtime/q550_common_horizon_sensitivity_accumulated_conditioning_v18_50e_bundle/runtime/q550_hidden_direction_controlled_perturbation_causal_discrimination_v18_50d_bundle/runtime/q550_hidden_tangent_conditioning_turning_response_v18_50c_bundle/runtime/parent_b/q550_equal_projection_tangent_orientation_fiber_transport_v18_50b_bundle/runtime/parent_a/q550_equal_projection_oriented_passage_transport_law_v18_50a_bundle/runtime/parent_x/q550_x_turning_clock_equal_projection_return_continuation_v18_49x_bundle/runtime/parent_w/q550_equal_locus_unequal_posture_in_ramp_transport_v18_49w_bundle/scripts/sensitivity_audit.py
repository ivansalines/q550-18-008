#!/usr/bin/env python3
"""Reclassify measured pairs under explicit diagnostic thresholds; no new solver run."""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/all_separated_pairs.csv').open() as fh: pairs=list(csv.DictReader(fh))
rows=[]
for sep in (.20,.25,.30):
 for tol in (.10,.20,.30,.40):
  v=[p for p in pairs if float(p['delta_sigma'])+1e-12>=sep and float(p['locus_xyz_scaled_gap'])<=tol]
  rows.append({'min_sigma_separation':sep,'3d_locus_normalized_threshold':tol,
       'accepted_pairs':len(v),'cases_with_pairs':len({(p['kappa_kind'],p['ramp_xi']) for p in v})})
with (ROOT/'results/threshold_sensitivity.csv').open('w',newline='') as fh:
 w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert next(x for x in rows if x['min_sigma_separation']==.20 and x['3d_locus_normalized_threshold']==.20)['accepted_pairs']==0
print('Wrote boundary-threshold sensitivity,',len(rows),'configurations')
