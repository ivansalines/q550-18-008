"""Geometric strain and signed-volume tools in the flat kinetic embedding.

No arbitrary observer-family selection appears in these material tensors.
The volume factor is invariant under constant tau-rescaling of the flat
kinetic embedding, but a different volume form may give a different value.
"""
import numpy as np
from scipy.linalg import eigh

def factor(B):
    """Return ordered stretch magnitudes, right axes in initial kinetic frame."""
    C=B.T@B
    eigen,axes=eigh(C,check_finite=False)
    idx=np.argsort(eigen)[::-1]
    v=eigen[idx];axes=axes[:,idx]
    if np.min(v)<=0:raise ValueError('Pullback metric must be positive definite')
    sigma=np.sqrt(v)
    sign,logdet=np.linalg.slogdet(B)
    if sign==0:raise ValueError('Singular variational flow')
    return sigma,axes,sign,float(logdet)

def fixed_metric_volume(f,J0,J1):
    """log volume between metric-volume forms, free of coordinate chart."""
    return (np.linalg.slogdet(f)[1]+np.linalg.slogdet(J1)[1]-np.linalg.slogdet(J0)[1])

def line_angle(a,b):
    cos=abs(float(np.dot(a,b)))/(np.linalg.norm(a)*np.linalg.norm(b))
    return float(np.rad2deg(np.arccos(np.clip(cos,0.,1.))))

def subspace_angles(a,b):
    """Both matrices hold an orthonormal basis of the same dimension."""
    sv=np.linalg.svd(a.T@b,compute_uv=False)
    return np.rad2deg(np.arccos(np.clip(sv,0.,1.)))

def anisotropic_length(sigma,axes,direction):
    u=direction/np.linalg.norm(direction)
    projected=axes.T@u
    return float(np.sqrt(np.sum(sigma**2*projected**2)))

def nearby_eigen_gaps(sigma):
    return np.abs(np.diff(sigma))/np.maximum(sigma[:-1],1e-100)

def gauge_strain_check(f,G0,G1,y0,y1):
    from kinetic_metric import nonlinear_chart_gauge
    fp,pg0,pg1=nonlinear_chart_gauge(f,G0,G1,y0,y1)
    orig=eigh(f.T@G1@f,G0,eigvals_only=True,check_finite=False)
    moved=eigh(fp.T@pg1@fp,pg0,eigvals_only=True,check_finite=False)
    return float(np.max(np.abs(orig-moved))/max(1.,float(np.max(orig))))

def volume_form_coordinate_change(f,G0,G1,D0,D1):
    """Arbitrary invertible endpoint chart matrices, with transformed metric."""
    fp=D1@f@np.linalg.inv(D0)
    g0=np.linalg.solve(D0.T,np.linalg.solve(D0,G0).T).T if False else np.linalg.inv(D0).T@G0@np.linalg.inv(D0)
    g1=np.linalg.inv(D1).T@G1@np.linalg.inv(D1)
    a=np.linalg.slogdet(fp)[1]+0.5*(np.linalg.slogdet(g1)[1]-np.linalg.slogdet(g0)[1])
    b=np.linalg.slogdet(f)[1]+0.5*(np.linalg.slogdet(G1)[1]-np.linalg.slogdet(G0)[1])
    return float(abs(a-b))
