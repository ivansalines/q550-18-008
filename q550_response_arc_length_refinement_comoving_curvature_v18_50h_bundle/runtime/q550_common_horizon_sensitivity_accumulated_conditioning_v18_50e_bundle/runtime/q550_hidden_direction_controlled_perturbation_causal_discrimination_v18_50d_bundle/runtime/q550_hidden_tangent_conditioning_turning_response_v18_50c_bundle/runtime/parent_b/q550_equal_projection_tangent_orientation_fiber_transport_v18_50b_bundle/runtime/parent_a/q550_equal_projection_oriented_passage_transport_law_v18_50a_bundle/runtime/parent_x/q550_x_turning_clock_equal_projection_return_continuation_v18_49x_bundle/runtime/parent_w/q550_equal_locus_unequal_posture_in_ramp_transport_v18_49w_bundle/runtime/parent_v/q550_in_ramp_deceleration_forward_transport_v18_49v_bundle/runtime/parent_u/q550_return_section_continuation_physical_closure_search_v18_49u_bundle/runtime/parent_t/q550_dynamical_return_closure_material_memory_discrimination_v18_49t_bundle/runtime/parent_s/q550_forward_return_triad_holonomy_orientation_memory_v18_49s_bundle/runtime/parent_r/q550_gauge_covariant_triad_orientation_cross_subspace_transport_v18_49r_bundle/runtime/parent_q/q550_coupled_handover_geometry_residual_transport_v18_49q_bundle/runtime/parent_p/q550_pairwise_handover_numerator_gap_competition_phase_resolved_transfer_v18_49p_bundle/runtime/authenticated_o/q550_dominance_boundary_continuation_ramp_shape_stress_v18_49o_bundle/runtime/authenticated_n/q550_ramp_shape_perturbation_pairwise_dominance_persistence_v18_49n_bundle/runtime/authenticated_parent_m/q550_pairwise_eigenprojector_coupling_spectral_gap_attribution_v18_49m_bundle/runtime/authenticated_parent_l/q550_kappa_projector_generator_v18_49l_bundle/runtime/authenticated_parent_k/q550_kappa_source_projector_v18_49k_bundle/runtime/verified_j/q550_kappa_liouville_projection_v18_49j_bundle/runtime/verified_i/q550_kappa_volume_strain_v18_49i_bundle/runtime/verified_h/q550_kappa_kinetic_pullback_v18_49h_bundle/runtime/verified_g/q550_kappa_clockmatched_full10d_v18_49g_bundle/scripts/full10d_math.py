"""Full 10D spherical curve statistics in one declared Euclidean common frame.

No intrinsic chiral orientation is inferred from a path in S^9. Direction
reversal flips the order of samples but leaves arclength and endpoint angle.
The chart metric must be transformed along with any coordinate transformation.
"""
from __future__ import annotations
import numpy as np

def unit(v):
    x=np.asarray(v,dtype=float)
    n=np.linalg.norm(x,axis=-1,keepdims=True)
    if np.any(n<1e-12):raise ValueError('A vanishing vector has no direction')
    return x/n

def metric_dot(a,b,metric):return float(np.asarray(a)@metric@np.asarray(b))
def normalized_in_metric(a,M):
    a=np.asarray(a,dtype=float)
    den=np.sqrt(metric_dot(a,a,M))
    if den<1e-12:raise ValueError('Metric length vanished')
    return a/den

def metric_cos(a,b,M):
    return float(np.clip(metric_dot(a,b,M)/np.sqrt(metric_dot(a,a,M)*metric_dot(b,b,M)),-1,1))

def spherical_path(vectors,metric=None):
    arr=np.asarray(vectors,float)
    if arr.ndim!=2 or arr.shape[0]<2:raise ValueError('Need 2+ vectors')
    M=np.eye(arr.shape[1]) if metric is None else np.asarray(metric,float)
    u=np.array([normalized_in_metric(x,M) for x in arr])
    dots=np.array([metric_cos(a,b,M) for a,b in zip(u[:-1],u[1:])])
    steps=np.arccos(dots)
    endpoint=np.arccos(metric_cos(u[0],u[-1],M))
    return {'length_deg':float(np.rad2deg(sum(steps))),
            'endpoint_deg':float(np.rad2deg(endpoint)),
            'excess_deg':float(np.rad2deg(sum(steps)-endpoint)),
            'steps_deg':np.rad2deg(steps),
            'normalizations':u}

def project_outside_basis(v,basis):
    basis=np.asarray(basis,float)
    return np.asarray(v,float)-basis@(basis.T@v)

def chart_covariance_error(path):
    """Affine chart y'=S y with M'=S^-T M S^-1, unchanged path metrics."""
    original=spherical_path(path)
    n=path.shape[1]
    S=np.eye(n)+.12*np.eye(n,k=1)+.07*np.eye(n,k=-2)
    inv=np.linalg.inv(S)
    M=inv.T@inv
    moved=spherical_path(np.asarray(path)@S.T,M)
    return max(abs(moved[k]-original[k]) for k in ['length_deg','endpoint_deg','excess_deg'])

def arclength_to_angle_ratio(path):
    res=spherical_path(path)
    return res['length_deg']/max(1e-14,res['endpoint_deg'])
