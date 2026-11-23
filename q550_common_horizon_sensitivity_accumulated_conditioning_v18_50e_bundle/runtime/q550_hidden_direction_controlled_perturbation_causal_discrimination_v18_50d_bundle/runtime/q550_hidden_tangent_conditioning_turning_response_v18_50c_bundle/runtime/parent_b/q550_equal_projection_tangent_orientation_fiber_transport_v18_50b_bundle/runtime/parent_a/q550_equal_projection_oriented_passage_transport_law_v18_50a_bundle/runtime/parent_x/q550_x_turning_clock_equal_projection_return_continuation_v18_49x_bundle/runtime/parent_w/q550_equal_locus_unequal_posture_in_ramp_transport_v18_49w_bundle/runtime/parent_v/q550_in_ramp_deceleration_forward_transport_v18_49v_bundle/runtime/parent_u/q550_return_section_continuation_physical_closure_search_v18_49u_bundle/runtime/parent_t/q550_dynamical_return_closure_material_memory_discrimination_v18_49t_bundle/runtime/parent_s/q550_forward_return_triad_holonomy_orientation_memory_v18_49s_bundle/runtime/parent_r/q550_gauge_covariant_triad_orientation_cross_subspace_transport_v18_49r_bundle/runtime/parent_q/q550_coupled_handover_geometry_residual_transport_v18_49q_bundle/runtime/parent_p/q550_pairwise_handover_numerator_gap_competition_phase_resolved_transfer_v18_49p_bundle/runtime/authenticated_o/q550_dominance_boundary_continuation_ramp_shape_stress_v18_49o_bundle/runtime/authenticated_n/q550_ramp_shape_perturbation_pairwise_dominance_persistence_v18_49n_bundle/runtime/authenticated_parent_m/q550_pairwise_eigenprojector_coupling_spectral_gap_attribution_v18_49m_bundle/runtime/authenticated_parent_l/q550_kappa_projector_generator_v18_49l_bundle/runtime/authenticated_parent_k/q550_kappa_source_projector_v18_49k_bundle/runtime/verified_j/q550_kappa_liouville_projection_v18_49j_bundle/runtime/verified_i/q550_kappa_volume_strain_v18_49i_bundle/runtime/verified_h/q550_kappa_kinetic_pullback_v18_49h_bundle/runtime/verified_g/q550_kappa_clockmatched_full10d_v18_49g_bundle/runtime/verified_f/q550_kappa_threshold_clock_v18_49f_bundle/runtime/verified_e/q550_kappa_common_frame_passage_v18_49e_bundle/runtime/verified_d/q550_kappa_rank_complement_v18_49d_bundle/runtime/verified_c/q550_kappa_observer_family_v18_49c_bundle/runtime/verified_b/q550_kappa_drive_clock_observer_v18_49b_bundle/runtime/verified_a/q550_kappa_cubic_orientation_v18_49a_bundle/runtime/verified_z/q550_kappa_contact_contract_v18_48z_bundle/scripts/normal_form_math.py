"""Independent local contact-barrier Taylor-normal-form diagnostics.

The squared-width invariant tends to 1 for any nondegenerate local maximum.
Finite threshold deviations and fitted higher jets are chart/protocol dependent.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import brentq

def fit_jet(q,values,qb,B,window=0.022,degree=4):
    """Fit the *measured* centered profile; constant B fixed by dense-IVP maximum.

    Use scaled coordinates z=(q-qb)/window. The slope is free to expose any
    residual localization error rather than forcing an exact zero derivative.
    """
    q=np.asarray(q,float);v=np.asarray(values,float)
    sel=np.abs(q-qb)<=window+1e-13
    z=(q[sel]-qb)/window
    if len(z)<degree+7:raise ValueError('Insufficient authentic samples for local Taylor fit')
    M=np.column_stack([z**p for p in range(1,degree+1)])
    coeff=np.linalg.lstsq(M,v[sel]-B,rcond=None)[0]
    if not np.all(np.isfinite(coeff)):raise ValueError('Nonfinite fitted jet')
    deriv={k:float(math.factorial(k)*coeff[k-1]/window**k) for k in range(1,degree+1)}
    fit=B+M@coeff
    return {'coeff':coeff,'derivatives':deriv,'max_abs_fit_error':float(np.max(np.abs(v[sel]-fit))),
            'rms_fit_error':float(np.sqrt(np.mean((v[sel]-fit)**2))),'n_samples':len(z)}

def normal_profile(x,B,deriv,degree):
    return B+sum(deriv[k]*x**k/math.factorial(k) for k in range(1,degree+1))

def first_nearby_zero(h, search_width=.03):
    """Find the *first* threshold crossing from the barrier on one side.

    A sublevel lobe is bounded: at a farther endpoint the distance may rise
    above the level again, so bracketing the whole side is mathematically wrong.
    """
    xs=np.linspace(1e-12,search_width,141)
    oldx=xs[0];oldv=h(oldx)
    for x in xs[1:]:
        newv=h(float(x))
        if oldv*newv<=0:
            return float(brentq(h,float(oldx),float(x),xtol=1e-13))
        oldx=float(x);oldv=newv
    raise ValueError('No first local threshold crossing within search domain')

def measured_bracketed_gap(f,qb,delta,search_width=.03):
    """Two nearest roots from true continuous dense-IVP evaluation."""
    B=float(f(qb));threshold=B-delta
    if not 0<delta:raise ValueError('delta must be >0')
    left=first_nearby_zero(lambda x:f(qb-x)-threshold,search_width)
    right=first_nearby_zero(lambda x:f(qb+x)-threshold,search_width)
    return float(left+right),float(qb-left),float(qb+right)

def polynomial_gap(B,deriv,degree,delta,search_width=.02):
    f=lambda x:normal_profile(x,B,deriv,degree)-(B-delta)
    a=first_nearby_zero(lambda x:f(-x),search_width)
    b=first_nearby_zero(f,search_width)
    return float(a+b)

def asymptotic_gaps(delta,curvature,d3=0.,d4=0.):
    """G = 2 sqrt(delta/a) [1+D delta/a + O(delta^2)],
    a=-curvature/2, b=d3/6, c=d4/24,
    D=5 b^2/(8 a^2)+c/(2 a).
    """
    a=-curvature/2.
    if a<=0:raise ValueError('Nonnegative barrier curvature')
    b=d3/6.;c=d4/24.
    s=math.sqrt(delta/a)
    quad=2*s
    correction=5*b*b/(8*a*a)+c/(2*a)
    quartic=quad*(1+correction*s*s)
    return quad,quartic,correction

def contract_ratio(gap,delta,curvature):
    return abs(curvature)*gap**2/(8*delta)

def affine_check(gap,delta,curvature,scale=2.3):
    """The ratio is exactly invariant under affine phase reparameterization."""
    return contract_ratio(scale*gap,delta,curvature/(scale*scale))
