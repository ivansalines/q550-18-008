#!/usr/bin/env python3
"""Prescribed ramp designs and robust one-dimensional phase-contact diagnostics."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import brentq
@dataclass(frozen=True)
class Design:
    name:str
    kind:str
    ramp:float
    dwell:float=0.0
    @property
    def prelude(self):return self.ramp+self.dwell
    @property
    def duration(self):return 1.+self.prelude

# More points around the previously observed short-ramp favorable region.
FULL_RAMPS=(0.,.04,.07,.09,.11,.125,.14,.15,.16,.175,.19,.21,.24,.28,.35,.50,.65)
CONTROL_RAMPS=(0.,.15,.35,.65)
def designs(alpha):
    ramps=FULL_RAMPS if float(alpha)==1.0 else CONTROL_RAMPS
    return [Design(('abrupt' if r==0 else f'cubic_{r:.3f}'),'instant' if r==0 else 'smoothstep',r) for r in ramps]

def cubic_clock_sign(t,d):
    if d.ramp==0:return -1.
    t=float(t)
    if t<=0:return 1.
    if t>=d.ramp:return -1.
    s=t/d.ramp
    return 1.-2*(3*s*s-2*s*s*s)
def cubic_phase_excursion(t,d):
    t=float(t)
    if d.ramp==0:return t
    if t<=0:return 0.
    if t>=d.ramp:return t-d.ramp
    s=t/d.ramp
    return -t+2*d.ramp*(s**3-.5*s**4)
def phase_time(q,d):
    if not 0.<q<1.:raise ValueError('Common-phase q must lie inside (0,1)')
    return d.ramp+float(q)

def subthreshold_intervals(fun,qgrid,th,minq=None,precomputed=None):
    """Refine threshold crossing via scalar root solving, using dense interior probes.

    This is not a global proof of the absence of still narrower crossings.
    Include an explicitly optimized minimum; all other zeros are bracketed by
    original phase samples (no fabricated crossing from dense interpolation).
    """
    q=np.asarray(qgrid,dtype=float)
    if precomputed is not None:
        vv=np.asarray(precomputed,dtype=float)
        if vv.shape!=q.shape:raise ValueError('Invalid cached shape values')
    else:vv=np.array([float(fun(x)) for x in q])
    if minq is None or not q[0]<=minq<=q[-1]:
        xs=q.copy();vals=vv-th
    else:
        xs=np.unique(np.r_[q,float(minq)]);xs.sort()
        vals=np.interp(xs,q,vv)-th
        vals[np.argmin(abs(xs-minq))]=float(fun(minq))-th
    roots=[float(xs[0])]
    for i in range(len(xs)-1):
        if vals[i]*vals[i+1]<0:
            roots.append(float(brentq(lambda x:float(fun(x))-th,float(xs[i]),float(xs[i+1]),xtol=2e-13)))
    roots.append(float(xs[-1]));roots=sorted(set(roots))
    spans=[]
    for a,b in zip(roots[:-1],roots[1:]):
        mid=(a+b)/2
        if float(fun(mid))<th:spans.append((a,b))
    if not spans:return {'threshold':float(th),'number_intervals':0,'longest_phase_width':0.,'total_phase_width':0.,'min_inside':0}
    merged=[]
    for a,b in spans:
        if merged and abs(merged[-1][1]-a)<1e-10:merged[-1]=(merged[-1][0],b)
        else:merged.append((a,b))
    return {'threshold':float(th),'number_intervals':len(merged),
            'longest_phase_width':float(max(b-a for a,b in merged)),
            'total_phase_width':float(sum(b-a for a,b in merged)),
            'min_inside':int(any(a<=minq<=b for a,b in merged)) if minq is not None else None}
