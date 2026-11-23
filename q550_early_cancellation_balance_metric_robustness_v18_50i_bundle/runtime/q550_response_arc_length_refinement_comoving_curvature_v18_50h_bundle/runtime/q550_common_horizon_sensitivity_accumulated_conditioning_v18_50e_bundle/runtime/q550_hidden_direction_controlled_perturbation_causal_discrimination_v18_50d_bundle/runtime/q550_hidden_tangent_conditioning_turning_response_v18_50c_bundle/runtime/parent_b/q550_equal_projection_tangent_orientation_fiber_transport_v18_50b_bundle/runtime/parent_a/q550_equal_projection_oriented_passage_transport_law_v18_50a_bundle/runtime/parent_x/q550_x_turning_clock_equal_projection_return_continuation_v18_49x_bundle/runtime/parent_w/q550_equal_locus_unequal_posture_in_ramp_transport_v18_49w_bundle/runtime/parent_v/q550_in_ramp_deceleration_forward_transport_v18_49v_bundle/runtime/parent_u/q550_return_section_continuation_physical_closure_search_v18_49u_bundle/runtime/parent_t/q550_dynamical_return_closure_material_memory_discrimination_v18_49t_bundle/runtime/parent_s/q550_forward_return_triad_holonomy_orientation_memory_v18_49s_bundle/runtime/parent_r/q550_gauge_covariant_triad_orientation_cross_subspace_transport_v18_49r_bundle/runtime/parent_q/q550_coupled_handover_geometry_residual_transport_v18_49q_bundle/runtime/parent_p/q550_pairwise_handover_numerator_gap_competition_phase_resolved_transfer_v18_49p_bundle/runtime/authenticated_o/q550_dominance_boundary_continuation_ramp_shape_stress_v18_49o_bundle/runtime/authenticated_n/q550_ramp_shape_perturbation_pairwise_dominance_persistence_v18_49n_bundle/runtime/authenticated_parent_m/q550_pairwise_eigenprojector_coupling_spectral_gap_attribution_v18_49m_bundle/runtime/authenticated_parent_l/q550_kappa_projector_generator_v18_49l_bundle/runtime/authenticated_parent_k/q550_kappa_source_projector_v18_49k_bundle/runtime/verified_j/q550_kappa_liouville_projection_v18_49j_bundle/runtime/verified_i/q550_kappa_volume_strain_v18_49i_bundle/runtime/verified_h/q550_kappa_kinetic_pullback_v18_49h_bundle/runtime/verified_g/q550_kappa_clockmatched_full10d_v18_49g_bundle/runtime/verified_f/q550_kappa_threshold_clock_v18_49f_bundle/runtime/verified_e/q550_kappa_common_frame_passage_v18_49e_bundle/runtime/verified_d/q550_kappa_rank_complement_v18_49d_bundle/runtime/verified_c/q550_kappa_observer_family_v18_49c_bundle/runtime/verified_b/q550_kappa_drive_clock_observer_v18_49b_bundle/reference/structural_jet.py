#!/usr/bin/env python3
"""Q550 analytic structural decomposition H = slope * (H_base + kappa*H_coupling).
State order [y1,v1,theta1,omega1,y2,v2,theta2,omega2,z,vz,Theta].
All derivatives are w.r.t. the ORIGINAL 11D internal state (not normalized chart).
"""
import math
import numpy as np
from generated_base_jet import base_jet

# The coordinate gradients of log(rho2/rho1) and the relative phase.
A=np.zeros(11);A[0]=-1.;A[4]=1.
D=np.zeros(11);D[2]=1.;D[6]=1.;D[10]=-1.

def coupling_jet(y, params):
    """Return analytic K, DK, D²K where F_support=F_base + kappa0*K."""
    y=np.asarray(y,float)
    if y.shape!=(11,) or not np.all(np.isfinite(y)):raise ValueError('nonfinite 11D state')
    delta=float(y[2]+y[6]-params.phi0-y[10]); c=math.cos(delta);s=math.sin(delta)
    out=np.zeros(11);jac=np.zeros((11,11));hess=np.zeros((11,11,11))
    for ic,isin,a in ((1,False,A),(3,True,A),(5,False,-A),(7,True,-A)):
        rr=math.exp(float(y[4]-y[0])) if ic in (1,3) else math.exp(float(y[0]-y[4]))
        sign=1. if isin else -1.
        phase=s if isin else c
        first=(a*phase + D*(c if isin else -s))
        second=(np.outer(a,a)-np.outer(D,D))*phase + (np.outer(a,D)+np.outer(D,a))*(c if isin else -s)
        out[ic]=2*math.pi*sign*rr*phase
        jac[ic]=2*math.pi*sign*rr*first
        hess[ic]=2*math.pi*sign*rr*second
    return out,jac,hess

def structural_jet(y,kappa0,params,slope=1.0):
    f0,j0,h0=base_jet(y,params)
    fk,jk,hk=coupling_jet(y,params)
    return slope*(f0+kappa0*fk),slope*(j0+kappa0*jk),slope*(h0+kappa0*hk)

def analytic_delta(y,kappa_ref,kappa_new,params,slope=1.0):
    f,j,h=coupling_jet(y,params)
    alpha=slope*(kappa_new-kappa_ref)
    return alpha*f,alpha*j,alpha*h

def chart_kernel(hessian,reference_field,scale,g):
    """Equivalent to speed*g·D²F_z[u,e_j] in v18.47 chart; j=0..9.
    Here chart weights are w=[scale,1], z=(y[:10]-center)/scale.
    The gradient g is the original frozen diagnostic candidate gradient.
    """
    sc=np.asarray(scale,float);gg=np.asarray(g,float);fy=np.asarray(reference_field,float)
    if sc.shape!=(10,) or gg.shape!=(10,) or fy.shape!=(11,):raise ValueError('chart shapes')
    w=np.r_[sc,1.];v=fy/w
    # speed*u=v; exact cancellation of speed removes division by ||v||.
    return np.einsum('i,iab,a,bj->j',gg/sc,hessian[:10],fy,np.diag(w)[:,:10])
