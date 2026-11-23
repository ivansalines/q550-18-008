#!/usr/bin/env python3
"""Independent geometric calculations for 3D near-passes and 2D projection crossings.

All angles are computed in declared chart coordinates; a projected crossing is
not a full-state intersection. The orientation of the tangent lines is distinct
from chronological direction of physical flow.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import minimize_scalar,least_squares

def wrap(t):return (np.asarray(t)+np.pi)%(2*np.pi)-np.pi

def shape(y):
    y=np.asarray(y,float)
    z=y[...,8]
    x=np.where(z>=0,1./(1.+np.exp(-np.clip(z,-700,700))),
               np.exp(np.clip(z,-700,700))/(1.+np.exp(np.clip(z,-700,700))))
    return np.stack((y[...,0],y[...,4],x),axis=-1)

def shape_tangent(y,f):
    z=shape(y);f=np.asarray(f,float)
    return np.stack((f[...,0],f[...,4],z[...,2]*(1-z[...,2])*f[...,8]),axis=-1)

def tangent_angles(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    na=np.linalg.norm(a);nb=np.linalg.norm(b)
    if min(na,nb)<1e-14:return dict(chronic_angle_deg=float('nan'),line_angle_deg=float('nan'),sin_3d=float('nan'),cross_norm=0.)
    cos=np.clip(np.dot(a,b)/(na*nb),-1.,1.)
    cross=np.linalg.norm(np.cross(a,b))
    return dict(chronic_angle_deg=float(np.degrees(np.arccos(cos))),
                line_angle_deg=float(np.degrees(np.arccos(abs(cos)))),
                sin_3d=float(cross/(na*nb)),cross_norm=float(cross))

def phase_locked_forward_progress(u,drive_rate,duration):
    """Same unwrapped external Θ phase; only valid for a single <2π excursion."""
    return 1.-drive_rate*duration*np.asarray(u,float)

def phase_locked_bounds(rate,duration,urange=(.25,.96),srange=(.04,.75)):
    a=rate*duration
    if a<=0:raise ValueError('Positive drive rate/duration required')
    return max(urange[0],(1-srange[1])/a),min(urange[1],(1-srange[0])/a)

def phase_locked_min(fwd,rev,rate,duration,umin=.25,umax=.96):
    lo,hi=phase_locked_bounds(rate,duration,urange=(umin,umax))
    if lo>=hi:return None
    grid=np.linspace(lo,hi,421)
    s=phase_locked_forward_progress(grid,rate,duration)
    ds=np.linalg.norm(shape(rev(grid))-shape(fwd(s)),axis=1)
    cand=[(float(ds[0]),float(grid[0])),(float(ds[-1]),float(grid[-1]))]
    for i in range(1,len(grid)-1):
        if ds[i]<=ds[i-1] and ds[i]<=ds[i+1]:
            x=minimize_scalar(lambda u:float(np.linalg.norm(shape(rev(u))-shape(fwd(1-rate*duration*u)))),
                    bounds=(grid[i-1],grid[i+1]),method='bounded',options={'xatol':1e-13})
            cand.append((float(x.fun),float(x.x)))
    distance,u=min(cand,key=lambda q:q[0]);s=float(phase_locked_forward_progress(u,rate,duration))
    return {'u':u,'s':s,'distance':distance,'interior':bool(lo+1e-6<u<hi-1e-6),
            'lo':lo,'hi':hi,'local_minima_count':len(cand)-2}

def segment_cross_candidates(r,f):
    """Find exact 2D intersections of sampled CHORD segments; follow with IVP refinement.
    r/f are (number_of_nodes,2). Returned fractions lie in [0,1].
    Parallel/collinear segments are excluded, not declared nonintersecting.
    """
    r=np.asarray(r,float);f=np.asarray(f,float)
    A=r[:-1,None,:];D=(r[1:]-r[:-1])[:,None,:]
    B=f[None,:-1,:];E=(f[1:]-f[:-1])[None,:,:]
    cross=lambda x,y:x[...,0]*y[...,1]-x[...,1]*y[...,0]
    denominator=cross(D,E)
    sep=B-A
    nonparallel=np.abs(denominator)>1e-15
    frac_r=np.divide(cross(sep,E),denominator,out=np.full_like(denominator,np.nan),where=nonparallel)
    frac_f=np.divide(cross(sep,D),denominator,out=np.full_like(denominator,np.nan),where=nonparallel)
    yes=nonparallel&(frac_r>=0)&(frac_r<=1)&(frac_f>=0)&(frac_f<=1)
    return [(int(i),int(j),float(frac_r[i,j]),float(frac_f[i,j])) for i,j in zip(*np.where(yes))]

def refine_2d_crossing(fwd,rev,rhs_forward,rhs_reverse,u,s,axes,urange=(.25,.96),srange=(.04,.75)):
    axes=np.asarray(axes,dtype=int)
    def fun(t):return (shape(rev(t[0]))-shape(fwd(t[1])))[axes]
    def jac(t):
        ar=shape_tangent(rev(t[0]),rhs_reverse(rev(t[0])))
        af=shape_tangent(fwd(t[1]),rhs_forward(fwd(t[1])))
        return np.column_stack((ar[axes],-af[axes]))
    ans=least_squares(fun,[u,s],jac=jac,bounds=([urange[0],srange[0]],
                       [urange[1],srange[1]]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=50)
    return dict(u=float(ans.x[0]),s=float(ans.x[1]),residual=float(np.linalg.norm(fun(ans.x))),
                jacobian_det=float(np.linalg.det(jac(ans.x))),success=bool(ans.success))
