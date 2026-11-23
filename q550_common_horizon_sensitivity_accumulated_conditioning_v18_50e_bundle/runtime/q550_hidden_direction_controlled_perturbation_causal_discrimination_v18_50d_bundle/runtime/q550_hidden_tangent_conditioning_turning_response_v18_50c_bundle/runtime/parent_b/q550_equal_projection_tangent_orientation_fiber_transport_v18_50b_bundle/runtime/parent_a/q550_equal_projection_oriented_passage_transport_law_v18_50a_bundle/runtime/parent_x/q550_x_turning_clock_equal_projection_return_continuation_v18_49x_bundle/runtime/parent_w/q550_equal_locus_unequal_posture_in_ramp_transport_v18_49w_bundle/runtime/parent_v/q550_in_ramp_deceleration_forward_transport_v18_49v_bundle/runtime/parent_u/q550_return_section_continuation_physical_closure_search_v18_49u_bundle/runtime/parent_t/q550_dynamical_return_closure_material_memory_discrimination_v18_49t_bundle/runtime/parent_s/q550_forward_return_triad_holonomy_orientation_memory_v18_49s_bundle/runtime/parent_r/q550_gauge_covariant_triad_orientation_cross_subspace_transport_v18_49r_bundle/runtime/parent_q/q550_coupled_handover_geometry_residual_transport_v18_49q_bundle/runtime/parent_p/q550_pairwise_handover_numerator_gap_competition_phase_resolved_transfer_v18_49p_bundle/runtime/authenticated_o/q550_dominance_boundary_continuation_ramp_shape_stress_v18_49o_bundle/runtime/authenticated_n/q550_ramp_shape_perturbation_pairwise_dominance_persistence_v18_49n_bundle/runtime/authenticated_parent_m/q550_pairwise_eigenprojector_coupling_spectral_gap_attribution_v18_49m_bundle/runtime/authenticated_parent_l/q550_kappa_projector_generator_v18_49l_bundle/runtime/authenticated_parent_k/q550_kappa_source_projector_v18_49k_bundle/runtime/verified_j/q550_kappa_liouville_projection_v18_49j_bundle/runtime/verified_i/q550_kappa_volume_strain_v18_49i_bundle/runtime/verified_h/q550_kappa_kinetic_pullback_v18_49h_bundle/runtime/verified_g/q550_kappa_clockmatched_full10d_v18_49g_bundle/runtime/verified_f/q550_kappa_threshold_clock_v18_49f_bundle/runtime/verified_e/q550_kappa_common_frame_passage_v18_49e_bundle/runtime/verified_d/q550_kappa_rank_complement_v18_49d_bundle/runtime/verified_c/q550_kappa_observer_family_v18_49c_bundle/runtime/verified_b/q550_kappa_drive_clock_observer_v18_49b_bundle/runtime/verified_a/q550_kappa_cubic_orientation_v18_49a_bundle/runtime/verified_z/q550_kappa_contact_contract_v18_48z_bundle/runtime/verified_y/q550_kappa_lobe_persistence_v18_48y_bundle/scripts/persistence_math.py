"""Independent finite-threshold contact geometry; never a topology certificate."""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq, minimize_scalar

def sample_curvature(f,q,h):
    # Symmetric second difference of actual continuous dense-IVP gap.
    return (f(q+h)-2*f(q)+f(q-h))/(h*h)

def barrier(f, bracket=(.465,.505), steps=(.002,.001,.0005,.00025)):
    sol=minimize_scalar(lambda q:-float(f(q)),bounds=bracket,method='bounded',
                        options={'xatol':1e-13})
    if not sol.success or abs(sol.x-bracket[0])<1e-4 or abs(sol.x-bracket[1])<1e-4:
        raise RuntimeError('Interior inter-lobe barrier has not been resolved')
    x=float(sol.x); b=float(f(x))
    cs=np.array([sample_curvature(f,x,h) for h in steps],float)
    # Richardson error: h and h/2 agree at O(h^2) in a smooth region.
    extrap=(4*cs[-1]-cs[-2])/3
    stability=abs(cs[-1]-cs[-2])/max(1.,abs(extrap))
    return {'q':x,'distance':b,'curvatures':cs.tolist(),
            'curvature_richardson':float(extrap),'curvature_step_variation':float(stability),
            'is_strict_local_max':bool(np.all(cs<0))}

def minimum(f,bracket):
    sol=minimize_scalar(f,bounds=bracket,method='bounded',options={'xatol':1e-12})
    if not sol.success:return None
    return {'q':float(sol.x),'distance':float(sol.fun)}

def root_intervals(qs, ys, threshold, f):
    qs=np.asarray(qs,float);ys=np.asarray(ys,float)
    roots=[]
    s=ys-threshold
    for i in range(len(qs)-1):
        if s[i]*s[i+1]<0:
            roots.append(float(brentq(lambda q:f(q)-threshold,float(qs[i]),float(qs[i+1]),xtol=1e-12)))
    cuts=[float(qs[0]),*roots,float(qs[-1])]
    spans=[(a,b) for a,b in zip(cuts[:-1],cuts[1:]) if b-a>1e-12 and f((a+b)/2)<threshold]
    return spans

def critical_bracket(rows, threshold):
    rows=sorted(rows,key=lambda a:a['ramp_duration_xi'])
    for l,r in zip(rows[:-1],rows[1:]):
        if l['barrier_distance_3D']>=threshold>r['barrier_distance_3D']:
            return {'threshold':float(threshold),'left_ramp':float(l['ramp_duration_xi']),
                    'right_ramp':float(r['ramp_duration_xi']),
                    'left_barrier':float(l['barrier_distance_3D']),
                    'right_barrier':float(r['barrier_distance_3D'])}
    return None
