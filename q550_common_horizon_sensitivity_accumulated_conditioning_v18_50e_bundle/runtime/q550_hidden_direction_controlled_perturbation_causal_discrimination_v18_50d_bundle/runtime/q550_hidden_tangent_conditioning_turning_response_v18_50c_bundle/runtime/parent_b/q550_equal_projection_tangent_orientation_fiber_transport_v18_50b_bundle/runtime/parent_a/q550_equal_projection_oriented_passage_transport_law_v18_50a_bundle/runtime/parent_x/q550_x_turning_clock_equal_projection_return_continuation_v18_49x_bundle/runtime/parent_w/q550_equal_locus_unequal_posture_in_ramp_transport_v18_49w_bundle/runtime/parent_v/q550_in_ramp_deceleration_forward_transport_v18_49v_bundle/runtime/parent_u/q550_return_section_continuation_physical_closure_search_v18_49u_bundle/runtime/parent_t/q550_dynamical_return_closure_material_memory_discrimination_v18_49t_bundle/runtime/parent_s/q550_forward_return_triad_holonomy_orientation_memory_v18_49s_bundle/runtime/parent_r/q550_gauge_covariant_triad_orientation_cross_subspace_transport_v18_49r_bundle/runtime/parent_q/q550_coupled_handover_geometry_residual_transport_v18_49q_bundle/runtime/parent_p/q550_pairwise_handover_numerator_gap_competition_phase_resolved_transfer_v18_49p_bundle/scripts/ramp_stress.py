"""Strict equal-area smooth ramp shapes; stress families are explicitly categorized.

h(0)=0,h(1)=1, h'(0)=h'(1)=0 and integral h=1/2. The command
is s(t)=1-2*h(t/r); its clock phase is -t+2*r*int_0^(t/r)h(z)dz.
Beta-mixtures are monotone, recoil controls may be nonmonotone but satisfy
0<=h<=1. These constraints are checked before a physical integration.
"""
import numpy as np
from scipy.special import betainc
from numpy.polynomial import Polynomial as Poly
S=Poly([0,1]);CUBIC=3*S**2-2*S**3
BULGE=S**2*(1-S)**2*((2*S-1)**2-Poly([1/7]))
BBASE=S**2*(1-S)**2

def shape_parts(name):
    a=name.split(':')
    if a[0]=='beta' and len(a)==3:
        x,y=float(a[1]),float(a[2]);
        if min(x,y)<2 or max(x,y)>256:raise ValueError('Beta parameters must be in [2,256]')
        return 'beta',x,y
    if a[0]=='skew' and len(a)==2:return 'skew',float(a[1]),None
    if a[0]=='recoil' and len(a)==3:
        amp=float(a[1]);n=int(a[2]);
        if n not in (1,2,3,4):raise ValueError('Recoil frequencies restricted to 1-4')
        return 'recoil',amp,n
    raise ValueError('Unknown ramp shape '+name)

def incomplete_integral(x,a,b):
    return x*betainc(a,b,x)-(a/(a+b))*betainc(a+1,b,x)

def sinusoidal_integral(x,n):
    """Exact definite integral [0,x] s^2(1-s)^2 sin(2*pi*n*s) ds."""
    k=2*np.pi*n
    x=np.asarray(x);sn=np.sin(k*x);cs=np.cos(k*x)
    I=[(1-cs)/k];J=[sn/k]
    for power in range(1,5):
        I.append(-x**power*cs/k+power*J[-1]/k)
        J.append(x**power*sn/k-power*I[-2]/k)
    return I[2]-2*I[3]+I[4]

def h(x,name):
    k,a,b=shape_parts(name)
    if k=='beta':return .5*(betainc(a,b,x)+betainc(b,a,x))
    if k=='skew':return CUBIC(x)+a*BULGE(x)
    return CUBIC(x)+a*BBASE(x)*np.sin(2*np.pi*b*x)

def area(x,name):
    k,a,b=shape_parts(name)
    if k=='beta':return .5*(incomplete_integral(x,a,b)+incomplete_integral(x,b,a))
    if k=='skew':return CUBIC.integ()(x)+a*BULGE.integ()(x)
    return CUBIC.integ()(x)+a*sinusoidal_integral(x,b)

def properties(name,samples=10001):
    x=np.linspace(0,1,samples);v=h(x,name);delta=np.diff(v)
    result={'shape':name,'end_0':float(h(0.,name)),'end_1':float(h(1.,name)),
       'area_1':float(area(1.,name)),'minimum_h':float(np.min(v)),
       'maximum_h':float(np.max(v)),'minimum_step':float(np.min(delta)),
       'monotone':bool(np.min(delta)>=-1e-11),
       'minimum_clock_rate':float(1-2*np.max(v)),
       'maximum_clock_rate':float(1-2*np.min(v))}
    result['admissible']=(abs(result['end_0'])<1e-10 and abs(result['end_1']-1)<1e-10
       and abs(result['area_1']-.5)<1e-10 and result['minimum_h']>=-1e-10
       and result['maximum_h']<=1+1e-10)
    return result

class ShapeClock:
    def __init__(self,original):self.original=original;self.Design=original.Design
    def cubic_clock_sign(self,t,d):
        if d.ramp<=0:raise ValueError('Positive ramp duration required')
        if t<=0:return 1.
        if t>=d.ramp:return -1.
        return float(1-2*h(t/d.ramp,d.kind))
    def cubic_phase_excursion(self,t,d):
        if d.ramp<=0:raise ValueError('Positive ramp duration required')
        if t<=0:return 0.
        if t>=d.ramp:return float(t-d.ramp)
        return float(-t+2*d.ramp*area(t/d.ramp,d.kind))
    def __getattr__(self,n):return getattr(self.original,n)
