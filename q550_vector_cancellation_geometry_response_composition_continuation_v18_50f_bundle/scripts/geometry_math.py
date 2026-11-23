"""Pure 4D Euclidean geometry in the metric-whitened coordinates of v18.50e."""
import numpy as np

def ledger(local, transported, observed=None):
    l=np.asarray(local,float);t=np.asarray(transported,float)
    if l.shape!=(4,) or t.shape!=(4,) or not np.all(np.isfinite(l)) or not np.all(np.isfinite(t)):
        raise ValueError('Require finite 4-vectors')
    r=l+t;a=float(np.linalg.norm(l));b=float(np.linalg.norm(t));c=float(np.linalg.norm(r))
    dot=float(l@t)
    cos=float(np.clip(dot/(a*b),-1,1)) if a>1e-14 and b>1e-14 else None
    projection=dot/a if a>1e-14 else None
    transverse=float(np.sqrt(max(0.,b*b-(projection or 0.)**2))) if a>1e-14 else None
    denom=a+b
    cancel=float(np.clip((denom-c)/denom,0.,1.)) if denom>0 else 0.
    ans=dict(local_norm=a,transported_norm=b,resultant_norm=c,local_transport_dot=dot,
       alignment_cos=cos,alignment_angle_deg=float(np.degrees(np.arccos(cos))) if cos is not None else None,
       transported_parallel_signed=projection,transported_perp_norm=transverse,
       cancellation_fraction=cancel,transport_share=b/denom if denom>0 else 0.,
       gram_determinant=max(0.,a*a*b*b-dot*dot),
       local_response_radial=float(l@r/c) if c>1e-14 else None,
       transported_response_radial=float(t@r/c) if c>1e-14 else None)
    if observed is not None:
        obs=np.asarray(observed,float)
        ans['observed_vs_split_abs']=float(np.linalg.norm(obs-r))
        ans['observed_vs_split_rel']=float(np.linalg.norm(obs-r)/max(1.,float(np.linalg.norm(obs))))
    return ans

def angular_change(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    na=np.linalg.norm(a);nb=np.linalg.norm(b)
    if na<1e-14 or nb<1e-14:return None
    return float(np.degrees(np.arccos(np.clip(a@b/(na*nb),-1.,1.))))
