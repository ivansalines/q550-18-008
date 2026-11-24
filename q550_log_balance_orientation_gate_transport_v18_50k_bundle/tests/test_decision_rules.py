"""Decision-rule and source/metric invariance checks for shipped outputs."""
from __future__ import annotations
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def main():
    rows=list(csv.DictReader((R/'results/geometric_gate_events.csv').open()))
    data=json.loads((R/'results/report.json').read_text())
    assert len(rows)==30 and len([r for r in rows if r['internal_event']=='True'])==24
    assert data['input_rows']==4800
    for r in rows:
        if r['internal_event']!='True':
            assert r['metric']=='raw_coordinate'
            continue
        assert float(r['parity_xi'])<float(r['stationary_xi'])
        assert abs(float(r['parity_log_ratio']))<1e-10
        assert abs(float(r['imbalance_rate_parity']))<1e-8
        assert float(r['orientation_rate_parity'])>0
        assert float(r['orientation_rate_stationary'])>0
        assert float(r['imbalance_rate_stationary'])<0
        assert abs(float(r['log_gate_rate_stationary']))<1e-7
        assert float(r['resultant_rate_stationary'])>0
    print('v18.50k: 24 event-order and 6 raw-control tests PASS')
if __name__=='__main__':main()
