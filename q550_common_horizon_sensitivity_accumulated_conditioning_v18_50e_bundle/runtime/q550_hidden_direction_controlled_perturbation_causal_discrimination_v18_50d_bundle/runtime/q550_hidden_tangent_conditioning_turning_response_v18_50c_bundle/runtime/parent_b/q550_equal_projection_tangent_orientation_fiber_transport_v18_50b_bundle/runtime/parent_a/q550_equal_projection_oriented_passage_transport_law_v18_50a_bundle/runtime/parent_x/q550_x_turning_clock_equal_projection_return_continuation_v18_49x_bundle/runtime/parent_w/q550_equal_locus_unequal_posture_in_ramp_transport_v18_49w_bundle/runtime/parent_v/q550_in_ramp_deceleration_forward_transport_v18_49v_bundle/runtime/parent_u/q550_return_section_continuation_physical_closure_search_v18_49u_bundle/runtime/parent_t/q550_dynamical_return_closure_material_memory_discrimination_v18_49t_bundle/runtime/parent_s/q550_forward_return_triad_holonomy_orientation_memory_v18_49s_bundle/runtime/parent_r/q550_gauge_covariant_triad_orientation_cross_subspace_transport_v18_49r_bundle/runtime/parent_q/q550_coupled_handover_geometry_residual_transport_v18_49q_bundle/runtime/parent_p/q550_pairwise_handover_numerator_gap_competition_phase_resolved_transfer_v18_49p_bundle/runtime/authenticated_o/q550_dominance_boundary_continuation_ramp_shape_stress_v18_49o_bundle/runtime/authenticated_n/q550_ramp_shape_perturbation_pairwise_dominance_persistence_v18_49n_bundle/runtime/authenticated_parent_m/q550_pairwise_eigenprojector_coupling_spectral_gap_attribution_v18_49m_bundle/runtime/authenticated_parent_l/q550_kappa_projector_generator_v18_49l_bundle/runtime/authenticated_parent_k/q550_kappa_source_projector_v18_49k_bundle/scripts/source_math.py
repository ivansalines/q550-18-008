"""Exact kinetic volume density, Liouville generator and projection split."""
import numpy as np

def sigmoid(z):
    return 1/(1+np.exp(-z)) if z>=0 else np.exp(z)/(1+np.exp(z))

def log_kinetic_density(y,mx,tau=1.):
    """log abs det DH = 5log(tau)+log(mx)+4l1+4l2+2log(x(1-x))."""
    x=sigmoid(float(y[8])); g=x*(1-x)
    return float(5*np.log(tau)+np.log(mx)+4*y[0]+4*y[4]+2*np.log(g))

def log_density_gradient(y):
    z=np.zeros(10);z[0]=4;z[4]=4;z[8]=2*(1-2*sigmoid(float(y[8])))
    return z

def rate_split(y,flow,jac):
    """Instantaneous metric-volume divergence = tr(Df)+f.grad(log sqrt(det G))."""
    return float(np.trace(jac[:10,:10])),float(log_density_gradient(y)@flow[:10])

def occupation(u,axes):
    u=np.asarray(u);u=u/np.linalg.norm(u)
    return (axes.T@u)**2

def rate_occupation_split(q,unit_directions,axes):
    """Projector derivative identity: p'_i=2u'^T P_i u + u^T P'_i u.

    Central finite differences avoid eigenvector sign flips, since P=aa^T.
    """
    q=np.asarray(q);u=np.asarray(unit_directions);a=np.asarray(axes)
    P=np.einsum('nki,nli->nikl',a,a) # [phase, rank, 10,10]
    p=np.einsum('ni,nkij,nj->nk',u,P,u)
    up=np.gradient(u,q,axis=0,edge_order=2)
    Pp=np.gradient(P,q,axis=0,edge_order=2)
    dp=np.gradient(p,q,axis=0,edge_order=2)
    directional=2*np.einsum('ni,nkij,nj->nk',up,P,u)
    basis=np.einsum('ni,nkij,nj->nk',u,Pp,u)
    return p,dp,directional,basis

def alternate_volume_shift(start,finish,alpha):
    """Counterfactual DIFFERENT volume form: exp(alpha*(l1-l2)) times kinetic form."""
    return float(alpha*((finish[0]-finish[4])-(start[0]-start[4])))
