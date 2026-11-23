#!/usr/bin/env python3
"""Regression tests of v18.50j audit's finite-window claims."""
from pathlib import Path
import csv,math
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/derivative_balance_events.csv').open() as f:rows=list(csv.DictReader(f))
assert len(rows)==30
for row in rows:
    metric=row['metric'];a=float(row['epsilon']);kind=row['kind']
    eq=float(row['norm_parity_xi']);peak=float(row['interpolated_stationary_xi'])
    if metric=='raw_coordinate':
        assert not math.isfinite(eq) and not math.isfinite(peak)
    else:
        assert math.isfinite(eq) and math.isfinite(peak) and eq<peak
        assert 0<peak<.004
        assert abs(float(row['total_derivative_at_stationary']))<1e-7
        assert float(row['resultant_norm_rate_at_stationary'])>0.
        assert float(row['balance_derivative_at_stationary'])<0.
        assert float(row['orientation_derivative_at_stationary'])>0.
for kind in ('original','autonomous'):
    byeps=[r for r in rows if r['kind']==kind and r['metric']=='common_parent_c']
    assert max(float(x['interpolated_stationary_xi']) for x in byeps)-min(float(x['interpolated_stationary_xi']) for x in byeps)<1e-9
    unit=[r for r in rows if r['kind']==kind and r['metric']=='common_uniform_rescale_3x']
    for a,b in zip(sorted(byeps,key=lambda x:float(x['epsilon'])),sorted(unit,key=lambda x:float(x['epsilon']))):
        assert abs(float(a['estimated_peak_c'])-float(b['estimated_peak_c']))<1e-7
print('v18.50j event and metric control tests PASS')
