"""Fail closed on missing results and violated scientific gates."""
from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[1]/'results'
r=json.loads((R/'report.json').read_text())
assert r['version']=='v18.49d'
assert r['genealogy']['nested_original_genealogy_authenticated_to_J']
assert r['physical_integrations'] in (2,14) and r['cotangent_integrations'] in (1,12)
for key,lim in [('max_parent_C_regression',1e-7),('max_forward_history_regression',1e-7),
('max_energy_ledger_residual',1e-8),('max_metric_chart_covariance_error',1e-7),
('max_metric_pythagorean_error',1e-8),('max_tangent_cotangent_duality_residual',1e-7)]:
 assert r[key]<lim,(key,r[key])
with (R/'rank_and_hidden_complement.csv').open() as f:rows=list(csv.DictReader(f))
assert len(rows)==r['data_rows']
# Nested observer sets cannot lose observable amplitude at fixed threshold (though ranks can change).
by={}
for a in rows:
 k=(a['kappa_kind'],a['ramp_xi'],a['phase_q'],a['metric'],a['rank_tolerance'])
 by.setdefault(k,{})[int(a['family_size'])]=float(a['observable_envelope'])
violations=[]
for k,family in by.items():
 if 2 in family and 5 in family and family[5]<family[2]-1e-8:violations.append(k)
assert not violations,violations[:4]
print('v18.49d checks PASS:',len(rows),'rank/family/phase records')
