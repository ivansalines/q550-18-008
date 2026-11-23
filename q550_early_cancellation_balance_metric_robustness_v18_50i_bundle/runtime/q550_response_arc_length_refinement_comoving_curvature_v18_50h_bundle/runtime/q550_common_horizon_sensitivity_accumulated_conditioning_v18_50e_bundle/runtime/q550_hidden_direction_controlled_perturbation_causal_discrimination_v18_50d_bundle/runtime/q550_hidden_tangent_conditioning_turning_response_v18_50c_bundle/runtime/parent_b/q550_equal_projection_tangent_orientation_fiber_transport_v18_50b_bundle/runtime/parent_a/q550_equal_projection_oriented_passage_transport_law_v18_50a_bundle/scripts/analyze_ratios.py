#!/usr/bin/env python3
"""Postprocess candidate two-channel co-transport without claiming a physical law."""
import json,csv
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]/'results'
with (R/'oriented_equal_projection_passages.csv').open() as f:d=list(csv.DictReader(f))
if not d:raise RuntimeError('No passage data')
a1=np.asarray([float(z['signed_area_x_theta1']) for z in d]);a2=np.asarray([float(z['signed_area_x_theta2']) for z in d]);
t1=np.asarray([float(z['theta1_transport_rad']) for z in d]);t2=np.asarray([float(z['theta2_transport_rad']) for z in d]);
if np.any(abs(a1)<1e-13):raise RuntimeError('Unresolved area ratio')
r=a2/a1;tr=t2/t1
out={'count':len(d),'area_ratio_theta2_over_theta1':{'minimum':float(np.min(r)),'maximum':float(np.max(r)),'mean':float(np.mean(r)),'standard_deviation':float(np.std(r,ddof=1))},
'angular_transport_ratio_theta2_over_theta1':{'minimum':float(np.min(tr)),'maximum':float(np.max(tr)),'mean':float(np.mean(tr))},
'area_signs':{'theta1':sorted(set(np.sign(a1).tolist())),'theta2':sorted(set(np.sign(a2).tolist()))},
'status':'DESCRIPTIVE_COTRANSPORT_RATIO_NOT_AN_INDEPENDENT_DYNAMICAL_LAW',
'limitations':'Pairs on the same trajectory are correlated; ratio may be inherited from underlying angular RHS or kinematic convention.'}
(R/'co_transport_ratio_diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
print('AREA_RATIO',out['area_ratio_theta2_over_theta1'])
