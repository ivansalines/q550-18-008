#!/usr/bin/env python3
"""Independent algebra/FD regression of the analytic normalized-jet Jacobian."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_audit import analytic_structural_observer_jet,projector,subspace_diagnostics
rng=np.random.default_rng(50)
f=rng.normal(size=11)
j=rng.normal(size=(11,11))
h=rng.normal(size=(11,11,11));h=(h+h.swapaxes(1,2))/2
weights=np.array([1.,2.,3.,4.]);scales=np.linspace(1,3,10)
d,B,raw,dh=analytic_structural_observer_jet(f,j,h,weights,scales)
assert abs(d@d-1)<1e-14
assert np.linalg.norm(d@B)<1e-13
P,K,s,rank=projector(B)
assert rank==3 and K.shape==(10,7)
assert np.linalg.norm(P@P-P)<1e-12
assert np.linalg.norm(B@P)<1e-12
assert subspace_diagnostics(K,K)['max_angle_deg']<1e-5
# Finite difference of a *separate polynomial realization* of F,J,H.
def observer(delta):
    F=f+j@delta+0.5*np.einsum('ijk,j,k->i',h,delta,delta)
    J=j+np.einsum('ijk,k->ij',h,delta)
    g=J@F
    u=np.array([F[2],F[6],g[2],g[6]])/weights
    return u/np.linalg.norm(u)
fd=np.empty_like(B)
for k in range(10):
    delta=np.zeros(11);delta[k]=1.e-6
    fd[:,k]=(observer(delta)-observer(-delta))/(2e-6*scales[k])
assert np.linalg.norm(B-fd)/np.linalg.norm(B)<1.e-8
# Orthogonal observer rotations preserve rank and the 10D kernel projector.
Q,_=np.linalg.qr(rng.normal(size=(4,4)))
_,K2,ss,rank2=projector(Q@B)
assert rank2==3 and np.linalg.norm(K@K.T-K2@K2.T)<1e-10
print('v18.50q analytic observer chain rule, rank-3 constraint and 7D projector tests PASS')
