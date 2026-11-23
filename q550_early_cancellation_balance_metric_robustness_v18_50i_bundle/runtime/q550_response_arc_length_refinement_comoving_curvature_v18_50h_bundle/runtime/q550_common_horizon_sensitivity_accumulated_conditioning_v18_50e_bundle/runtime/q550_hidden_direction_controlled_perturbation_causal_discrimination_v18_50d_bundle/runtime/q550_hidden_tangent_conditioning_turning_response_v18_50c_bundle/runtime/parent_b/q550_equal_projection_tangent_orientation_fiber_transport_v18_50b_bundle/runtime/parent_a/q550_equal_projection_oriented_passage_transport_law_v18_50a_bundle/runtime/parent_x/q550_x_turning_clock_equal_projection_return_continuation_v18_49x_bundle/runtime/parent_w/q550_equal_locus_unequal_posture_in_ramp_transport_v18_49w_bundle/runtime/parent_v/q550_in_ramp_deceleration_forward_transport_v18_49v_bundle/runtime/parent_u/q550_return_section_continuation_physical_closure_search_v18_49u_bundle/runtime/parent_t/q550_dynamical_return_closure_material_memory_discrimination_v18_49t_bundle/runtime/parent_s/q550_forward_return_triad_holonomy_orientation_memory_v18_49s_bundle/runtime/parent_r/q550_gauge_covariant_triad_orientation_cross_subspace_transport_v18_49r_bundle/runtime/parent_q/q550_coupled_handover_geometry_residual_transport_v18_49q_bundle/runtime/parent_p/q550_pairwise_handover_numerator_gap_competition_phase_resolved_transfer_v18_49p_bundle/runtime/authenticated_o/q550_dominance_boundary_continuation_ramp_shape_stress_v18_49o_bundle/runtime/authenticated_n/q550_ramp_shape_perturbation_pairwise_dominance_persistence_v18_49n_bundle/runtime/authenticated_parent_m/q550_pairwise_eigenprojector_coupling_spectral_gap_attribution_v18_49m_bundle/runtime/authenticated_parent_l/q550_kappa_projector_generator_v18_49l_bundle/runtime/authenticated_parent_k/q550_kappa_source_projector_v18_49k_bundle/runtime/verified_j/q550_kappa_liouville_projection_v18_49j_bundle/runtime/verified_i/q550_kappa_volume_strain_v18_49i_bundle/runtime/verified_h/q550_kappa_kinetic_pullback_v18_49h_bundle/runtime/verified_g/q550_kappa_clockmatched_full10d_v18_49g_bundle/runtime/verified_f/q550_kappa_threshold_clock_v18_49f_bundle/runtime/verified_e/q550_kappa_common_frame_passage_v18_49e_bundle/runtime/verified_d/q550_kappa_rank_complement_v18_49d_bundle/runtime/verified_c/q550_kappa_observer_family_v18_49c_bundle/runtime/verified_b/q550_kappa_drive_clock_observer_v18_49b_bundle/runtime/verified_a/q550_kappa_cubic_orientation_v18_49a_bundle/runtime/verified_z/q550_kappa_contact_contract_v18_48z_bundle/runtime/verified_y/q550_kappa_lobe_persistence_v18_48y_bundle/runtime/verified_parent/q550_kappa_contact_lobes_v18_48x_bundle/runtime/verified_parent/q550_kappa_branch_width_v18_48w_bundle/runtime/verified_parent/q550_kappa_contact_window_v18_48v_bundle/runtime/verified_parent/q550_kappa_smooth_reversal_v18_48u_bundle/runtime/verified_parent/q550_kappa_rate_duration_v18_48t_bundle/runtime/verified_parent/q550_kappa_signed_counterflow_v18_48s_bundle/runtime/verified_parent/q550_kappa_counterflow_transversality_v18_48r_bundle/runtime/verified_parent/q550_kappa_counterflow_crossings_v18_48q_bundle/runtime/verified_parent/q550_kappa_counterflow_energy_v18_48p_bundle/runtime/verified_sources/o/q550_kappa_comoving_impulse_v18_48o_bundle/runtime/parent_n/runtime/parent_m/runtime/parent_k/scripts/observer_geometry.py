"""Analytic observer-space linear kernels and geodesic width diagnostics.

Angles are intrinsic to the HISTORICAL frozen 10D Euclidean covector chart;
they are not Euclidean angles in an arbitrary anisotropically rescaled chart.
"""
import math
import numpy as np

