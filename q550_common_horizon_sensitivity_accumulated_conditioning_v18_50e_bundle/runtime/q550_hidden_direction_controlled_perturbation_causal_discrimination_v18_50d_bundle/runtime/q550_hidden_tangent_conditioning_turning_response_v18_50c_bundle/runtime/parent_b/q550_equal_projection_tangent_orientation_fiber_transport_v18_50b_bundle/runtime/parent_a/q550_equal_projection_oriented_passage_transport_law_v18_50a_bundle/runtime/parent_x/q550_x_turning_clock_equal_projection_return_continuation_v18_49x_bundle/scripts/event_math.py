"""Event-based roots and observables for Q550 v18.49x; solver-independent mathematical core."""
import numpy as np
from scipy.optimize import brentq

def logistic(z):
    z=float(z)
    return float(1/(1+np.exp(-z))) if z>=0 else float(np.exp(z)/(1+np.exp(z)))

def scan_sign_roots(fun,a,b,points=129,xtol=5e-13):
    if points<3 or b<=a:raise ValueError('Bad scanning interval')
    tt=np.linspace(a,b,int(points));vv=[float(fun(t)) for t in tt]
    if not all(np.isfinite(vv)):raise ValueError('Non-finite diagnostic function')
    ans=[]
    for j in range(len(tt)-1):
        l,h=float(tt[j]),float(tt[j+1]);u,v=vv[j:j+2]
        if u==0:ans.append(l)
        if u*v<0:ans.append(float(brentq(fun,l,h,xtol=xtol)))
    if vv[-1]==0:ans.append(float(tt[-1]))
    return [float(t) for i,t in enumerate(sorted(ans)) if i==0 or t-sorted(ans)[i-1]>max(xtol*10,1e-11)]

def classify_turn(dx,t,tbound):
    h=max(1e-8,min(2e-5*(tbound[1]-tbound[0]),(t-tbound[0])*.3,(tbound[1]-t)*.3))
    if t-h<=tbound[0] or t+h>=tbound[1]:return 'boundary'
    a,b=dx(t-h),dx(t+h)
    if a>0 and b<0:return 'maximum'
    if a<0 and b>0:return 'minimum'
    return 'other'

def turns_to_degrees(R):
    co=np.clip((np.trace(R)-1)/2,-1,1)
    return float(np.degrees(np.arccos(co)))

def matched_locus(state_a,state_b,spans):
    a=np.asarray([state_a[0],state_a[4],logistic(state_a[8])]);b=np.asarray([state_b[0],state_b[4],logistic(state_b[8])])
    return float(np.linalg.norm((b-a)/np.maximum(spans,1e-12)))
