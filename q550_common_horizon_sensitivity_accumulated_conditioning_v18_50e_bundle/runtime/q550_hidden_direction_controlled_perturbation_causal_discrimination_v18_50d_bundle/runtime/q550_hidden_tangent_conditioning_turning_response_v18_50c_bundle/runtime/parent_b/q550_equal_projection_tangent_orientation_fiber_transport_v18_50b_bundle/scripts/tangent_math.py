"""Coordinate-chart tangent geometry; not a physical or coordinate-invariant fiber metric."""
import numpy as np

def cosine(u,v,scale=None):
    a=np.asarray(u,float);b=np.asarray(v,float)
    if a.shape!=b.shape or a.ndim!=1:raise ValueError('Mismatched tangent shape')
    if scale is not None:
        s=np.asarray(scale,float)
        if s.shape!=a.shape or np.any(s<=0) or not np.isfinite(s).all():raise ValueError('Bad scale')
        a=a/s;b=b/s
    na=np.linalg.norm(a);nb=np.linalg.norm(b)
    if na<1e-14 or nb<1e-14:return None
    return float(np.clip(a@b/(na*nb),-1.,1.))

def fiber_fraction(vec,scale):
    u=np.asarray(vec,float)/np.asarray(scale,float)
    mag=float(np.linalg.norm(u))
    return float(np.linalg.norm(u[1:])/mag) if mag>1e-14 else None

def range_scales(samples, floor_rel=1e-5, floor_abs=1e-8):
    arr=np.asarray(samples,float)
    if arr.ndim!=2 or arr.shape[0]<3:raise ValueError('Need time series')
    span=np.ptp(arr,axis=0)
    return np.maximum(span,np.maximum(np.max(span)*floor_rel,floor_abs))

def equal_x_opposed(dx1,dx2,tol=1e-12):
    if abs(dx1)<tol or abs(dx2)<tol:return 'grazing'
    return 'opposed' if dx1*dx2<0 else 'same'

def five_state_and_tangent(y,field,jac):
    y=np.asarray(y,float);f=np.asarray(field,float);J=np.asarray(jac,float)
    x=float(1/(1+np.exp(-y[8])));dx=float(x*(1-x)*f[8])
    accel=J@f
    s=np.array([x,y[2],y[6],f[2],f[6]],float)
    v=np.array([dx,f[2],f[6],accel[2],accel[6]],float)
    return s,v

def ten_chart_and_tangent(y,field):
    y=np.asarray(y,float);f=np.asarray(field,float)
    x=float(1/(1+np.exp(-y[8])));dx=x*(1-x)*float(f[8])
    z=np.r_[y[:8],x,y[9]]
    v=np.r_[f[:8],dx,f[9]]
    return z,v
