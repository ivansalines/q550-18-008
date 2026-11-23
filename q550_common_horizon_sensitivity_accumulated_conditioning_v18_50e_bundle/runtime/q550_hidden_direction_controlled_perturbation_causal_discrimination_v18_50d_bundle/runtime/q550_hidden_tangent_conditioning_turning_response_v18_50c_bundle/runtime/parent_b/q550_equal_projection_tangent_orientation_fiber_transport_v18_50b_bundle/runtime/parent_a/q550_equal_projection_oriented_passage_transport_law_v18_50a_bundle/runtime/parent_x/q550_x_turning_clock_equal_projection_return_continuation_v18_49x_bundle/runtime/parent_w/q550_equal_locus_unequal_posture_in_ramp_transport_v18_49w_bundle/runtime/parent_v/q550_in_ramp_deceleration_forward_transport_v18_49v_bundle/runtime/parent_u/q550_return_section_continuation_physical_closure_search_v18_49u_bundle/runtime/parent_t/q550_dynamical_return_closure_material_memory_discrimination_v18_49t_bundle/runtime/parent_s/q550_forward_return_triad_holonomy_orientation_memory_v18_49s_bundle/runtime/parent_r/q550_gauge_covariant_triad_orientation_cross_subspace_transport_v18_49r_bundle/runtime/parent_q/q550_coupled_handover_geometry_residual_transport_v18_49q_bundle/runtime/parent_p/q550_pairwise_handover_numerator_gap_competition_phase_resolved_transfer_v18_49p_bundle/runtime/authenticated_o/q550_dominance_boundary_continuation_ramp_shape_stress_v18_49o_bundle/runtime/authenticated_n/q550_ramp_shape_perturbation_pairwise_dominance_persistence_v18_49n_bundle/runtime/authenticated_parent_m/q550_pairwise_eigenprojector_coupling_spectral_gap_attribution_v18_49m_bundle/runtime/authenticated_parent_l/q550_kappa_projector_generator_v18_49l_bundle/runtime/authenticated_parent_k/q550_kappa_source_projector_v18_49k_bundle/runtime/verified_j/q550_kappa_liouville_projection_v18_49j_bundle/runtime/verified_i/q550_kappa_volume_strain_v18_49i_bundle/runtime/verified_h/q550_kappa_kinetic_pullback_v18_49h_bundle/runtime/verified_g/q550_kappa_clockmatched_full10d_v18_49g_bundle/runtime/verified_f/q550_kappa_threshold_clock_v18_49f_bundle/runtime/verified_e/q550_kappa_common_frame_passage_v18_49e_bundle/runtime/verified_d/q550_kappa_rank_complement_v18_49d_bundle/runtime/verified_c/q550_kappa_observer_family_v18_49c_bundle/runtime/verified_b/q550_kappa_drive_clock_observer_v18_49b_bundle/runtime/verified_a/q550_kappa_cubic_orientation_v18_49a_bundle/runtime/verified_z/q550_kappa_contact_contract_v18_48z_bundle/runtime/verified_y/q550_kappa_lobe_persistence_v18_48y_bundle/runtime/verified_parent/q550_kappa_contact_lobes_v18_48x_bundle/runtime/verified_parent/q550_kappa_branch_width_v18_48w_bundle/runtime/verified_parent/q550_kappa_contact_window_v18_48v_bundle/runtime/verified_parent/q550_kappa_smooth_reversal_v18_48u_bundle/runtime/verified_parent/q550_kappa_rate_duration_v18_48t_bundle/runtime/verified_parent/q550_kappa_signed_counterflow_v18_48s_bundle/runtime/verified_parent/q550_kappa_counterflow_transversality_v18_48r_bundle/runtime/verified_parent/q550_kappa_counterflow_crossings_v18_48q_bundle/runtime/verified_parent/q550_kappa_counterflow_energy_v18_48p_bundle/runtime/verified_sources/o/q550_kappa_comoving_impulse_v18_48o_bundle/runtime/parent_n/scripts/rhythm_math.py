"""v18.48n: self-contained frozen-chart diagnostics (not a reverse physical IVP)."""
from __future__ import annotations
import math
import numpy as np

