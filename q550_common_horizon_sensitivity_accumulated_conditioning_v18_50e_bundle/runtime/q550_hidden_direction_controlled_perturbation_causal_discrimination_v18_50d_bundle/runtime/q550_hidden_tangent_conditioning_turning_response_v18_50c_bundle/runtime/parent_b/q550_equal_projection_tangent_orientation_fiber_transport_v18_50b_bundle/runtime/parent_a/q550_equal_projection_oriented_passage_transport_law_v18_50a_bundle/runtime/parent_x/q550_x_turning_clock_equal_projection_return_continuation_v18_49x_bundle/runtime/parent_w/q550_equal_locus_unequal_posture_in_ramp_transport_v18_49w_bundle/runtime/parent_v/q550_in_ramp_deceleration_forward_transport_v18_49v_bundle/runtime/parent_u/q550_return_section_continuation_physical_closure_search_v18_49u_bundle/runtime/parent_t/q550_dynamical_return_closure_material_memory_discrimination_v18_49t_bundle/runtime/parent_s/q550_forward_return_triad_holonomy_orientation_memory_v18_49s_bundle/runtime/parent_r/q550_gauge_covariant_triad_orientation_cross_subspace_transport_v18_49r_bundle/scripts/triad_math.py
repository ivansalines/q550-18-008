"""Gauge-covariant triad decompositions in the fixed kinetic metric.

No intrinsic orientation is assigned to a set of three *unoriented* eigenlines.
Orientation of an aligned eigenframe is relative to an explicit initial sign gauge.
Projectors, K_ij, cross-subspace singular values, commutator alignment, and
subspace parallel transport are invariant under all independent line-sign flips.
"""
import numpy as np
from scipy.linalg import expm
IN=np.array([5,6,7]); OUT=np.array([0,1,2,3,4,8,9]); EYE=np.eye(10)

def decompose(K,P):
    S=np.sum(P[IN],axis=0); T=EYE-S
    ki=S@K@S; kc=S@K@T+T@K@S; ke=T@K@T
    dS=K@S-S@K
    b=T@K@S
    denom=max(1.,np.linalg.norm(K))
    frac=lambda x:float(np.linalg.norm(x)**2/np.linalg.norm(K)**2)
    return {'S':S,'ki':ki,'kc':kc,'ke':ke,'dS':dS,'b':b,
        'frac_internal':frac(ki),'frac_cross':frac(kc),'frac_external':frac(ke),
        'closure':float(np.linalg.norm(K-ki-kc-ke)/denom),
        'cross_derivative_closure':float(np.linalg.norm(dS-(kc@S-S@kc))),
        'svals':np.linalg.svd(b,compute_uv=False)[:3]}

def parts_from_eigenaxes(axes,Omega):
    """Return the invariant pair operators from gauge-variant axes and Omega."""
    from itertools import combinations
    out={}
    for i,j in combinations(range(10),2):
        out[(i,j)]=Omega[j,i]*(np.outer(axes[:,j],axes[:,i])-np.outer(axes[:,i],axes[:,j]))
    return out

def chi(p67,p78,p68,tol=1e-12):
    comm=p67@p78-p78@p67
    d=np.linalg.norm(comm)*np.linalg.norm(p68)
    return (float(np.sum(comm*p68)/d),float(d)) if d>tol else (None,float(d))

def gauge_flip(axes,omega,signs):
    """Signs are arbitrary and independent for all eigenlines."""
    d=np.asarray(signs,float);return axes*d[np.newaxis,:],(d[:,None]*omega*d[None,:])

def aligned_triad(axes,reference):
    A=np.asarray(axes[:,IN],float).copy()
    if reference is None:return A, np.ones(3),np.ones(3)
    overlaps=np.sum(reference*A,axis=0)
    s=np.where(overlaps<0,-1.,1.)
    return A*s[np.newaxis,:],s,np.abs(overlaps)

def transport_cross(cross_midpoints,h):
    U=np.eye(10)
    for kc in cross_midpoints:U=expm(h*kc)@U
    return U

def aligned_relative_rotation(A0,Ucross,Aend):
    # Under exact Kato transport, Ucross maps S0 to Send. The 3x3 block is SO(3)
    raw=A0.T@Ucross.T@Aend
    u,s,vt=np.linalg.svd(raw)
    rot=u@vt
    return raw,rot,s,float(np.arccos(np.clip((np.trace(rot)-1)/2,-1.,1.)))
