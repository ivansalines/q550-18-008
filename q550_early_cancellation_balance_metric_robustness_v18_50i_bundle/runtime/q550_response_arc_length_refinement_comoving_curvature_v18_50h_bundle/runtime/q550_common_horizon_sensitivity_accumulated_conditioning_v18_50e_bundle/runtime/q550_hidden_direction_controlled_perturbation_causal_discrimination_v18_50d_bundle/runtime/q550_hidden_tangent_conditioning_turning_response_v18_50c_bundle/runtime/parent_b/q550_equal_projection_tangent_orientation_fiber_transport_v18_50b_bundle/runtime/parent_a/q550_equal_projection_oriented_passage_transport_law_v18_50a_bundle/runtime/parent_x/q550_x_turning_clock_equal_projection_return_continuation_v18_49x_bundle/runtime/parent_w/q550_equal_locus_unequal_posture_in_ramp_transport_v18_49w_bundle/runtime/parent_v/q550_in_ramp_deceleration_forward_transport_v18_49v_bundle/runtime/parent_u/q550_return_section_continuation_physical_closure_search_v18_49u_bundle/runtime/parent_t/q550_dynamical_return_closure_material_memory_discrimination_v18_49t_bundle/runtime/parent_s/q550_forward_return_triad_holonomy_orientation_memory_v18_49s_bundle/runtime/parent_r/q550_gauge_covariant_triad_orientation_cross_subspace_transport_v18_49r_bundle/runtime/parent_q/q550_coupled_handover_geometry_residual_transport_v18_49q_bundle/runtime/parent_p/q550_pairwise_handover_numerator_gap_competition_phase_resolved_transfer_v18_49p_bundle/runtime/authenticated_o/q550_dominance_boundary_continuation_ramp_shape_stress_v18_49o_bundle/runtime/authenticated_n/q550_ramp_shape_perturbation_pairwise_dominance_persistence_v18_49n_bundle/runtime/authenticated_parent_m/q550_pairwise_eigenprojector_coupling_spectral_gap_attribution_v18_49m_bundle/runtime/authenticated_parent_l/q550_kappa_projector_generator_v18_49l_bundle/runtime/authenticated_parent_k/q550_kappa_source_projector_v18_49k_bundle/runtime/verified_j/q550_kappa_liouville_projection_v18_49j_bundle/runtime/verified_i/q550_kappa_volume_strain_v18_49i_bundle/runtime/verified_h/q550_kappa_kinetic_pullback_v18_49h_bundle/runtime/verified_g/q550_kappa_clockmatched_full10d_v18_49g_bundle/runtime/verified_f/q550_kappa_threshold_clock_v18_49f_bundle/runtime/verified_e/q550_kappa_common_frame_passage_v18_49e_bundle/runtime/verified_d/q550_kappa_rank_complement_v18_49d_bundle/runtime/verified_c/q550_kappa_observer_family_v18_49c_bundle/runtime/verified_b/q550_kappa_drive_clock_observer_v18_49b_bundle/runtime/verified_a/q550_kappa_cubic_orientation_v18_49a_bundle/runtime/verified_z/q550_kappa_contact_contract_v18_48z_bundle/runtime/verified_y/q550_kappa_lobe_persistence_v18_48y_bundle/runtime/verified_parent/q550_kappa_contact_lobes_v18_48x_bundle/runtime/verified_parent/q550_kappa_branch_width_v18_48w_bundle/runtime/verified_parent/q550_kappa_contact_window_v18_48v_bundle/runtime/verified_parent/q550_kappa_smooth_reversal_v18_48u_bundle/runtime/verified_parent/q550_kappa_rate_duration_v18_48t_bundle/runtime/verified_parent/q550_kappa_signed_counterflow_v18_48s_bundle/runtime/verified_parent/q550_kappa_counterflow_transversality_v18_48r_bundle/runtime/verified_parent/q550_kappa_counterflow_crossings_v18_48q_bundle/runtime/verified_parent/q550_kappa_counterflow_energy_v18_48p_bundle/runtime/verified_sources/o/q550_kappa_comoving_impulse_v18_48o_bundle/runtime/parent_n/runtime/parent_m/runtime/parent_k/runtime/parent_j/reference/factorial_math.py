"""Two-/three-factor Shapley arithmetic for scalar diagnostics and vectors.

Pure arithmetic: NOT a coordinate-invariant geometric attribution or causal
intervention. Crossing a transported covector and a different base state is
an explicitly labelled, frozen-chart counterfactual.
"""
from __future__ import annotations
from itertools import permutations
import numpy as np


def shapley(values, n):
    """Shapley contributions for an n-cube, indexed by bitmask.

    f[i] scalar or ndarray. Equal averaging over every permutation of the
    factors. Telescopic sum of contributions equals f[(1<<n)-1]-f[0].
    """
    if len(values) != (1 << n):
        raise ValueError('All binary combinations must be provided')
    contributions = [np.zeros_like(np.asarray(values[0],float)) for _ in range(n)]
    for order in permutations(range(n)):
        mask=0
        for factor in order:
            nxt=mask | (1 << factor)
            contributions[factor] += (np.asarray(values[nxt],float)-np.asarray(values[mask],float))
            mask=nxt
    import math
    return [v/math.factorial(n) for v in contributions]


def second_interaction(q00,q10,q01,q11):
    return np.asarray(q11)-np.asarray(q10)-np.asarray(q01)+np.asarray(q00)


def diagnostics(B,C,null_relative=1e-12):
    B=np.asarray(B,float);C=np.asarray(C,float)
    nb=float(np.linalg.norm(B));nc=float(np.linalg.norm(C));S=B+C
    ns=float(np.linalg.norm(S));total=nb+nc
    zero_coupling=nc<=null_relative*max(nb,1e-30)
    # A structurally coupling-null observable is not called "compensated".
    if zero_coupling:
        score=0.;ratio=1.
    elif total<=1e-30:
        score=0.;ratio=1.
    else:
        ratio=total/max(ns,1e-30)
        score=float(np.log(ratio))
    return dict(log_cancellation=score,cancellation_ratio=ratio,
                base_norm=nb,coupling_norm=nc,resultant_norm=ns,
                cancellation_fraction=1-ns/max(total,1e-30),
                opposition_cosine=float(B@C/(nb*nc)) if nb*nc>1e-30 else None,
                is_coupling_null=bool(zero_coupling),
                near_singular_resultant=bool(ns<1e-10*max(total,1e-30)))