def unit(x):
    y=np.asarray(x,float);n=np.linalg.norm(y)
    if not np.isfinite(n) or n<1e-270:raise ValueError('Invalid norm')
    return y/n

def projective_angle(a,b):
    a=unit(a);b=unit(b)
    return math.degrees(2*math.asin(min(1.,np.linalg.norm(a-(b if a@b>=0 else -b))/2)))

def projection_loss(g,P):
    g=unit(g)
    z=float(g@(P@g))
    return float(np.clip(1-z,0,1))

def lag_correlation(x,y,max_lag=6,min_pairs=12):
    """Positive lag l: x(t) compared against y(t+l). Return all lags."""
    x=np.asarray(x,float);y=np.asarray(y,float)
    if x.shape!=y.shape:raise ValueError('Lag arrays mismatched')
    out=[]
    for lag in range(-max_lag,max_lag+1):
        a=x[max(0,-lag):len(x)-max(0,lag)]
        b=y[max(0,lag):len(y)-max(0,-lag)]
        ok=np.isfinite(a)&np.isfinite(b)
        a=a[ok];b=b[ok]
        if len(a)<min_pairs or np.std(a)<1e-14 or np.std(b)<1e-14:
            corr=math.nan
        else:
            a=a-a.mean();b=b-b.mean()
            corr=float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)))
        out.append(dict(lag_steps=lag,pairs=int(len(a)),correlation=corr))
    return out

def reverse_projector_symmetry(P,Q):
    """Same two snapshots reordered have identical undirected projector distance."""
    f=float(np.linalg.norm(Q-P,'fro'))
    b=float(np.linalg.norm(P-Q,'fro'))
    return f,b,abs(f-b)

def directed_loss(g0,g1,P0,P1):
    """Changes in geometric mismatch from a frozen observer at each endpoint.

    Not a physical energy, work, dissipation, or reversed-flow integral.
    """
    lf=projection_loss(g0,P1)-projection_loss(g0,P0)
    lr=projection_loss(g1,P0)-projection_loss(g1,P1)
    return float(lf),float(lr)

def cancellation_signals(B,C,g):
    g=unit(g);b=B@g;c=C@g
    nb=float(np.linalg.norm(b));nc=float(np.linalg.norm(c));nt=float(np.linalg.norm(b+c))
    source=math.hypot(nb,nc)
    coupling_zero=(nc <= 1e-12*max(nb,1e-30))
    ratio=(nb+nc)/max(nt,1e-30)
    cosine=float(np.clip((b@c)/(nb*nc),-1.,1.)) if min(nb,nc)>1e-250 else math.nan
    return dict(log_R=math.log(max(ratio,1e-30)),R=ratio,
                resultant_over_source=nt/max(source,1e-30),
                base_norm=nb,coupling_norm=nc,source_norm=source,
                opposition_cosine=cosine,
                source_imbalance=(nb-nc)/max(nb+nc,1e-30),
                coupling_null=bool(coupling_zero))

def score_best(lags):
    valid=[a for a in lags if np.isfinite(a['correlation'])]
    return max(valid,key=lambda a:(abs(a['correlation']),-abs(a['lag_steps']))) if valid else None

def circular_control(x,y,max_lag=6):
    """Null comparator: all cyclic rephasings, peak absolute lag scanned each time.

    A descriptive finite-record control, not a test of independent events.
    """
    x=np.asarray(x);y=np.asarray(y)
    obs=score_best(lag_correlation(x,y,max_lag=max_lag))
    if obs is None:return dict(observed=math.nan,exceedance_fraction=math.nan,valid_shifts=0)
    null=[]
    for sh in range(1,len(y)):
        best=score_best(lag_correlation(x,np.roll(y,sh),max_lag=max_lag))
        if best is not None:null.append(abs(best['correlation']))
    if not null:return dict(observed=obs['correlation'],exceedance_fraction=math.nan,valid_shifts=0)
    return dict(observed=obs['correlation'],exceedance_fraction=float((1+sum(a>=abs(obs['correlation']) for a in null))/(1+len(null))),valid_shifts=len(null))
