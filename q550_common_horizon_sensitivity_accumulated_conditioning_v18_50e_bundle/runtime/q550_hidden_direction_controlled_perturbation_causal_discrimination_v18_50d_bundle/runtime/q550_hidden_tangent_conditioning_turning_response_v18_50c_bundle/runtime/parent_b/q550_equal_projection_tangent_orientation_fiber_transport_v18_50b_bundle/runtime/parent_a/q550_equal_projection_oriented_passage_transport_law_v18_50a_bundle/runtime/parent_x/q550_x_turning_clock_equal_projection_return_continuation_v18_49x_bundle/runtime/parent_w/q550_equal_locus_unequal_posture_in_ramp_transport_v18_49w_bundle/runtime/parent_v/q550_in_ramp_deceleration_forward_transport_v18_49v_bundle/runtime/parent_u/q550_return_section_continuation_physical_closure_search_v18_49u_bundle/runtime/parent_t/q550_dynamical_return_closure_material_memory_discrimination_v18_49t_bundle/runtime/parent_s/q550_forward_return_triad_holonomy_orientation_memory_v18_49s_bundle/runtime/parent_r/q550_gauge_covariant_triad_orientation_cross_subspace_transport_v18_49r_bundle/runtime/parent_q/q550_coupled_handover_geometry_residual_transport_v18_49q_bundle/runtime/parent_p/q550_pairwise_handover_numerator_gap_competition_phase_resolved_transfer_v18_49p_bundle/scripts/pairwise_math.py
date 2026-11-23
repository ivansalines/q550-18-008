"""Gauge-robust rank-pair decomposition of the Cauchy-Green generator.

For a simple ordered spectrum, |Omega[j,i]| = |N[j,i]| / (lambda[i]-lambda[j]).
Total ||K||_F^2 = 2 sum_{i<j} |Omega[j,i]|^2.
The two-factor symmetric Shapley decomposition is an EXACT algebraic identity
for the endpoint difference; its components are not dynamical causes.
"""
import numpy as np
from itertools import combinations
PAIRS=list(combinations(range(10),2))

def pair_spectrum(out):
    eig=np.asarray(out['eigenvalues'],float)
    axes=np.asarray(out['axes'],float)
    M=axes.T@np.asarray(out['Cdot'],float)@axes
    numerator=np.array([abs(float(M[j,i])) for i,j in PAIRS])
    gap=np.array([float(eig[i]-eig[j]) for i,j in PAIRS])
    if np.any(gap<=0):raise ValueError('Rank-ordered simple spectrum required')
    omega=numerator/gap
    sq=2*omega**2
    assert len(sq)==45
    return {'numerator':numerator,'gap':gap,'omega_abs':omega,'pair_K_frob_sq':sq,
            'total_K_frob_sq':float(sq.sum())}

def shapley_pair_attribution(before,after):
    n0,n1=before['numerator'],after['numerator']
    g0,g1=before['gap'],after['gap']
    # Independent rank-pair measurements at fixed clock points; no change
    # in each eigenvector's arbitrary sign can affect the attribution.
    f00=2*n0**2/g0**2;f10=2*n1**2/g0**2
    f01=2*n0**2/g1**2;f11=2*n1**2/g1**2
    num=.5*((f10-f00)+(f11-f01))
    den=.5*((f01-f00)+(f11-f10))
    err=float(np.max(np.abs((num+den)-(f11-f00))))
    return {'numerator_attribution':num,'gap_attribution':den,'delta_pair_norm_sq':f11-f00,
            'closure_error':err,'initial_norm_sq':float(f00.sum()),'final_norm_sq':float(f11.sum())}

def gap_only_and_num_only(before,after):
    n0,n1=before['numerator'],after['numerator']
    g0,g1=before['gap'],after['gap']
    return {'base':float(np.sqrt(np.sum(2*(n0/g0)**2))),
            'numerator_only':float(np.sqrt(np.sum(2*(n1/g0)**2))),
            'gap_only':float(np.sqrt(np.sum(2*(n0/g1)**2))),
            'both':float(np.sqrt(np.sum(2*(n1/g1)**2)))}

def top_pair_indices(spec,top=5):
    return np.argsort(-spec['pair_K_frob_sq'])[:top]
