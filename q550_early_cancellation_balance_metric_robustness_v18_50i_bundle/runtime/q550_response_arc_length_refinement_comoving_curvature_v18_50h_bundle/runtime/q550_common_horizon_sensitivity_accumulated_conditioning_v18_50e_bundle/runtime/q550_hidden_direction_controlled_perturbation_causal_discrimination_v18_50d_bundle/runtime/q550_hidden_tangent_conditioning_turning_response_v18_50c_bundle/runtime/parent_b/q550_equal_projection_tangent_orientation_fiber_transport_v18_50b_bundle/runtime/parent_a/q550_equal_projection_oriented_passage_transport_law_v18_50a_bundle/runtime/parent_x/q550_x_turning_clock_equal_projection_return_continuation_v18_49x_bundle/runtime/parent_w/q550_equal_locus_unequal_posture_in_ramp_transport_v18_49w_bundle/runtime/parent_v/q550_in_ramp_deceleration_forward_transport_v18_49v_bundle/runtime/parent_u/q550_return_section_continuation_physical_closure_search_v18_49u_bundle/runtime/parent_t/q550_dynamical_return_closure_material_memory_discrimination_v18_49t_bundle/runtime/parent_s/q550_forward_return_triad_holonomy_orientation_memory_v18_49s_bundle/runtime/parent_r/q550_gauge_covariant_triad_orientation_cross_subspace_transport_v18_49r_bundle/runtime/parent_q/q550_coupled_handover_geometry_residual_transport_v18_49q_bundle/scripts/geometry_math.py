"""Q550 v18.49q: projector geometry with a common fixed kinetic reference.

The rank labels refer to *ordered simple eigenspaces*, not tracked material objects.
K = sum K_ij, K_ij = omega[j,i] (a_j a_i^T - a_i a_j^T).
Pairwise Frobenius contributions are orthogonal at the same phase. Their
NONCOMMUTING finite transports are not additive; a zero instantaneous closure
error does NOT imply a zero geometrical remainder.
"""
import numpy as np
from scipy.linalg import expm
from itertools import combinations
PAIRS=list(combinations(range(10),2))
I67=PAIRS.index((5,6)); I78=PAIRS.index((6,7)); I68=PAIRS.index((5,7))

def pair_generators(out):
    a=out['axes'];omega=out['Omega'];parts=[]
    for i,j in PAIRS:
        parts.append(omega[j,i]*(np.outer(a[:,j],a[:,i])-np.outer(a[:,i],a[:,j])))
    return np.stack(parts)

def decompose(out):
    K=np.asarray(out['generator']); parts=pair_generators(out)
    p67=parts[I67];p78=parts[I78];p68=parts[I68]
    two=p67+p78; other=K-two
    reconstruct=np.sum(parts,axis=0)
    powers=np.sum(parts**2,axis=(1,2));total=np.sum(K*K)
    if not total>0:raise ValueError('Generator norm is zero')
    comm=p67@p78-p78@p67
    axes=out['axes']; a6,a8=axes[:,5],axes[:,7]
    # Lie bracket is a rotation in the 6-8 plane, not necessarily an observed K_68.
    probe=np.outer(a8,a6)-np.outer(a6,a8)
    S=np.sum(out['projectors'][[5,6,7]],axis=0)
    # The two selected pairs rotate INSIDE S; the other 43 can move S itself.
    leak=other@S-S@other
    return {'K':K,'two':two,'other':other,'parts':parts,'P':out['projectors'],
      'comm':comm,'bracket_68_coefficient':float(np.sum(comm*probe)/2),
      'comm_outside_68':float(np.linalg.norm(comm-np.sum(comm*probe)/2*probe)),
      'norm_comm':float(np.linalg.norm(comm)),
      'norm_K':float(np.linalg.norm(K)),'norm_two':float(np.linalg.norm(two)),
      'norm_other':float(np.linalg.norm(other)),'norm_leak_S678':float(np.linalg.norm(leak)),
      'share_two':float(np.sum(two*two)/total),'share_other':float(np.sum(other*other)/total),
      'share_68':float(powers[I68]/total),'share_67':float(powers[I67]/total),
      'share_78':float(powers[I78]/total),
      'generator_closure_relative':float(np.linalg.norm(K-reconstruct)/max(1,np.linalg.norm(K))),
      'orthogonality_relative':float(abs(np.sum(two*other))/max(1,total)),
      'internal_subspace_commutator':float(np.linalg.norm(two@S-S@two)),
      'projector_derivative_closure':float(max(np.linalg.norm(out['projector_dot'][j]-(K@out['projectors'][j]-out['projectors'][j]@K)) for j in range(10))),
      'comm_theory_residual':float(abs(np.linalg.norm(comm)-np.sqrt(2)*abs(out['Omega'][6,5]*out['Omega'][7,6]))) }

def transports(midpoints,h):
    """Orthogonal midpoint exponential integration in declared common frame."""
    U=np.eye(10); U2=U.copy();Uo=U.copy();U68=U.copy()
    for obj in midpoints:
        U=expm(h*obj['K'])@U
        U2=expm(h*obj['two'])@U2
        Uo=expm(h*obj['other'])@Uo
        U68=expm(h*(obj['two']+obj['parts'][I68]))@U68
    return U,U2,Uo,U68

def projector_transport_error(U,P0,P1,indices=(5,6,7)):
    return float(max(np.linalg.norm(U@P0[i]@U.T-P1[i]) for i in indices))

def aggregated_subspace_change(S0,S1):
    return float(np.linalg.norm(S1-S0))

def angle_projector(P0,P1):
    return float(np.clip(np.trace(P0@P1),0,1))

