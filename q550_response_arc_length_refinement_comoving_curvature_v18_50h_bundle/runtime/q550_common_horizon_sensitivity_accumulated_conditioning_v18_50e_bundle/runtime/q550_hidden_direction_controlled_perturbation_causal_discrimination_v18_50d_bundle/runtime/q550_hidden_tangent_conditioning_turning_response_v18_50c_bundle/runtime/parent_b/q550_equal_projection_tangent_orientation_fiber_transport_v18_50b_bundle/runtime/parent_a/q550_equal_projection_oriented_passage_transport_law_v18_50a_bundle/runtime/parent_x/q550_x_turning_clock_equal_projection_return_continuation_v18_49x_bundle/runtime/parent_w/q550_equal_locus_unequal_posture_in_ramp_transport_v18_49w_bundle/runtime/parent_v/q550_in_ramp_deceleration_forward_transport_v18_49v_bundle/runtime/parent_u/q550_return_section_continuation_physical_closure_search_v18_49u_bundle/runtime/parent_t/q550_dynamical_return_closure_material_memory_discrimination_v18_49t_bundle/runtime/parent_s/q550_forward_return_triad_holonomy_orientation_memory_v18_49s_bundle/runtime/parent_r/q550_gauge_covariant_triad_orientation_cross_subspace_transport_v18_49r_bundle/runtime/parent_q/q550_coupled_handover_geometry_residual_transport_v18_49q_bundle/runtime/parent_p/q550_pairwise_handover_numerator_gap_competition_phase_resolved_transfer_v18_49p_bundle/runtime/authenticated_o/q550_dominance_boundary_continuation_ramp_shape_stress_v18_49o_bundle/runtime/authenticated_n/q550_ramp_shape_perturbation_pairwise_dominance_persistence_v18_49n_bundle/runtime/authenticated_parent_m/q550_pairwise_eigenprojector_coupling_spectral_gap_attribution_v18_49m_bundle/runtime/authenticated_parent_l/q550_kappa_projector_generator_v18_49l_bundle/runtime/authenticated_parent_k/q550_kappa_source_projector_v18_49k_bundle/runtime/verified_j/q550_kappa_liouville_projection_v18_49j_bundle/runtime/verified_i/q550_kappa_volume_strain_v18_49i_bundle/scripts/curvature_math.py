"""Covariant S^9 geodesic curvature in one fixed flat kinetic frame.

For an arbitrary smooth path u(q) of unit vectors:
   v=||du/dq||, T=u'/v,
   k_g=|| (I-uu^T-TT^T)u'' || / v^2.
This is invariant to smooth monotone reparameterization of the curve
and to metric-preserving coordinate transformations. It is NOT independent
of the chosen Sasaki position/velocity weighting tau_ref.
"""
import numpy as np

def unit(v):
    a=np.asarray(v,float);n=np.linalg.norm(a,axis=-1,keepdims=True)
    if np.any(n<1e-12):raise ValueError('Undefined material direction')
    return a/n

def path_angles(u):
    u=unit(u)
    step=2*np.arcsin(np.clip(np.linalg.norm(np.diff(u,axis=0),axis=1)/2,0,1))
    end=2*np.arcsin(np.clip(np.linalg.norm(u[-1]-u[0])/2,0,1))
    return dict(length_deg=float(np.rad2deg(step.sum())),endpoint_deg=float(np.rad2deg(end)),
                excess_deg=float(np.rad2deg(step.sum()-end)))

def sphere_curvature(u,q,trim=4):
    q=np.asarray(q,float);u=unit(u)
    d1=np.gradient(u,q,axis=0,edge_order=2)
    d2=np.gradient(d1,q,axis=0,edge_order=2)
    speed=np.linalg.norm(d1,axis=1)
    tangent=d1/np.maximum(speed[:,None],1e-14)
    normal=d2 -np.sum(d2*u,axis=1)[:,None]*u -np.sum(d2*tangent,axis=1)[:,None]*tangent
    k=np.linalg.norm(normal,axis=1)/np.maximum(speed,1e-14)**2
    valid=np.arange(len(q))[trim:len(q)-trim]
    return dict(curvature=k,speed=speed,indices=valid,
                median=float(np.median(k[valid])),maximum=float(np.max(k[valid])),
                speed_min=float(np.min(speed[valid])))
