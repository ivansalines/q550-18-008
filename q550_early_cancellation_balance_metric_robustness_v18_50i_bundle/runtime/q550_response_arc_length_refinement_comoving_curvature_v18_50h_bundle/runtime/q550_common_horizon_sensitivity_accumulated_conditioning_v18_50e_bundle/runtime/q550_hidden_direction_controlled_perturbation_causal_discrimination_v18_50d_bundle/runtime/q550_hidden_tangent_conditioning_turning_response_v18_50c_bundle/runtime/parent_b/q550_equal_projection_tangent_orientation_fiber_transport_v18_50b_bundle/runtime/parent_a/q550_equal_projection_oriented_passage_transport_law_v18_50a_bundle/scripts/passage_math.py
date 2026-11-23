"""Signed projected passage area and tests; no claim of physical spatial area."""
import numpy as np
from scipy.integrate import simpson

def integrate_passage(time,x,theta,x_level):
    time=np.asarray(time,float);x=np.asarray(x,float);theta=np.asarray(theta,float)
    if len(time)<5 or len(time)%2!=1 or not np.all(np.diff(time)>0):raise ValueError('Need odd increasing time grid')
    if not (np.isfinite(x).all() and np.isfinite(theta).all()):raise ValueError('Nonfinite signal')
    # Closed by the vertical connector at x=x_level; its contribution is exactly zero.
    return float(simpson((x-x_level)*np.gradient(theta,time,edge_order=2),x=time))

def integrate_rates(time,x,theta_rate,x_level):
    time=np.asarray(time,float);x=np.asarray(x,float);theta_rate=np.asarray(theta_rate,float)
    return float(simpson((x-x_level)*theta_rate,x=time))

def signed_polyline_area(x,theta,x_level):
    """Exact polygonal line-integral in (x,theta) closed at x=x_level."""
    x=np.asarray(x);theta=np.asarray(theta)
    return float(np.sum(((x[:-1]+x[1:])/2-x_level)*np.diff(theta)))

def projector_gap(P,Q):
    a,b=np.asarray(P,float),np.asarray(Q,float)
    return float(np.linalg.norm(a-b,'fro'))

def transversality(left_rate,right_rate,tol=1e-12):
    if abs(left_rate)<tol or abs(right_rate)<tol:return 'grazing_or_unresolved'
    if left_rate*right_rate<0:return 'opposed'
    return 'same_direction'
