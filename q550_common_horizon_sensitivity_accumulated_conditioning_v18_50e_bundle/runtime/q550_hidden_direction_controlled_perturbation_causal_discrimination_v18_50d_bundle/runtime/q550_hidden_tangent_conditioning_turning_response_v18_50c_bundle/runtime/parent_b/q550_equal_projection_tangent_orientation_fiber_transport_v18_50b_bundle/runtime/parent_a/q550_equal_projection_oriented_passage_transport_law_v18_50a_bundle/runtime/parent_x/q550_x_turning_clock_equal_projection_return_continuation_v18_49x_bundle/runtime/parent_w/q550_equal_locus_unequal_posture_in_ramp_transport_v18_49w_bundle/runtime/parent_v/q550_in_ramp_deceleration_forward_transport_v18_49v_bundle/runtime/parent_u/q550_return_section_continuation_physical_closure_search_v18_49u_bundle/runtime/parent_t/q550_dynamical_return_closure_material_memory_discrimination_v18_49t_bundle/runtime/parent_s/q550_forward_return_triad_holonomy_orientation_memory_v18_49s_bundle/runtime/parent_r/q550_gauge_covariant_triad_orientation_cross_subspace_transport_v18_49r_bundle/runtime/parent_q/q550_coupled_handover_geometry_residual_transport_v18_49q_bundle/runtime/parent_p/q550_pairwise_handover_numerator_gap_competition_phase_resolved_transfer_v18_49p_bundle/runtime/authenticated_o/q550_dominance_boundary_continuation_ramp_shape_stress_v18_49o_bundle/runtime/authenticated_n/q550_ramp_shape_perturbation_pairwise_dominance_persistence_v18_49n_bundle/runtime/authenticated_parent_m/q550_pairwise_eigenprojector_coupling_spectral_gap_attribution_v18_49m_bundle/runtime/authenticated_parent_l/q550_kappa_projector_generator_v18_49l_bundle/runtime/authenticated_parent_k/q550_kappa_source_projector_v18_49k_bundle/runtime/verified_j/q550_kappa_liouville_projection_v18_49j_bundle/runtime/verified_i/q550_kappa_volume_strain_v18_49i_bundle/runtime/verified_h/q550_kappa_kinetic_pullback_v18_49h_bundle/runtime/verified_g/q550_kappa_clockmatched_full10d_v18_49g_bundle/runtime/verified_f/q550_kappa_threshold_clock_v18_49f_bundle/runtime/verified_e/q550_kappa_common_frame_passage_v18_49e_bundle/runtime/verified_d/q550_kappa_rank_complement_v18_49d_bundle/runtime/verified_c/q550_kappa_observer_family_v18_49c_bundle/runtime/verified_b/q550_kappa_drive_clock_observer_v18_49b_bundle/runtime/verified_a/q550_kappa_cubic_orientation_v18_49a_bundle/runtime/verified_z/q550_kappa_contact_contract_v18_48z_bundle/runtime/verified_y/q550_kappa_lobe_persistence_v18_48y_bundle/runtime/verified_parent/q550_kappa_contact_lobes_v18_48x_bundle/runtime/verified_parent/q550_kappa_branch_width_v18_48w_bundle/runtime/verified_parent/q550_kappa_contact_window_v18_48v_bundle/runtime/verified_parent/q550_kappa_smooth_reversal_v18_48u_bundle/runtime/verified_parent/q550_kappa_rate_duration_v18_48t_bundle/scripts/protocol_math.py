#!/usr/bin/env python3
"""Pure controls for rate-duration, partial velocity reversal and phase persistence.

Names `rate`, `duration`, and `alpha` refer to independent *imposed* controls,
not inferred intrinsic quantities of the autonomous Q550 field.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from scipy.optimize import minimize_scalar
MATERIAL_VELOCITY_INDICES=(1,3,5,7,9)
@dataclass(frozen=True)
class Design:
    name:str
    rate:float
    duration:float

def designs():
    # 7 unique controls. Three constant-total-phase (a=1), plus 2 fixed
    # duration variations and 2 fixed rate variations around rate=duration=1.
    return (Design('phaseclosed_slow',.75,4./3.),
            Design('phaseclosed_reference',1.,1.),
            Design('phaseclosed_fast',1.25,.8),
            Design('durationfixed_slow',.75,1.),
            Design('durationfixed_fast',1.25,1.),
            Design('ratefixed_short',1.,.8),
            Design('ratefixed_long',1.,1.2))

def initial_velocity_scale(alpha):
    if not (0<=alpha<=1):raise ValueError('alpha must be in [0,1]')
    return 1.-2.*alpha

def prepare_reversal(y_turn,alpha):
    new=np.asarray(y_turn,float).copy()
    new[list(MATERIAL_VELOCITY_INDICES)]*=initial_velocity_scale(alpha)
    return new

def common_phase_domain(controls,umin=.25,umax=.96,forward_low=.04,forward_high=.75):
    """Common q=a*u, s=1-q domain for EVERY declared design."""
    lows=[];highs=[]
    for d in controls:
        a=d.rate*d.duration
        lows.append(max(a*umin,1.-forward_high))
        highs.append(min(a*umax,1.-forward_low))
    lo=max(lows);hi=min(highs)
    if not lo<hi:raise ValueError('There is no common nontrivial phase interval')
    return lo,hi

def shape_gap(f,r,geometry,u,a):
    s=1.-a*u
    return np.asarray(geometry.shape(r(u)[:11])-geometry.shape(f(s)[:11]),float)

def minimum_on_shared_clock(f,r,geometry,d,umin=.25,umax=.96,forward_low=.04,forward_high=.75,nodes=141):
    a=d.rate*d.duration
    lo=max(umin,(1.-forward_high)/a);hi=min(umax,(1.-forward_low)/a)
    if not lo<hi:raise ValueError('No usable same-phase contact domain')
    ts=np.linspace(lo,hi,nodes)
    ds=np.linalg.norm(geometry.shape(r(ts)[...,:11])-geometry.shape(f(1.-a*ts)[...,:11]),axis=-1)
    candidates=[(float(ds[0]),float(ts[0])),(float(ds[-1]),float(ts[-1]))]
    for i in range(1,len(ts)-1):
        if ds[i]<=ds[i-1] and ds[i]<=ds[i+1]:
            res=minimize_scalar(lambda u:float(np.linalg.norm(shape_gap(f,r,geometry,u,a))),
                 method='bounded',bounds=(float(ts[i-1]),float(ts[i+1])),options={'xatol':1e-12})
            candidates.append((float(res.fun),float(res.x)))
    dist,u=min(candidates,key=lambda v:v[0])
    return {'gap':dist,'u':u,'s':float(1.-a*u),'q':float(a*u),
      'interior':bool(lo+1e-6<u<hi-1e-6),'domain_lo_u':lo,'domain_hi_u':hi,
      'number_local_candidates':len(candidates)-2}

def contiguous_phase_support(q,flags):
    """Maximum interval between consecutive TRUE samples, in phase units."""
    q=np.asarray(q,float);flags=np.asarray(flags,bool)
    if len(q)!=len(flags) or len(q)<2:raise ValueError('Invalid common q samples')
    dx=0.;run=0.
    for i in range(len(q)-1):
        if flags[i] and flags[i+1]:
            run+=float(q[i+1]-q[i]);dx=max(dx,run)
        else:run=0.
    return dx

def sample_persistence(q,distances,threshold):
    d=np.asarray(distances,float)
    if len(d)!=len(q):raise ValueError('q and distance dimensions do not match')
    mask=d<=threshold
    return {'count':int(mask.sum()),'fraction':float(mask.mean()),
      'max_contiguous_phase_width':contiguous_phase_support(q,mask)}

def signed_power_opposition(a,b,eps=1e-13):
    """0 marks numerically unresolved signs, not opposite signed powers."""
    if abs(a)<=eps or abs(b)<=eps:return 0
    return int(a*b<0)
