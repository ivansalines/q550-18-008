"""Principal-angle geometry on frozen normalized ten-dimensional covector charts.

No rank is asserted exactly. Mathematically mandatory intersections by dimension
are explicitly separated from numerically near-shared directions.
"""
from __future__ import annotations
import numpy as np

def orth(X):
    X=np.asarray(X,float)
    if X.ndim != 2:raise ValueError('basis must be 2D')
    if X.shape[1]==0:return np.zeros((X.shape[0],0))
    Q,R=np.linalg.qr(X,mode='reduced')
    if np.linalg.matrix_rank(R,tol=1e-11*np.linalg.norm(R,ord=2))<X.shape[1]:
        raise ValueError('linearly dependent basis')
    return Q

def projector(U):
    U=orth(U)
    return U@U.T

def principal(U,V):
    U=orth(U);V=orth(V)
    if U.shape[0]!=V.shape[0]:raise ValueError('ambient dimension mismatch')
    n=U.shape[0];r=U.shape[1];s=V.shape[1]
    if min(r,s)==0:
        return dict(angles_deg=[],principal_cosines=[],frobenius_gap=float(np.sqrt(r+s)),
          spectral_gap=float(bool(r or s)),numeric_shared_1e_4=0,numeric_shared_1e_2=0,
          mandatory_intersection_dimension=max(0,r+s-n),dimension_a=r,dimension_b=s)
    cross=U.T@V
    u,c,vh=np.linalg.svd(cross,full_matrices=False)
    c=np.clip(c,0.,1.)
    angles=np.rad2deg(np.arccos(c))
    # Residual norms for robust principal small-angle diagnostic.
    align=V@vh.T
    safe=[]
    for j in range(len(c)):
        anchor=U@u[:,j]
        dif=align[:,j]-(anchor if anchor@align[:,j]>=0 else -anchor)
        safe.append(float(np.rad2deg(2*np.arcsin(min(1.,np.linalg.norm(dif)/2)))))
    pp=U@U.T-V@V.T
    return dict(angles_deg=safe,principal_cosines=c.tolist(),
      frobenius_gap=float(np.linalg.norm(pp,'fro')),
      spectral_gap=float(np.linalg.norm(pp,ord=2)),
      numeric_shared_1e_4=int(np.sum(np.asarray(safe)<1e-4)),
      numeric_shared_1e_2=int(np.sum(np.asarray(safe)<1e-2)),
      mandatory_intersection_dimension=max(0,r+s-n),dimension_a=r,dimension_b=s)

def principal_candidates(U,V):
    """Vectors anchored in each subspace for each principal angle."""
    U=orth(U);V=orth(V)
    if min(U.shape[1],V.shape[1])==0:return []
    left,c,right=np.linalg.svd(U.T@V,full_matrices=False)
    pairs=[]
    for j in range(len(c)):
        a=U@left[:,j]; b=V@right.T[:,j]
        if a@b<0:b=-b
        g=a+b
        if np.linalg.norm(g)==0:g=a
        g/=np.linalg.norm(g)
        pairs.append((a,b,g,float(np.clip(c[j],0,1))))
    return pairs

def source_active_subspaces(B,C,source_cutoff,relative_cancel_cutoff):
    """Right SVD source plane, then whitened near-cancellation subspace.

    T W singular values measure ||T g||/||A g|| on active source plane,
    where W has A-orthonormal columns. Returned plane uses Euclidean QR.
    """
    A=np.vstack((B,C));T=B+C
    _,source_s,Vh=np.linalg.svd(A,full_matrices=False)
    r=int(np.sum(source_s>source_cutoff*source_s[0])); r=max(1,r)
    src=orth(Vh[:r,:].T)
    W=Vh[:r,:].T/source_s[:r][None,:]
    _,qs,vqh=np.linalg.svd(T@W,full_matrices=False)
    # The threshold is on the generalized residual relative to source response.
    count=int(np.sum(qs<=relative_cancel_cutoff))
    plane=orth(W@vqh[-count:,:].T) if count else np.zeros((B.shape[1],0))
    return dict(src=src,near=plane,source_rank=r,near_rank=count,
      source_sigma_max=float(source_s[0]),source_last=float(source_s[r-1]),
      generalized_min=float(qs[-1]),generalized_second=float(qs[-2]) if r>1 else None,
      generalized_values=qs.tolist(),A=A,T=T)

def evaluate_shared_direction(B0,C0,B1,C1,g):
    g=np.asarray(g,float);g=g/np.linalg.norm(g)
    a0=np.linalg.norm(np.r_[(B0@g),(C0@g)]);a1=np.linalg.norm(np.r_[(B1@g),(C1@g)])
    t0=np.linalg.norm((B0+C0)@g);t1=np.linalg.norm((B1+C1)@g)
    return dict(source_a=float(a0),source_b=float(a1),resultant_a=float(t0),resultant_b=float(t1),
       source_relative_a=float(a0/max(np.linalg.svd(np.vstack((B0,C0)),compute_uv=False)[0],1e-300)),
       source_relative_b=float(a1/max(np.linalg.svd(np.vstack((B1,C1)),compute_uv=False)[0],1e-300)),
       residual_over_source_a=float(t0/max(a0,1e-300)),residual_over_source_b=float(t1/max(a1,1e-300)))

def projected_line_angle(g,h,axes):
    g=np.asarray(g)[list(axes)];h=np.asarray(h)[list(axes)]
    gn=np.linalg.norm(g);hn=np.linalg.norm(h)
    if gn<1e-12 or hn<1e-12:return None,gn,hn
    cos=abs(float(g@h))/(gn*hn)
    return float(np.rad2deg(np.arccos(np.clip(cos,-1,1)))),float(gn),float(hn)
