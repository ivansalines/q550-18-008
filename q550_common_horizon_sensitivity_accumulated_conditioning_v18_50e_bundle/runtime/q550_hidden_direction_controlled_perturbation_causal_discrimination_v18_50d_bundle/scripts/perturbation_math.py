"""Small, explicit interventions. All quantities are in the original model's chart."""
import numpy as np

def pulse(t,t0,t1,amp):
    """Perturb clock phase by a compact C1 sin^2 bump: zero at both ends."""
    if not t0<t1:raise ValueError('Nonpositive pulse duration')
    if t<=t0 or t>=t1:return 0.,0.
    s=(t-t0)/(t1-t0)
    phase=amp*(t1-t0)/(2*np.pi)*np.sin(np.pi*s)**2
    derivative=amp*.5*np.sin(2*np.pi*s)
    return float(phase),float(derivative)

def unit(v,scale):
    a=np.asarray(v,dtype=float)/np.asarray(scale,dtype=float)
    n=np.linalg.norm(a)
    if n<1e-12 or not np.isfinite(n):raise ValueError('Invalid hidden tangent')
    return a/n

def centered(u0,up,um,eps):
    return (np.asarray(up)-np.asarray(um))/(2*eps)

def direction_angle(u,v):
    return float(np.degrees(np.arccos(np.clip(np.dot(u,v),-1.,1.))))
