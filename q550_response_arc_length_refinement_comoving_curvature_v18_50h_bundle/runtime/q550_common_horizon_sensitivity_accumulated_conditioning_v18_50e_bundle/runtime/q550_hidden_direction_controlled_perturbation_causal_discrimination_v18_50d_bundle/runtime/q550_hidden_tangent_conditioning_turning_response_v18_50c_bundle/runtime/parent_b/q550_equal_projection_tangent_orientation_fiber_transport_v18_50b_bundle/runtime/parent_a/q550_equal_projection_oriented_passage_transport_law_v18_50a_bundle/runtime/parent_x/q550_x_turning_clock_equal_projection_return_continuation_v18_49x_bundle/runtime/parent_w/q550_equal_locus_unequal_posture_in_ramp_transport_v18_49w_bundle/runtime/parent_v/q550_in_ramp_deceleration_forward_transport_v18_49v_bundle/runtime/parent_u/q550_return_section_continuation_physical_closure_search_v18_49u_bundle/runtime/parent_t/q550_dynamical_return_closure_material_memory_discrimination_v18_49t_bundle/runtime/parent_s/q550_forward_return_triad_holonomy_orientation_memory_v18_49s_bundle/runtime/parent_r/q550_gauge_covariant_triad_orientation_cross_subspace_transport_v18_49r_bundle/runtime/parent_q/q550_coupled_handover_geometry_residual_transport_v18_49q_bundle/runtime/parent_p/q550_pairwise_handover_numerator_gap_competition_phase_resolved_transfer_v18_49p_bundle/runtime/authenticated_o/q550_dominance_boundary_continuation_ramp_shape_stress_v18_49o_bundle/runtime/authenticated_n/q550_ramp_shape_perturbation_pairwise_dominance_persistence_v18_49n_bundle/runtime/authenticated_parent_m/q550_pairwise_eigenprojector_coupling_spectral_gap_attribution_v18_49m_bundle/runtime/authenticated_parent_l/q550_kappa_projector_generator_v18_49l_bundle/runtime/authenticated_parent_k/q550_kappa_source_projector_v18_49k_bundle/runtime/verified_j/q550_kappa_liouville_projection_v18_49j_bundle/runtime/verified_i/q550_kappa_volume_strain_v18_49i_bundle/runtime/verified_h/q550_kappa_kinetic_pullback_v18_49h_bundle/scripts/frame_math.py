"""Linear tangent common-frame transport and oriented marker diagnostics.

The physical variational propagator F transports MATERIAL tangent vectors
on one physical return trajectory; observer rows g(t) obey g(t)F(t)=g(0).
Finite differences between different trajectories are not exact tangent
perturbations; their linear pullback F^-1 delta is a diagnostic, not a nonlinear
material invariant. Metric in common frame is explicitly Euclidean at start.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.linalg import svdvals

def transport_frame(state,kappa,params,slope,jacobian,duration,rtol=2e-10,atol=2e-12,max_step=.0125):
    n=10
    def rhs(t,flattened):
        j=jacobian(state(t)[:11],kappa,params,slope)[:n,:n]
        f=flattened.reshape(n,n)
        return (j@f).ravel()
    solution=solve_ivp(rhs,(0.,duration),np.eye(n).ravel(),method='DOP853',
        rtol=rtol,atol=atol,max_step=max_step,dense_output=True)
    if not solution.success:raise RuntimeError('Frame IVP failed: '+solution.message)
    return lambda t:solution.sol(float(t)).reshape(n,n),solution

def physical_to_initial(f,delta,observers_t=None,observers_initial=None):
    """Return initial-frame material separation; optionally test cotangent duality."""
    pulled=np.linalg.solve(f,np.asarray(delta,float))
    err=None
    if observers_t is not None and observers_initial is not None:
        lhs=np.asarray(observers_t,float)@np.asarray(delta,float)
        rhs=np.asarray(observers_initial,float)@pulled
        err=float(np.linalg.norm(lhs-rhs)/max(1.,np.linalg.norm(lhs),np.linalg.norm(rhs)))
    return pulled,err

def orthonormal_family(rows,rtol=1e-10):
    u,s,vt=np.linalg.svd(np.asarray(rows,float).T,full_matrices=False)
    keep=s>s[0]*rtol
    if not np.any(keep):raise ValueError('No resolved observer rank')
    return u[:,keep],s,int(keep.sum())

def common_decomposition(pulled,U):
    obs=U@(U.T@pulled)
    hidden=pulled-obs
    d=np.linalg.norm(pulled);e=np.linalg.norm(obs);h=np.linalg.norm(hidden)
    return {'total':float(d),'observed':float(e),'hidden':float(h),
            'fraction':float(e/d) if d else 0.,'hidden_vector':hidden,
            'balance_error':float(abs(d*d-e*e-h*h)/max(1.,d*d))}

def oriented_crossings(fun,grid,level=0.,dx=1e-5,xtol=5e-12):
    """Only sign-bracketed, refined crossings; no interpolation-only events."""
    xs=np.asarray(grid,float);values=np.array([float(fun(q))-level for q in xs])
    roots=[]
    for a,b,ya,yb in zip(xs[:-1],xs[1:],values[:-1],values[1:]):
        if ya*yb>=0:continue
        t=float(brentq(lambda x:float(fun(x))-level,float(a),float(b),xtol=xtol))
        d=(float(fun(t+dx))-float(fun(t-dx)))/(2*dx)
        roots.append({'q':t,'orientation':('entry' if d<0 else 'exit') if abs(d)>1e-9 else 'unresolved',
                      'signed_slope':float(d),'residual':float(fun(t)-level)})
    return roots

def passage_pairs(events):
    """Oriented entrance/exit intervals; never treat lobe pair as closed orbit."""
    pairs=[];entry=None
    for event in events:
        if event['orientation']=='entry':entry=event
        elif event['orientation']=='exit' and entry is not None:
            pairs.append({'entry_q':entry['q'],'exit_q':event['q'],'span_q':event['q']-entry['q']})
            entry=None
    return pairs

def compare_orientation(v,w):
    a=np.linalg.norm(v);b=np.linalg.norm(w)
    if a<1e-13 or b<1e-13:return np.nan
    return float(v@w/(a*b))

def gauge_test(f,g0,gt,delta,seed=0):
    """Active chart y'=Sy: material and row covectors transform oppositely."""
    s=np.eye(10)+.07*np.eye(10,k=1)+.035*np.eye(10,k=-1)
    inv=np.linalg.inv(s)
    fp=s@f@inv
    gp=gt@inv
    initialp=g0@inv
    pull=np.linalg.solve(f,delta)
    pullp=np.linalg.solve(fp,s@delta)
    e1=np.linalg.norm(pullp-s@pull)/max(1.,np.linalg.norm(s@pull))
    e2=np.linalg.norm(gp@(s@delta)-gt@delta)/max(1.,np.linalg.norm(gt@delta))
    e3=np.linalg.norm(gp@fp-initialp)/max(1.,np.linalg.norm(initialp))
    return float(max(e1,e2,e3))
