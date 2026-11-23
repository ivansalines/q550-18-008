"""Equal-duration, equal-phase-area, smooth physical command profile variants.

For return ramp duration r, sign(t)=1-2 h(t/r) and
phase_excursion(t)=-t+2*r*integral_0^(t/r) h(s) ds for t in [0,r].
Each shape satisfies h(0)=0,h(1)=1, h'(0)=h'(1)=0,
0<=h<=1, h' >= 0, integral_0^1 h=1/2.
After t=r, phase_excursion=t-r so all registered return phases q agree.
"""
from numpy.polynomial import Polynomial as P
import numpy as np
S=P([0.,1.]);CUBIC=3*S**2-2*S**3
QUINTIC=10*S**3-15*S**4+6*S**5
# Even zero-area correction: weighted second moment exactly 1/7.
# This breaks midpoint time-reversal symmetry while preserving net phase.
BULGE=(S**2)*(1-S)**2*((2*S-1)**2-P([1/7]))
SHAPES=('cubic','quintic','cosine','skew_minus','skew_plus')
_POLYS={'cubic':CUBIC,'quintic':QUINTIC,
        'skew_minus':CUBIC-3*BULGE,'skew_plus':CUBIC+3*BULGE}
_ANTIDERS={k:v.integ() for k,v in _POLYS.items()}

def h(s,kind):
    if kind=='cosine':return .5*(1-np.cos(np.pi*s))
    return _POLYS[kind](s)

def area(s,kind):
    if kind=='cosine':return .5*s-np.sin(np.pi*s)/(2*np.pi)
    return _ANTIDERS[kind](s)

def validate_shapes():
    x=np.linspace(0,1,10001)
    for shape in SHAPES:
        height=h(x,shape);slope=np.diff(height)
        if abs(h(0.,shape))>2e-13 or abs(h(1.,shape)-1)>2e-13:raise AssertionError(shape+' endpoint')
        if abs(area(1.,shape)-.5)>1e-12:raise AssertionError(shape+' phase area')
        if np.min(height)<-1e-11 or np.max(height)>1+1e-11:raise AssertionError(shape+' bounds')
        if np.min(slope)<-1e-11:raise AssertionError(shape+' monotonicity')
    return True

class ShapeClock:
    """Compatible original-ramp adapter: no changes to authenticated physics."""
    def __init__(self,authentic_module):
        self.original=authentic_module
        self.Design=authentic_module.Design
    def cubic_clock_sign(self,t,d):
        if d.ramp<=0:raise ValueError('Ramp must have positive duration')
        if t<=0:return 1.
        if t>=d.ramp:return -1.
        return float(1.-2*h(float(t)/d.ramp,d.kind))
    def cubic_phase_excursion(self,t,d):
        if d.ramp<=0:raise ValueError('Ramp must have positive duration')
        if t<=0:return 0.
        if t>=d.ramp:return float(t-d.ramp)
        return float(-t+2*d.ramp*area(float(t)/d.ramp,d.kind))
    def __getattr__(self,k):return getattr(self.original,k)
