"""SVD-resolved observer span, metric residual, projector transport and angle audits.

The tangent metric is explicitly declared. These are conditional, not intrinsic
material invariants. 'Unobserved' means metric orthogonal to the CHOSEN family.
"""
from __future__ import annotations
import numpy as np


def subspace(g, delta, metric, tol):
    g=np.atleast_2d(np.asarray(g,float))
    delta=np.asarray(delta,float)
    m=np.asarray(metric,float)
    chol=np.linalg.cholesky(m)
    w=np.linalg.solve(chol,g.T)
    u,s,vt=np.linalg.svd(w,full_matrices=False)
    keep=s>float(tol)*s[0] if len(s) and s[0] else np.zeros(len(s),dtype=bool)
    if not np.any(keep):raise ValueError('Unresolved observer family')
    U=u[:,keep]
    P=U@U.T
    xd=chol.T@delta
    observed=P@xd
    hidden=xd-observed
    distance=float(np.linalg.norm(xd))
    amplitude=float(np.linalg.norm(observed))
    residual=float(np.linalg.norm(hidden))
    return {'U':U,'P':P,'s':s,'rank':int(keep.sum()),'amplitude':amplitude,
        'residual':residual,'distance':distance,'fraction':amplitude/distance if distance else 0.,
        'hidden':hidden,'observed':observed,'metric':m,
        'identity_error':abs(distance**2-amplitude**2-residual**2)/max(1.,distance**2)}


def compare(a,b):
    """Subspaces share the SAME chart and tangent metric; allow unequal ranks."""
    ua,ub=a['U'],b['U']
    angles=np.degrees(np.arccos(np.clip(np.linalg.svd(ua.T@ub,compute_uv=False),-1,1)))
    gap=float(np.linalg.norm(a['P']-b['P'],ord='fro'))
    # NOTE unequal ranks: one should not interpret minimal angle as full continuity.
    return {'min_principal_angle_deg':float(angles.min()),
            'max_principal_angle_deg':float(angles.max()),
            'projector_frobenius_gap':gap,
            'rank_jump':abs(a['rank']-b['rank'])}


def complement_alignment(a,b):
    """Cosine of METRIC-WHITENED hidden displacement directions."""
    x,y=a['hidden'],b['hidden']
    if np.linalg.norm(x)<1e-13 or np.linalg.norm(y)<1e-13:return np.nan
    return float(x@y/(np.linalg.norm(x)*np.linalg.norm(y)))


def independent_extension(seeds):
    """Make 5 additional *synthetic mathematical* independent covectors.

    New rows span the nullspace of the initial historical five in the
    declared Euclidean coordinate chart. No physical privilege is claimed.
    """
    s=np.asarray(seeds,float)
    _,sv,vh=np.linalg.svd(s,full_matrices=True)
    if sv[-1]<sv[0]*1e-12:raise RuntimeError('Historical seed rank unresolved')
    return np.vstack([s,vh[5:,:]])


def maximal_projection_check(g,delta,metric,tol):
    a=subspace(g,delta,metric,tol)
    return a['identity_error']