def unit(x):
    x=np.asarray(x,float);n=float(np.linalg.norm(x))
    if n<1e-30 or not np.isfinite(n):raise ValueError('Zero/nonfinite observer')
    return x/n

def matrices(hb,hc,f,scale):
    """Return linear maps from 10D chart covector to projected Hessian 10D covector.

    B_j = sum_i,a g_i/sc_i H^i_{a j} f_a sc_j (state order 11D).
    """
    sc=np.asarray(scale,float)
    def one(H):return np.einsum('iaj,a,j,i->ji',H[:10,:,:10],f,sc,1/sc,optimize=True)
    return one(hb),one(hc)

def ratio_from_maps(Lb,Lc,g):
    B=Lb@g;C=Lc@g
    nb=float(np.linalg.norm(B));nc=float(np.linalg.norm(C));nt=float(np.linalg.norm(B+C))
    zero=bool(nc<=1e-12*max(nb,1e-30))
    r=1. if zero else (nb+nc)/max(nt,1e-30)
    return r,nb,nc,nt,zero

def log_gradient(Lb,Lc,g):
    B=Lb@g;C=Lc@g;T=B+C
    nb=np.linalg.norm(B);nc=np.linalg.norm(C);nt=np.linalg.norm(T)
    if min(nb,nc,nt)<1e-25:raise ValueError('Unstable log gradient')
    grad=(Lb.T@B/nb+Lc.T@C/nc)/(nb+nc)-(Lb+Lc).T@T/(nt**2)
    return grad

def tangent_to_sphere(g,v):
    v=v-g*np.dot(g,v)
    return unit(v)

def rotate_observer(g,d,angle):
    return g*math.cos(angle)+d*math.sin(angle)

def half_width(Lb,Lc,g,d,target,sign,cutoff=math.radians(45.)):
    """First departure below a threshold, on one signed geodesic arc.

    Uses a geometric scan followed by bisection, not a globally monotone claim.
    """
    base=ratio_from_maps(Lb,Lc,g)[0]
    if not target<base:return math.nan
    trial=np.geomspace(1e-12,cutoff,140)
    hi=None;lo=0.
    for a in trial:
        r=ratio_from_maps(Lb,Lc,rotate_observer(g,d,float(sign*a)))[0]
        if r<target:
            hi=float(a);break
        lo=float(a)
    if hi is None:return math.nan
    for _ in range(56):
        mid=.5*(lo+hi)
        if ratio_from_maps(Lb,Lc,rotate_observer(g,d,sign*mid))[0]>=target:lo=mid
        else:hi=mid
    return math.degrees(.5*(lo+hi))

def principal_direction(Lb,Lc,g):
    d=tangent_to_sphere(g,log_gradient(Lb,Lc,g))
    return d

def width_diagnostics(Lb,Lc,g,d):
    R=ratio_from_maps(Lb,Lc,g)[0]
    target=R/2
    p=half_width(Lb,Lc,g,d,target,1)
    m=half_width(Lb,Lc,g,d,target,-1)
    p10=half_width(Lb,Lc,g,d,10.,1) if R>10 else float('nan')
    m10=half_width(Lb,Lc,g,d,10.,-1) if R>10 else float('nan')
    return (m,p,m+p if math.isfinite(m) and math.isfinite(p) else float('nan'),m10,p10)

def spectral_report(Lb,Lc):
    """Full singular spectra; do not call a tolerance-selected numerical rank 'exact'."""
    A=np.vstack((Lb,Lc));T=Lb+Lc
    s=np.linalg.svd(A,compute_uv=False)
    st=np.linalg.svd(T,compute_uv=False)
    return s,st

def gauge_check(Lb,Lc,g,S):
    """Covariance with BOTH covector metric and observer input-angle metric.

    g'=S^-T g, K'=S^-T K; cometric is S S^T.
    """
    SiT=np.linalg.inv(S.T)
    gp=SiT@g
    Lbp=SiT@Lb@S.T;Lcp=SiT@Lc@S.T
    b=Lbp@gp;c=Lcp@gp
    nb=np.linalg.norm(S.T@b);nc=np.linalg.norm(S.T@c);nt=np.linalg.norm(S.T@(b+c))
    return (nb+nc)/nt
