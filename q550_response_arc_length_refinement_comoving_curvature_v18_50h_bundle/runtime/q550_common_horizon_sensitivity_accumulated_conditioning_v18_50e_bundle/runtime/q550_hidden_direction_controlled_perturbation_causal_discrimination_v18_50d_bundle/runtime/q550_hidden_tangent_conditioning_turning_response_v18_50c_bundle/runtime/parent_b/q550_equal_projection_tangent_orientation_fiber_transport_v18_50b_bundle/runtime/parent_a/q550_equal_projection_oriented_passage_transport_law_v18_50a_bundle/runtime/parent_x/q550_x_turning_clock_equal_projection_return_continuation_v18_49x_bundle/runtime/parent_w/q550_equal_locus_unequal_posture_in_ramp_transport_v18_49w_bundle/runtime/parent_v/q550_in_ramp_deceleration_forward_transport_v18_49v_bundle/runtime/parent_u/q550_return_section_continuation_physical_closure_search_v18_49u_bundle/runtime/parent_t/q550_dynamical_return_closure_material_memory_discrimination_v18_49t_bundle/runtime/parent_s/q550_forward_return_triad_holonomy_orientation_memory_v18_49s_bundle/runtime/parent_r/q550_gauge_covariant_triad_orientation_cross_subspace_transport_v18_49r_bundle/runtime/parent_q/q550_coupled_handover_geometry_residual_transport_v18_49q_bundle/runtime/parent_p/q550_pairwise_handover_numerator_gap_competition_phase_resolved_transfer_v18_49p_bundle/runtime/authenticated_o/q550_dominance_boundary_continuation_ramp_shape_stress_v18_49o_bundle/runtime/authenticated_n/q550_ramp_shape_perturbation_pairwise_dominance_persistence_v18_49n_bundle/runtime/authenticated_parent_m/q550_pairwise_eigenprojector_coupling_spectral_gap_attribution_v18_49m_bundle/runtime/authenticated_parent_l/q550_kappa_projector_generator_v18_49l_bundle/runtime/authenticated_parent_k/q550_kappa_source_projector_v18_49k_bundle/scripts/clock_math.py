"""Clock-matched source roots, gauge-safe rank-one eigenprojector transport.

A scalar root derived from a volume form need not be an observer-free event.
Projector P_i=a_i a_i^T is invariant under eigenvector sign; the chosen
Euclidean frame is the initial kinetic embedding with tau_ref=1.
"""
from __future__ import annotations
import itertools
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

def roots_on_grid(q,y):
    q=np.asarray(q,float);y=np.asarray(y,float)
    if q.ndim!=1 or len(q)!=len(y) or np.any(np.diff(q)<=0):raise ValueError('Invalid clock grid')
    f=PchipInterpolator(q,y)
    results=[]
    for i in range(len(q)-1):
        if y[i]==0:results.append(float(q[i]))
        if y[i]*y[i+1]<0:results.append(float(brentq(f,float(q[i]),float(q[i+1]),xtol=3e-14)))
    if y[-1]==0:results.append(float(q[-1]))
    return sorted(set(results))

def smooth_root(q,y,require_unique=True):
    roots=roots_on_grid(q,y)
    if require_unique and len(roots)!=1:return float('nan'),len(roots)
    return (roots[0] if roots else float('nan')),len(roots)

def projector_speed(q,axes):
    """Speed of each projective line: ||d(aa^T)/dq||_F/sqrt(2).

    Assumes axes ordered by continuously isolated eigenvalues; detects
    near-crossings separately. Sign changes do not change projectors.
    """
    a=np.asarray(axes,float)
    P=np.einsum('nki,nli->nikl',a,a)
    dp=np.gradient(P,np.asarray(q,float),axis=0,edge_order=2)
    v=np.sqrt(np.maximum(0.,np.einsum('nkij,nkij->nk',dp,dp)/2.))
    return P,dp,v

def half_turn_clock(q,speed):
    """Weighted median of nonnegative projector angular speed, not a discrete peak."""
    q=np.asarray(q,float);s=np.asarray(speed,float)
    weights=.5*(s[:-1]+s[1:])*np.diff(q)
    total=float(weights.sum())
    if total<1e-11:return float('nan'),total
    partial=np.concatenate([[0.],np.cumsum(weights)])
    idx=min(int(np.searchsorted(partial,total*.5,side='right')-1),len(weights)-1)
    fraction=np.clip((total*.5-partial[idx])/weights[idx],0,1) if weights[idx] else 0.
    return float(q[idx]+fraction*(q[idx+1]-q[idx])),total

def projector_rates(q,u,axes):
    P,dp,speeds=projector_speed(q,axes)
    u=np.asarray(u,float)
    du=np.gradient(u,np.asarray(q,float),axis=0,edge_order=2)
    occup=np.einsum('ni,nkij,nj->nk',u,P,u)
    rate_direction=2*np.einsum('ni,nkij,nj->nk',du,P,u)
    rate_projector=np.einsum('ni,nkij,nj->nk',u,dp,u)
    return occup,rate_direction,rate_projector,speeds

def exact_permutation_p(x,y):
    """Exact 6! permutation test for centered Pearson correlation (DESCRIPTIVE only)."""
    x=np.asarray(x,float);y=np.asarray(y,float)
    n=len(x)
    if n>8:raise ValueError('Exhaustive permutation limit')
    xc=x-x.mean();yc=y-y.mean()
    den=np.linalg.norm(xc)*np.linalg.norm(yc)
    if den<=1e-12:return float('nan'),float('nan')
    obs=float(xc@yc/den)
    extreme=sum(abs(float(xc@yc[np.asarray(p)]/den))>=abs(obs)-1e-13
                for p in itertools.permutations(range(n)))
    return obs,float(extreme/__import__('math').factorial(n))
