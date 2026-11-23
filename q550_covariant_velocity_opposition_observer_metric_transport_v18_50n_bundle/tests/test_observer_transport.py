#!/usr/bin/env python3
"""Local synthetic identities — independent of numerical Q550 results."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from run_audit import angle,known_gauge,comoving,adversarial_metric

a=np.array([1.,0.,2.,-.4]);b=np.array([-1.,2.,-.9,.1])
da=np.array([-3.,4.,.5,1.]);db=np.array([1.,-2.,-8.,2.])
W=np.array([[2,.3,0,0],[.3,1,.1,0],[0,.1,2,.2],[0,0,.2,1]],float)
assert np.linalg.eigvalsh(W).min()>0
s=known_gauge(a,b,da,db,W,410)
assert abs(s['covariant_rotating_angle_deg']-angle(da,db,W))<1e-10
assert abs(s['covariant_sheared_angle_deg']-angle(da,db,W))<1e-10
assert s['finite_pulled_metric_invariance_error']<1e-12
c=comoving(a,b,da,db,W)
assert c['transverse_after_frame_correction']<1e-8
assert c['transverse_speed_before_frame_correction']>0
s2=known_gauge(a,b,da,db,W,-300)
assert abs(s2['covariant_rotating_angle_deg']-s['covariant_rotating_angle_deg'])<1e-10
# Deliberate SPD bisector negative-control on obtuse but nonparallel pair.
c1=np.array([1.,0.,0.,0.]);c2=np.array([-.8,.6,0.,0.])
assert angle(c1,c2)>90 and adversarial_metric(c1,c2)<90
print('v18.50n mathematical observer/covariance tests PASS')
