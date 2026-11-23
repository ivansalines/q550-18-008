#!/usr/bin/env python3
import csv,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=json.loads((r/'results/report.json').read_text())
assert p['numeric_controls']['forward_regression']<1e-7
assert p['numeric_controls']['max_parent_cubic_difference']<2e-6
with (r/'results/case_surveys.csv').open() as f:rows=list(csv.DictReader(f))
with (r/'results/phase_pair67_profiles.csv').open() as f:phase=list(csv.DictReader(f))
assert len(rows)==p['number_of_evaluations']
assert len(phase)>=5*len({(x['kappa_kind'],x['ramp_xi'],x['shape']) for x in rows})
for row in rows:
 assert abs(float(row['margin_at_q065']))<=1.
 assert float(row['minimum_relative_eigen_gap'])>1e-7
for b in p['duration_brackets_refined']:
 if b['sign_change_confirmed']:assert b['margin_lower']*b['margin_upper']<0
print('PASS Q550 v18.49o count, historical regression, eigen-gap, bracket sanity')
