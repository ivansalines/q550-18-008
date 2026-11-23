"""Independent sampling calculations; the physical IVP is imported from the parent."""
import numpy as np
VEL=(1,3,5,7,9)
CFG=(0,2,4,6,8,10)

def x_from_z(z):
    z=float(z)
    return 1./(1.+np.exp(-z)) if z>=0 else np.exp(z)/(1.+np.exp(z))

def coordinate_gap(y1,y2):
    """Explicit coordinate-based, NOT a physical-distance invariant."""
    a=np.asarray(y1,float); b=np.asarray(y2,float)
    return float(np.linalg.norm(a[[0,4]]-b[[0,4]])),float(np.linalg.norm(a[[2,6]]-b[[2,6]])),abs(x_from_z(a[8])-x_from_z(b[8]))

def poly_sign(s):
    s=np.asarray(s,float)
    if np.any((s<0)|(s>1)):raise ValueError('sigma outside [0,1]')
    return 1.-2*(3*s*s-2*s*s*s)

def speed10(flow):return float(np.linalg.norm(np.asarray(flow,float)[:10]))

def finite_motion(xs):
    """Returns nonnegative incremental path lengths in 10 original state coordinates."""
    x=np.asarray(xs,float)
    if x.ndim!=2 or x.shape[1]<10:raise ValueError('Expected (samples,10+) states')
    return np.r_[0., np.cumsum(np.linalg.norm(np.diff(x[:,:10],axis=0),axis=1))]

def first_sign_transition(x):
    d=np.diff(np.asarray(x,float))
    return bool(np.any(d>0) and np.any(d<0))
