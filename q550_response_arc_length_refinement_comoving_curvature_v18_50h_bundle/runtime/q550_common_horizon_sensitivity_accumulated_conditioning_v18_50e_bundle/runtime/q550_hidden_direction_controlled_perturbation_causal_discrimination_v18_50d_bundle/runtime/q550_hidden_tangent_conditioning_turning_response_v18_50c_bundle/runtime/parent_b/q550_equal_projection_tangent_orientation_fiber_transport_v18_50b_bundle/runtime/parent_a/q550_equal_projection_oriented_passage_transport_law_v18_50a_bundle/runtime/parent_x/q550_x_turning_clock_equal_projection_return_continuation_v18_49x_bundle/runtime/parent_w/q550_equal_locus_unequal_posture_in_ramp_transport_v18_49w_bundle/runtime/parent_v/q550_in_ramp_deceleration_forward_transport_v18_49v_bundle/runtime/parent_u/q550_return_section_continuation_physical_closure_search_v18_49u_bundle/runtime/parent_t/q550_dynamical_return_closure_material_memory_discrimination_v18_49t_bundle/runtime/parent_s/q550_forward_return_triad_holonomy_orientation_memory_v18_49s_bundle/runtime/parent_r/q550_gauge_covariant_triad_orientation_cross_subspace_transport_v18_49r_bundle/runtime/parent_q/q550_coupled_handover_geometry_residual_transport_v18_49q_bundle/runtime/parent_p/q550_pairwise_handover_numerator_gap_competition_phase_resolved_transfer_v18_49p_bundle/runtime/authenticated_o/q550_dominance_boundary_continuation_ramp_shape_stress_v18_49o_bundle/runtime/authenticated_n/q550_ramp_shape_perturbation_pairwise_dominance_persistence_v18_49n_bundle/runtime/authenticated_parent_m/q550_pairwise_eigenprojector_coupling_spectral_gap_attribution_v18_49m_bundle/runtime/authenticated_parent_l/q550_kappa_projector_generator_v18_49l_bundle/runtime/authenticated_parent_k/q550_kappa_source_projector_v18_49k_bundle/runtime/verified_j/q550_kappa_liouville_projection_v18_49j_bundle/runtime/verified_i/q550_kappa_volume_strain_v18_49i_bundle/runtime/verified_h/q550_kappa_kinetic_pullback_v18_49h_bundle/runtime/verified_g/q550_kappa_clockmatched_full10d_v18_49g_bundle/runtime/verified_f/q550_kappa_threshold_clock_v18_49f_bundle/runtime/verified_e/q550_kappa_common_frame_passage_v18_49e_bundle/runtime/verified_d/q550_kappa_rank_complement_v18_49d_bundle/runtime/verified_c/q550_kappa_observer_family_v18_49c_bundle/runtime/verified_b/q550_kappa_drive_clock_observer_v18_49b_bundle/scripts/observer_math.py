"""Physical-cotangent transport in the 10D material subsystem at fixed drive control.

Theta is prescribed externally. Thus J is the 10x10 partial material Jacobian
of the unchanged 11D physical RHS; the omitted control perturbation is ZERO.
The dual pairing g^T v is conserved for the variational/adjoint system, not
for arbitrary differences of two finite-amplitude trajectories.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp

def dual_field(J,g,v):
    return -J.T@g,J@v

def diagonal_covariance(g,v,scale):
    S=np.asarray(scale,float)
    return float((g/S)@(S*v)-g@v)

def shape_gradient(a,b):
    """d ||shape(a)-shape(b)|| / d a[:10] at fixed comparison state b.

    shape=(log rho1, log rho2, sigmoid z). This is an ordinary gradient of
    the selected projected distance, not a constitutive/material metric.
    """
    delta=np.array([a[0]-b[0],a[4]-b[4],0.],float)
    z1,z2=float(a[8]),float(b[8]);x1=1/(1+np.exp(-z1));x2=1/(1+np.exp(-z2))
    delta[2]=x1-x2
    d=float(np.linalg.norm(delta))
    out=np.zeros(10)
    if d>1e-14:
        out[0]=delta[0]/d;out[4]=delta[1]/d;out[8]=delta[2]*x1*(1-x1)/d
    return out,d

def projective_angle(g,ref):
    x=np.asarray(g,float);y=np.asarray(ref,float)
    n=np.linalg.norm(x)*np.linalg.norm(y)
    return float(np.degrees(np.arccos(np.clip(abs(float(x@y))/n,-1.,1.)))) if n>0 else float('nan')

def integrate_dual(state,design,kappa,params,slope,omega,jacobian,g0,v0,duration,rtol=2e-10,atol=2e-12,max_step=.0125):
    """Genuine tangent/adjoint IVP on a prescribed-control, material trajectory."""
    g0=np.asarray(g0,float)
    v0=np.asarray(v0,float)
    count=len(g0)
    init=np.r_[g0.reshape(-1),v0]
    def rhs(t,z):
        y=state(t)[:11]
        J=jacobian(y,kappa,params,slope)[:10,:10]
        g=z[:count*10].reshape(count,10);v=z[count*10:]
        gd,vd=dual_field(J,g.T,v)
        # dual_field expects J,g(10,n); return gdot(10,n)
        return np.r_[gd.T.ravel(),vd]
    ans=solve_ivp(rhs,(0.,duration),init,method='DOP853',rtol=rtol,atol=atol,max_step=max_step,dense_output=True)
    if not ans.success:raise RuntimeError('Cotangent IVP failed: '+ans.message)
    def evaluate(t):
        z=ans.sol(float(t))
        return z[:count*10].reshape(count,10),z[count*10:]
    return evaluate,ans
