#!/usr/bin/env python3
"""Analytic control laws for smooth external-phase reversal in Q550 v18.48u.

All profiles start at the historical positive clock speed, then brake and
reverse to the common negative clock speed. The constant negative control is
a deliberately discontinuous reference. Every smooth prelude has zero signed
phase integral, so post-prelude clock and rate are exactly comparable to the
instant reference at the same unwrapped phase q>0.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Design:
    name: str
    kind: str
    ramp: float
    dwell: float = 0.
    @property
    def prelude(self):return self.ramp+self.dwell
    @property
    def duration(self):return self.prelude+1.

def designs():
    return (
      Design('instant','instant',0.),
      Design('smooth_short','smoothstep',.15),
      Design('smooth_medium','smoothstep',.35),
      Design('smooth_long','smoothstep',.65),
      Design('smoother_medium','smootherstep',.35),
      Design('stop_dwell','stop',.35,.15))

def smoothstep(s):return s*s*(3.-2.*s)
def smootherstep(s):return s*s*s*(10.-15.*s+6.*s*s)

def clock_sign(t,d):
    """dTheta/dxi = omega * clock_sign; chronological xi, not reversed time."""
    t=float(t)
    if d.kind=='instant':return -1.
    if t<=0:return 1.
    if t>=d.prelude:return -1.
    if d.kind in ('smoothstep','smootherstep'):
        s=min(1.,max(0.,t/d.ramp))
        f=smoothstep(s) if d.kind=='smoothstep' else smootherstep(s)
        return 1.-2.*f
    if d.kind=='stop':
        half=d.ramp/2.
        if t<half:return 1.-smoothstep(t/half)
        if t<half+d.dwell:return 0.
        return -smoothstep((t-half-d.dwell)/half)
    raise ValueError('Unknown control kind: '+d.kind)

def phase_excursion(t,d):
    """q(t)=-integral_0^t clock_sign(s) ds, analytic, unwrapped.

    A smooth phase initially moves FORWARD (q<0), then turns and reaches
    q=0 at prelude; after it, q=t-prelude, monotonic and positive.
    """
    t=float(t)
    if d.kind=='instant':return t
    if t<=0:return 0.
    if t>=d.prelude:return t-d.prelude
    if d.kind in ('smoothstep','smootherstep'):
        s=t/d.ramp
        # Primitive for 3s^2-2s^3: s^3 - 1/2 s^4.
        # Primitive for 10s^3-15s^4+6s^5: (5/2)s^4-3s^5+s^6.
        integral=(s**3-.5*s**4) if d.kind=='smoothstep' else (2.5*s**4-3*s**5+s**6)
        return -t+2*d.ramp*integral
    if d.kind=='stop':
        half=d.ramp/2.
        if t<=half:
            s=t/half
            return -t+half*(s**3-.5*s**4)
        if t<=half+d.dwell:
            return -half/2.
        z=t-half-d.dwell;s=z/half
        return -half/2.+half*(s**3-.5*s**4)
    raise ValueError('Unknown control kind')

def same_phase_time(q,d):
    """Unique post-reversal crossing of matched q>0."""
    if q<=0 or q>=1:raise ValueError('Matched phase must lie inside (0,1)')
    return d.prelude+float(q)

MATERIAL_VELOCITY_INDICES=(1,3,5,7,9)
def prepare_reversal(y,alpha):
    if not 0<=alpha<=1:raise ValueError('alpha out of [0,1]')
    v=np.asarray(y,float).copy()
    v[list(MATERIAL_VELOCITY_INDICES)]*=1.-2.*alpha
    return v

def signed_power_opposition(a,b,eps=1e-13):
    return int(abs(a)>eps and abs(b)>eps and a*b<0)


def width_under_threshold(q,d,threshold):
    q=np.asarray(q,float);d=np.asarray(d,float)
    flag=d<threshold
    diffs=np.diff(q)
    run=0.;longest=0.
    for i in range(len(diffs)):
        if flag[i] and flag[i+1]:
            run+=float(diffs[i]);longest=max(longest,run)
        else:run=0.
    return {'fraction':float(flag.mean()),'longest_q_span':longest}
