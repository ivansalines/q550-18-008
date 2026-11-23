"""Declared local ramp refinements and branch-resolved, signed diagnostics."""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import minimize_scalar
RAMP_CENTERS={('phaseblind',0):.28,('phaseblind',1):.07,('phasecov',0):.04,('phasecov',1):.35}
OFFSETS=(-.02,-.015,-.01,-.005,.005,.01,.015,.02)
THRESHOLDS=(.0025,.005,.01)
FIXED_PHASES=(.35,.50,.65)
def branch_key(family):
    if family.startswith('phaseblind'):return 'phaseblind'
    if family.startswith('phasecov'):return 'phasecov'
    raise ValueError('Unexpected original family: '+family)
def refinements(family,branch):
    center=RAMP_CENTERS[(branch_key(family),int(branch))]
    offsets=tuple((.018 if off==.02 else off) for off in OFFSETS) if (branch_key(family),int(branch))==('phaseblind',1) else OFFSETS
    return tuple(round(center+off,8) for off in offsets)
def sign_of(value,tol=1e-12):
    if not math.isfinite(value):raise ValueError('Non-finite signed work')
    return 1 if value>tol else (-1 if value<-tol else 0)
def sign_transitions(rows,key,sign_key):
    """Sign-change brackets only, not interpolated/verified zeros."""
    p=sorted((float(x[key]),float(x[sign_key])) for x in rows)
    found=[]
    for (a,fa),(b,fb) in zip(p[:-1],p[1:]):
        if sign_of(fa)*sign_of(fb)<0:
            found.append({'ramp_left_xi':a,'ramp_right_xi':b,'work_left':fa,'work_right':fb})
    return found
def differences(gaps,fulls):
    z=np.array(gaps,float);t=np.array(fulls,float)
    if len(z)==0 or len(z)!=len(t) or np.any(z<0) or np.any(t<0):raise ValueError('Bad contact gap arrays')
    return {'median_3D':float(np.median(z)),'median_11D':float(np.median(t)),'smallest_3D':float(z.min())}
def phase_minimum(fun,qgrid,cached):
    """Reuse parent's bounded searches; only local minima of sampled q-grid."""
    q=np.asarray(qgrid,float);g=np.asarray(cached,float)
    pairs=[(float(g[0]),float(q[0])),(float(g[-1]),float(q[-1]))]
    for i in range(1,len(q)-1):
        if g[i]<=g[i-1] and g[i]<=g[i+1]:
            res=minimize_scalar(fun,method='bounded',bounds=(float(q[i-1]),float(q[i+1])),options={'xatol':1e-12})
            pairs.append((float(res.fun),float(res.x)))
    return min(pairs)
