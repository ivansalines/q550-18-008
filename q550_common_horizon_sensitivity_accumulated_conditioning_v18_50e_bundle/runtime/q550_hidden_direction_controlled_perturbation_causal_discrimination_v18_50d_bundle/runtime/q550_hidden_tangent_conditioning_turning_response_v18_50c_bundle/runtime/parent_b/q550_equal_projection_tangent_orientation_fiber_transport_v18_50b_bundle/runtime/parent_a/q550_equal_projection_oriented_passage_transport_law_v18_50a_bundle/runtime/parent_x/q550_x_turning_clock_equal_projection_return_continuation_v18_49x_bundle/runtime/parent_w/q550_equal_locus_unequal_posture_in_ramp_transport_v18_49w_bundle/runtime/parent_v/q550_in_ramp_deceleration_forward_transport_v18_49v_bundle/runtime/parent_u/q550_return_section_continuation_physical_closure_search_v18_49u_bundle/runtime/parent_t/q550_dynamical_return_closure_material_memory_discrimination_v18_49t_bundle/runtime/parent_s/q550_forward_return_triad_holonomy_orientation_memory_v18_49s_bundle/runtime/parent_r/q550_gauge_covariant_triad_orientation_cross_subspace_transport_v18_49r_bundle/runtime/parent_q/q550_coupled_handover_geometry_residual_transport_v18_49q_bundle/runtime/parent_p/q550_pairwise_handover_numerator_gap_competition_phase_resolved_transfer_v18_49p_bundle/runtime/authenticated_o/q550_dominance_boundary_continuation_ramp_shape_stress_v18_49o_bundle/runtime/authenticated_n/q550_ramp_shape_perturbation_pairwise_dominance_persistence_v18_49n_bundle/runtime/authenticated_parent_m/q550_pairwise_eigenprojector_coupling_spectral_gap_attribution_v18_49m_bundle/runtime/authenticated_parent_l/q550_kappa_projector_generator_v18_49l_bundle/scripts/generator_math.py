"""Instantaneous Cauchy-Green eigenprojector generator in a fixed kinetic frame.

All derivatives are with respect to the registered return phase q (dt/dq=1).
Let C=B^T B. The material generator K is the unique skew-symmetric
operator without within-eigenspace diagonal gauge when the spectrum is simple:
   K = A Omega A^T, Omega[j,i]=(A^T Cdot A)[j,i]/(lambda_i-lambda_j).
Then dP_i/dq = [K,P_i]. This construction is intrinsic under time-independent
orthogonal changes of the declared initial kinetic frame, NOT under arbitrary
changes of physical metric, or time-dependent uncorrected gauge rotations.
"""
import numpy as np
from scipy.linalg import eigh


def kinetic_frame_derivative(y, flow, mx, tau, embedding, epsilon=2e-5):
    """Directional derivative of DH along the authentic material flow.

    Symmetric directional stencil is evaluated on the exact analytic kinetic
    embedding; no trajectory-based finite difference is used here.
    """
    y=np.asarray(y,dtype=float)[:10]
    v=np.asarray(flow,dtype=float)[:10]
    magnitude=max(1.,float(np.linalg.norm(v)))
    h=epsilon/magnitude
    _,jp=embedding(y+h*v,mx,tau)
    _,jm=embedding(y-h*v,mx,tau)
    return (jp-jm)/(2*h)


def deforming_frame(J,F,J0,Jdot,Jmaterial):
    """B=J*F/J0, Bdot=(Jdot+J*Jmaterial)*F/J0 in the initial kinetic frame."""
    right=np.linalg.solve(J0,np.eye(J0.shape[0]))
    B=(J@F)@right
    Bdot=((Jdot+J@Jmaterial)@F)@right
    return B,Bdot


def spectral_generator(B,Bdot,relative_gap_floor=1e-7):
    C=B.T@B
    Cdot=Bdot.T@B+B.T@Bdot
    lam,A=eigh(C,check_finite=False)
    idx=np.argsort(lam)[::-1]
    lam,A=lam[idx],A[:,idx]
    if np.min(lam)<=0:raise ValueError('Non-positive pullback tensor')
    relative_gaps=np.diff(lam)*-1/np.maximum(lam[:-1],1e-200)
    gmin=float(np.min(relative_gaps))
    if gmin<relative_gap_floor:raise ValueError('Insufficiently separated principal eigenspaces')
    M=A.T@Cdot@A
    den=lam[None,:]-lam[:,None]  # den[j,i] = lam_i-lam_j
    Omega=np.zeros_like(M)
    mask=~np.eye(len(lam),dtype=bool)
    Omega[mask]=M[mask]/den[mask]
    Omega=.5*(Omega-Omega.T)
    K=A@Omega@A.T
    P=np.einsum('ri,si->irs',A,A)
    Pdot=np.einsum('ij,njk->nik',K,P)-np.einsum('nij,jk->nik',P,K)
    speeds=np.linalg.norm(Pdot,axis=(1,2))/np.sqrt(2.)
    sigma=np.sqrt(lam)
    sigma_rate=np.diag(M)/(2*sigma)
    volume_rate=float(np.trace(np.linalg.solve(B,Bdot)))
    L=Bdot@np.linalg.inv(B)
    spatial_strain_rate=.5*(L+L.T)
    normC=float(np.linalg.norm(C));normCd=float(np.linalg.norm(Cdot))
    comm=C@Cdot-Cdot@C
    comm_ratio=float(np.linalg.norm(comm)/(normC*normCd)) if normCd>0 else 0.
    offdiag_ratio=float(np.linalg.norm(M-np.diag(np.diag(M)))/normCd) if normCd>0 else 0.
    return {'C':C,'Cdot':Cdot,'eigenvalues':lam,'axes':A,'projectors':P,'projector_dot':Pdot,
        'Omega':Omega,'generator':K,'speed':speeds,'sigma':sigma,'sigma_rate':sigma_rate,
        'log_volume_rate':volume_rate,'spatial_strain_rate':spatial_strain_rate,
        'commutator_fraction':comm_ratio,'offdiagonal_strain_fraction':offdiag_ratio,
        'min_relative_eigengap':gmin,'generator_frobenius':float(np.linalg.norm(K)),
        'projector_reconstruction_error':float(np.max(np.abs(Pdot-(K@P-P@K))))}


def occupation_split(u,uprime,P,Pdot):
    """Gauge-sign invariant decomposition of d(u.T P u)/dq."""
    pp=float(u@P@u)
    direction=float(2*uprime@P@u)
    axis=float(u@Pdot@u)
    return pp,direction,axis


def constant_orthogonal_gauge(B,Bdot,R):
    """Change the initial kinetic basis only: C' = R C R^T, K'=R K R^T."""
    return B@R.T,Bdot@R.T


def log_strain_sum_rule(out):
    return float(np.sum(out['sigma_rate']/out['sigma'])-out['log_volume_rate'])
