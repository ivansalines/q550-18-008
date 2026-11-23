#!/usr/bin/env python3
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_audit import geometry,extract_events
L=np.array([1.,0.,0.,0.]);T=np.array([-.8,.6,0.,0.])
for W in [np.eye(4),np.diag([1,2,3,4])]:
    a=geometry(L,T,W)
    assert 0<a['cancellation']<1
    assert np.isclose(a['R_norm']**2,a['L_norm']**2+a['T_norm']**2+2*a['L_norm']*a['T_norm']*a['c_cos'],rtol=1e-13)
    b=geometry(T,L,W)
    assert np.isclose(a['cancellation'],b['cancellation'])
    assert np.isclose(a['c_cos'],b['c_cos'])
# Analytic smoothly evolving vectors with norm parity before cancellation peak.
t=np.linspace(.9,1.1,513)
rows=[]
for z in t:
    b=z; theta=2.0+0.02*(z-1)
    v=np.array([1.,0.,0.,0.]);w=b*np.array([np.cos(theta),np.sin(theta),0,0])
    rows.append(dict(horizon_xi=z,**geometry(v,w,np.eye(4))))
e=extract_events(rows)
assert e['parity'] and e['stationary'] and e['event_order']
print('v18.50l geometry, label symmetry and event extraction tests PASS')
