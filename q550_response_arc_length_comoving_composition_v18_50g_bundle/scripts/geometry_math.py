"""Coordinate-dependent but metric-explicit, vector/arc diagnostics. Only sampled paths."""
import numpy as np

def safe_angle(v,w):
    nv=float(np.linalg.norm(v));nw=float(np.linalg.norm(w))
    if min(nv,nw)<1e-14:return None
    return float(np.degrees(np.arccos(np.clip(np.dot(v,w)/(nv*nw),-1,1))))

def metric_matrix(case):
    if case=='parent_whitened':return np.eye(4)
    if case=='declared_diagonal_stress':return np.diag([1,1,2,0.5])
    raise ValueError('Unknown chart metric')

def transform(v,metric):return np.sqrt(np.diag(metric))*np.asarray(v,float)

def norm(v):return float(np.linalg.norm(v))

def cancellation(l,t):
    a=norm(l);b=norm(t);c=norm(l+t)
    return (a+b-c)/(a+b) if a+b>1e-13 else 0.0

def arc_diagnostics(points, metric):
    """points [(tau,L,T,Robserved),...] measured, no interpolation or physical integration."""
    P=[]
    for tau,L,T,obs in points:
        l=transform(L,metric);t=transform(T,metric);o=transform(obs,metric);r=l+t
        P.append(dict(tau=float(tau), L=l,T=t,R=r,obs=o,obs_res=norm(o-r),c=cancellation(l,t),gain=norm(r)))
    arcs=[0.0];segments=[]
    for i in range(1,len(P)):
        a,b=P[i-1],P[i];dL=b['L']-a['L'];dT=b['T']-a['T'];dR=dL+dT
        chord=norm(dR);dt=b['tau']-a['tau']
        if dt<=0:raise ValueError('non-monotone horizons')
        arcs.append(arcs[-1]+chord)
        tangent=dR/chord if chord>1e-14 else np.zeros(4)
        both=norm(dL)+norm(dT)
        segments.append(dict(tau0=a['tau'],tau1=b['tau'],mid_tau=(a['tau']+b['tau'])/2,
            length=chord, avg_speed=chord/dt,
            local_signed_advance=float(np.dot(dL,tangent)),
            transported_signed_advance=float(np.dot(dT,tangent)),
            local_transverse=norm(dL-np.dot(dL,tangent)*tangent),
            transported_transverse=norm(dT-np.dot(dT,tangent)*tangent),
            segment_cancellation=(both-chord)/both if both>1e-14 else 0.0,
            increment_angle=safe_angle(dL,dT),dR=dR,dir=tangent))
    for i,v in enumerate(P):
        v['ell']=arcs[i];v['normalized_arc']=arcs[i]/arcs[-1] if arcs[-1]>0 else 0.0
    for i,row in enumerate(segments):
        row['arc0']=arcs[i];row['arc1']=arcs[i+1]
        row['normalized_mid_arc']=(arcs[i]+arcs[i+1])/(2*arcs[-1]) if arcs[-1]>0 else 0.
        row['turn_from_previous_deg']=safe_angle(segments[i-1]['dR'],row['dR']) if i>0 else None
        row['dc_dell']=(P[i+1]['c']-P[i]['c'])/row['length'] if row['length']>1e-14 else None
    sparse=norm(P[2]['R']-P[0]['R'])+norm(P[4]['R']-P[2]['R'])
    direct=norm(P[-1]['R']-P[0]['R'])
    return P,segments,dict(arc5=arcs[-1],arc3=sparse,arc2=direct,
                            coarse_loss_fraction=(arcs[-1]-sparse)/arcs[-1] if arcs[-1] else 0.,
                            straightness=direct/arcs[-1] if arcs[-1] else 1.,
                            max_composition_residual=max(x['obs_res'] for x in P))
