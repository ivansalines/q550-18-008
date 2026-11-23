"""Numerical contact-lobe components on a common external-phase interval.

Components refer to strict d3(q)<threshold. A sampled sign change is
refined against the actual dense numerical IVP, not merely an interpolation.
The finite grid cannot rule out unobserved subgrid components.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq
THRESHOLDS=(.0025,.005,.01,.015)
EXTENDED=(.10,.90)
PARENT=(.312500001,.719999999)
def intervals(q,values,threshold,fn=None):
    q=np.asarray(q,dtype=float);v=np.asarray(values,dtype=float)
    if q.ndim!=1 or v.shape!=q.shape or len(q)<3 or not np.all(np.diff(q)>0):
        raise ValueError('Bad monotonic phase profile')
    if not np.all(np.isfinite(v)) or np.min(v)<0:raise ValueError('Nonfinite or negative distance')
    inside=v<threshold
    roots=[]
    for i in range(len(q)-1):
        if inside[i]!=inside[i+1]:
            a,b=float(q[i]),float(q[i+1])
            root=float(brentq(lambda z:(float(fn(z)) if fn is not None else float(np.interp(z,q,v)))-threshold,
                              a,b,xtol=1e-13))
            roots.append(root)
    cuts=[float(q[0]),*roots,float(q[-1])]
    result=[]
    for a,b in zip(cuts[:-1],cuts[1:]):
        mid=(a+b)/2
        if (float(fn(mid)) if fn is not None else float(np.interp(mid,q,v)))<threshold:
            result.append((a,b))
    # A root aligned with an exact sample can introduce a zero-width piece;
    # such degenerate events are deliberately excluded from component counts.
    return [(a,b) for a,b in result if b-a>1e-12]
def analyze(q,v,th,fn):
    spans=intervals(q,v,th,fn)
    return {'threshold':float(th),'component_count':len(spans),
            'intervals':[[float(a),float(b)] for a,b in spans],
            'total_width_q':float(sum(b-a for a,b in spans)),
            'longest_width_q':float(max((b-a for a,b in spans),default=0)),
            'touches_left_boundary':bool(spans and abs(spans[0][0]-q[0])<1e-10),
            'touches_right_boundary':bool(spans and abs(spans[-1][1]-q[-1])<1e-10),
            'gap_between_first_two_q':float(spans[1][0]-spans[0][1]) if len(spans)>=2 else None}
def in_window(q,v,lo,hi,fn,threshold):
    core=np.r_[lo,q[(q>lo)&(q<hi)],hi]
    vals=np.array([float(fn(float(qq))) for qq in core],float)
    return analyze(core,vals,threshold,fn)
def merger_diagnostic(lo,hi):
    """Conservative terminology: observed loss of separation, not topology proof."""
    if lo['component_count']==2 and hi['component_count']==1:
        if (not lo['touches_left_boundary'] and not lo['touches_right_boundary']
            and not hi['touches_left_boundary'] and not hi['touches_right_boundary']):
            return 'INTERIOR_TWO_TO_ONE_NUMERICAL_MERGER'
        return 'AMBIGUOUS_WINDOW_BOUNDARY'
    return 'NO_TWO_TO_ONE_EVENT_IN_PAIR'
def logit_to_x(z):
    z=np.asarray(z,float)
    out=np.empty_like(z)
    pos=z>=0
    out[pos]=1/(1+np.exp(-z[pos]))
    e=np.exp(z[~pos])
    out[~pos]=e/(1+e)
    return out
def shapes(states):
    s=np.asarray(states,float)
    out=np.stack((s[...,0],s[...,4],logit_to_x(s[...,8])),axis=-1)
    return out
