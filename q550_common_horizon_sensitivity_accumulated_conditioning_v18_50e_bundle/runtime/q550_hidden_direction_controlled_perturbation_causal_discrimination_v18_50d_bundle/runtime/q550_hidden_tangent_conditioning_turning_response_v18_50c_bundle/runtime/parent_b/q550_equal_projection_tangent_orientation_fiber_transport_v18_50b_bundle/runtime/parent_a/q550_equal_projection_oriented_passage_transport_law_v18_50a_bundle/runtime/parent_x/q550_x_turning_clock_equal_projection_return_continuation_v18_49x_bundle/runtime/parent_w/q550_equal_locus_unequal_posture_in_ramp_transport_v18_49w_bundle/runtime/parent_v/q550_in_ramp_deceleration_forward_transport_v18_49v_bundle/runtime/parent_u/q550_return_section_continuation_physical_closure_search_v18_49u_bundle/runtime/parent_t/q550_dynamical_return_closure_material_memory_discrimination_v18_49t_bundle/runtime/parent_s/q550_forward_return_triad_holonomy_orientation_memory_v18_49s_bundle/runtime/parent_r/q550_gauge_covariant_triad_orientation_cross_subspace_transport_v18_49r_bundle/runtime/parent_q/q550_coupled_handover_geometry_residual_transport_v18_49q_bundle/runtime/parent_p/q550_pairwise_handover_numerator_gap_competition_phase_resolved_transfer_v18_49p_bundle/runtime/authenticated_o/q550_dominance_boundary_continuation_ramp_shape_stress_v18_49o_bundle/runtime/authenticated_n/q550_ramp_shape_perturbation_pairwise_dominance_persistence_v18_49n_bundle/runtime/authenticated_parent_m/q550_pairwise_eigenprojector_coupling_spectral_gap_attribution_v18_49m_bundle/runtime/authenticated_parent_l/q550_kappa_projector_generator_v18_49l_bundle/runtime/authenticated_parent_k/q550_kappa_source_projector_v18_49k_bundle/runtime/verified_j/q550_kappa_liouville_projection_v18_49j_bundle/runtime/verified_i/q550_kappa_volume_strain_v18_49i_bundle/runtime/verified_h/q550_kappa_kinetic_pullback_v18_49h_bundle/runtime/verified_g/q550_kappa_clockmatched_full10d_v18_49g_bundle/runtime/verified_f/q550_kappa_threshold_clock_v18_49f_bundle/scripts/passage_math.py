"""Event detection, clock-relative and common-frame orientation diagnostics."""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq,minimize_scalar
from scipy.signal import find_peaks

def critical_points(fun,qgrid,values):
    """Refine ALL discrete 1D extrema so an almost-closed gap is not overlooked."""
    qgrid=np.asarray(qgrid,float);values=np.asarray(values,float)
    candidates=[]
    for sign in (+1,-1):
        ids,_=find_peaks(sign*values)
        for i in ids:
            a=float(qgrid[max(0,i-2)]);b=float(qgrid[min(i+2,len(qgrid)-1)])
            res=minimize_scalar(lambda q:sign*float(fun(q)),bounds=(a,b),method='bounded',options={'xatol':2e-13})
            if res.success:candidates.append((float(res.x),'max' if sign>0 else 'min',float(fun(res.x))))
    return sorted(candidates)

def crossings_from_extrema(fun,qgrid,values,critical,threshold,xtol=1e-12):
    """Sign-bracketed roots with extrema inserted; tangencies are not crossings."""
    cached={float(q):float(v) for q,v in zip(qgrid,values)}
    cached.update({float(x[0]):float(x[2]) for x in critical})
    points=sorted(cached)
    # Insert extrema but do not rely on grid sampling to infer the sign of near-threshold barrier.
    roots=[]
    last_q=None
    for a,b in zip(points[:-1],points[1:]):
        ya=cached[a]-threshold;yb=cached[b]-threshold
        if ya*yb>=0:continue
        q=float(brentq(lambda x:float(fun(x))-threshold,a,b,xtol=xtol))
        if last_q is not None and abs(q-last_q)<1e-9:continue
        h=min(5e-6,(q-float(qgrid[0]))/2,(float(qgrid[-1])-q)/2)
        derivative=(float(fun(q+h))-float(fun(q-h)))/(2*h)
        roots.append({'q':q,'orientation':'entry' if derivative<0 else 'exit',
                      'slope_q':float(derivative),'residual':float(fun(q)-threshold)})
        last_q=q
    return roots

def paired_passages(events):
    pairs=[];entry=None
    for e in events:
        if e['orientation']=='entry':entry=e
        elif e['orientation']=='exit' and entry is not None:
            pairs.append((entry,e));entry=None
    return pairs

def normalized(v):
    v=np.asarray(v,float);n=np.linalg.norm(v)
    if n<1e-13:raise ValueError('Orientation undefined for vanishing hidden vector')
    return v/n

def relative_orientation(a,b):
    x=normalized(a);y=normalized(b)
    return float(np.clip(x@y,-1,1))

def orientation_trace(hidden,q0,q1,samples=25,reference_q=None):
    """Anchor an oriented plane at fixed reference_q and its +q derivative; record leakage.

    The anchor is identical across threshold choices when reference_q is fixed.
    The signed projected angle depends on this declared clock-registered plane.
    """
    q=np.linspace(q0,q1,samples);units=np.array([normalized(hidden(float(t))) for t in q])
    anchor=float(q0 if reference_q is None else reference_q)
    e1=normalized(hidden(anchor))
    hh=min(2e-5,(q1-q0)/50)
    du=normalized(hidden(anchor+hh))-e1
    e2raw=du-e1*(e1@du)
    e2=normalized(e2raw)
    x=units@e1;y=units@e2
    angles=np.unwrap(np.arctan2(y,x))
    leakage=np.sqrt(np.maximum(0,1-x*x-y*y))
    dot=np.clip(np.sum(units[:-1]*units[1:],axis=1),-1,1)
    path_turn=np.arccos(dot).sum()
    return {'entry_exit_cosine':relative_orientation(units[0],units[-1]),
            'entry_exit_angle_deg':float(np.rad2deg(np.arccos(relative_orientation(units[0],units[-1])))),
            'signed_projected_angle_deg':float(np.rad2deg(angles[-1]-angles[0])),
            'projected_angle_max_abs_deg':float(np.rad2deg(np.max(np.abs(angles)))),
            'path_total_turn_deg':float(np.rad2deg(path_turn)),
            'plane_leakage_max':float(np.max(leakage)),
            'plane_leakage_exit':float(leakage[-1])},q,angles,leakage

def covariance_in_common_frame(F,g0,gt,delta):
    import numpy.linalg as la
    pull=la.solve(F,delta)
    pair_err=la.norm(gt@delta-g0@pull)/max(1.,la.norm(gt@delta),la.norm(g0@pull))
    return pull,float(pair_err)
