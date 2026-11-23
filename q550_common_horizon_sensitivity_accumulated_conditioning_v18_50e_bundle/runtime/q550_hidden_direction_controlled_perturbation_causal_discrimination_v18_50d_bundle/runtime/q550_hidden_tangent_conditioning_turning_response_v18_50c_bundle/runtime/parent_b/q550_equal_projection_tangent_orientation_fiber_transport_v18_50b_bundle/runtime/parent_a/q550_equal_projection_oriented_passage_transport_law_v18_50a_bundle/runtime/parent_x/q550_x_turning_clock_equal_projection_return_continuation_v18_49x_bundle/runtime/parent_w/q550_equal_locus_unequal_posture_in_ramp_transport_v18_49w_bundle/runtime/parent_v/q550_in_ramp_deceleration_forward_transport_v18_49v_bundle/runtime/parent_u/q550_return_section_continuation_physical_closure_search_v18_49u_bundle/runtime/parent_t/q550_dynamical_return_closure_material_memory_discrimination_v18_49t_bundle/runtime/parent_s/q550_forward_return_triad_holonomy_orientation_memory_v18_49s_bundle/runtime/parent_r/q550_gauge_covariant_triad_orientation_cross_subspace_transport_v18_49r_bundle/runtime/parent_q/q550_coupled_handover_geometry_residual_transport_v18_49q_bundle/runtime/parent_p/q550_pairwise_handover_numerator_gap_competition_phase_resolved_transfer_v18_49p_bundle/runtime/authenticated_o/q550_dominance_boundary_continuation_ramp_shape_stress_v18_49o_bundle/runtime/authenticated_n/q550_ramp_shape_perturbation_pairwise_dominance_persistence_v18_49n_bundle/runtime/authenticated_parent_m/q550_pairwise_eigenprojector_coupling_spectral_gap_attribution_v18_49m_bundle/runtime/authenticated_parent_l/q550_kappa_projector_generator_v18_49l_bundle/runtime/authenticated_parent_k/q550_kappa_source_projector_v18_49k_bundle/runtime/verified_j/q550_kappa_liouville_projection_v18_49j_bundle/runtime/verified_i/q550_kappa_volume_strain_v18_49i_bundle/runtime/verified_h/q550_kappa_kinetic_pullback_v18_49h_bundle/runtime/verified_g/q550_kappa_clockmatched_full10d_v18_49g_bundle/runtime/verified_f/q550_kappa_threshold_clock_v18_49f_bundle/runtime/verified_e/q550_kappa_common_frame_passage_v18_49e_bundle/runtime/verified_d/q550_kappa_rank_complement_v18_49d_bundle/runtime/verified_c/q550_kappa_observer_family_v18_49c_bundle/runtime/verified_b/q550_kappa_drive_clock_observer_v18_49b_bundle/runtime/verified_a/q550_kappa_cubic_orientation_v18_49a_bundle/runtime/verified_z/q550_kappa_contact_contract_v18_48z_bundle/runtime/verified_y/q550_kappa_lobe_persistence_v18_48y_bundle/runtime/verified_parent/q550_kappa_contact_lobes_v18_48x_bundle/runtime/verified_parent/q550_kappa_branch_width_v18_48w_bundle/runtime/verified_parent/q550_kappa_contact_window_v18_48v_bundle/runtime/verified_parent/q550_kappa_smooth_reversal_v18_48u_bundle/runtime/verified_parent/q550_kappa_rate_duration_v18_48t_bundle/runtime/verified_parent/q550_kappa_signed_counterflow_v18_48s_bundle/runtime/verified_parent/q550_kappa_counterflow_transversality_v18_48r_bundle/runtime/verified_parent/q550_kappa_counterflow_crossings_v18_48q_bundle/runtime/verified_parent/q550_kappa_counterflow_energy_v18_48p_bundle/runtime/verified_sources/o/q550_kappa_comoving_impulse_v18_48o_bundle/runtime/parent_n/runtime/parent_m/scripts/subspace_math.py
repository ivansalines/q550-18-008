"""Source-active near-null and sign-consistent one-dimensional subspace continuation.
All angles are measured in the frozen historical 10D Euclidean covector chart.
"""
import numpy as np
from observer_geometry_v18_48k import ratio_from_maps,unit

def source_active_mode(B,C,relative_cutoff):
    A=np.vstack((B,C));T=B+C
    U,s,Vh=np.linalg.svd(A,full_matrices=False)
    rank=int(np.count_nonzero(s>relative_cutoff*s[0]))
    if rank<1:raise ValueError('No source-active directions')
    # Whitening in source-active coordinates: ||A W z|| = ||z||.
    W=Vh[:rank,:].T/s[:rank][None,:]
    Q=T@W
    _,qs,vq=np.linalg.svd(Q,full_matrices=False)
    g=unit(W@vq[-1,:]);a=np.linalg.norm(A@g);t=np.linalg.norm(T@g)
    rr,nb,nc,nt,zero=ratio_from_maps(B,C,g)
    return dict(rank=rank,g=g,gen_min=float(qs[-1]),source_norm=float(a),resultant_norm=float(t),
                activity_relative=float(a/s[0]),cancel_ratio=float(rr),sigma_source_max=float(s[0]),
                sigma_source_last_active=float(s[rank-1]),source_null=bool(zero))

def full_null(B,C):
    A=np.vstack((B,C));T=B+C
    _,st,vt=np.linalg.svd(T,full_matrices=False)
    _,sa,_=np.linalg.svd(A,full_matrices=False)
    g=unit(vt[-1,:]);R,nb,nc,nt,z=ratio_from_maps(B,C,g)
    return dict(g=g,sigma_min=float(st[-1]),sigma_next=float(st[-2]),
        sigma_max=float(st[0]),source_sigma_min=float(sa[-1]),source_sigma_max=float(sa[0]),
        source_norm=float(np.linalg.norm(A@g)),resultant_norm=float(np.linalg.norm(T@g)),
        cancellation_ratio=float(R),coupling_zero=z)

def subspace_angle(u,v):
    c=float(np.clip(abs(np.dot(unit(u),unit(v))),0,1))
    # Robust small angles from norm difference after sign alignment.
    un=unit(u);vn=unit(v)
    if un@vn<0:vn=-vn
    return float(2*np.arcsin(min(1.,np.linalg.norm(un-vn)/2))*180/np.pi)
