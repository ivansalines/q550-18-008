"""Affine/time-dependent chart-gauge tensor, cotangent and metric transport.

For z'=G(t) z+b(t), H'=G H[G^-1,G^-1]; the frame drift is
(Gdot G^-1)(z'-b)+bdot, which has zero spatial Hessian.
Use *material* velocity G F, not total moving-coordinate derivative.
For covectors p'=G^-T p and K'=G^-T K, use cometric G G.T.
"""
from __future__ import annotations
import numpy as np

def unit(a):
    n=np.linalg.norm(a)
    if n<1e-30 or not np.isfinite(n):raise ValueError('vanishing vector')
    return a/n

def align_rotation(u,v):
    """Minimal proper rotation sending unit u to v in R^d (u != -v)."""
    u=unit(np.asarray(u,float));v=unit(np.asarray(v,float))
    c=float(np.clip(u@v,-1,1));I=np.eye(len(u))
    if c>1-1e-14:return I
    if c<-1+1e-10:raise ValueError('antipodal tangent: ambiguous transport')
    K=np.outer(v,u)-np.outer(u,v)
    R=I+K+(K@K)/(1+c)
    if np.linalg.norm(R@u-v)>2e-10 or np.linalg.norm(R.T@R-I)>2e-10:
        raise ValueError('bad minimal rotation')
    return R

def frames_from_velocities(vs):
    vs=np.asarray(vs,float);us=np.asarray([unit(a) for a in vs]);n=vs.shape[1]
    E=align_rotation(np.eye(n)[0],us[0])
    frames=[E.T.copy()]
    for a,b in zip(us[:-1],us[1:]):
        E=align_rotation(a,b)@E
        frames.append(E.T.copy())
    for S,u in zip(frames,us):
        if np.linalg.norm(S@u-np.eye(n)[0])>3e-10:raise ValueError('comoving frame not tangent aligned')
    return np.array(frames)

def chart_hessian(H,w):
    H=np.asarray(H,float);w=np.asarray(w,float)
    return H*w[None,:,None]*w[None,None,:]/w[:,None,None]

def push_forward_tensor(H,G):
    Gi=np.linalg.inv(G)
    return np.einsum('pi,ijk,ja,kb->pab',G,H,Gi,Gi,optimize=True)

def projection(H,g,v):
    return np.einsum('p,pab,a->b',g,H,v,optimize=True)[:10]

def covector_transform(k,S):return np.linalg.solve(S.T,k)

def corrected_norm(k_prime,S):
    # Cometric on covectors inherited from the original Euclidean chart.
    a=S.T@k_prime
    return float(np.linalg.norm(a))

def ratio(B,C,norm=np.linalg.norm):
    nb=float(norm(B));nc=float(norm(C));ns=float(norm(B+C))
    if nc<1e-12*max(nb,1e-30):return 1.
    return (nb+nc)/max(ns,1e-30)

def connection_identity(G,Gdot,J,g):
    """Instantaneous covector connection identity for original adjoint -J.T*g.
    Does not by itself prove the measured observer follows that ODE.
    """
    Gi=np.linalg.inv(G);cov=Gi.T@g
    Jnew=G@J@Gi+Gdot@Gi
    d_cov=Gi.T@(-J.T@g)-Gi.T@Gdot.T@cov
    rhs=-Jnew.T@cov
    return np.linalg.norm(d_cov-rhs)/max(1.,np.linalg.norm(rhs))
