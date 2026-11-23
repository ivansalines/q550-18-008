#!/usr/bin/env python3
"""Validate real full-scan products before packaging."""
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'results'
report=json.loads((p/'report.json').read_text())
assert report['version']=='v18.49j' and report['parent_i_authenticated_to_J']
assert report['physical_integrations']==14 and report['frame_integrations']==12,'smoke run is NOT complete'
expected={'liouville_source_integrals.csv':12,'clockmatched_kappa_cancellation.csv':6,
 'instantaneous_volume_sources.csv':732,'ten_axis_occupation_and_split.csv':7320,
 'counterfactual_volume_forms.csv':60}
for name,n in expected.items():
 with (p/name).open(newline='') as fi:
  rows=list(csv.DictReader(fi))
 assert len(rows)==n,(name,len(rows),n)
 for r in rows:
  for v in r.values():
   if v is None:raise RuntimeError('Truncated CSV column: '+name)
assert report['source_max_errors']['liouville']<1e-7
assert report['source_max_errors']['parent_logvolume']<1e-7
assert report['source_max_errors']['occupation_balance']<.01
print('v18.49j checks passed: 14 physical, 12 tangent, all row counts and scientific gates')
