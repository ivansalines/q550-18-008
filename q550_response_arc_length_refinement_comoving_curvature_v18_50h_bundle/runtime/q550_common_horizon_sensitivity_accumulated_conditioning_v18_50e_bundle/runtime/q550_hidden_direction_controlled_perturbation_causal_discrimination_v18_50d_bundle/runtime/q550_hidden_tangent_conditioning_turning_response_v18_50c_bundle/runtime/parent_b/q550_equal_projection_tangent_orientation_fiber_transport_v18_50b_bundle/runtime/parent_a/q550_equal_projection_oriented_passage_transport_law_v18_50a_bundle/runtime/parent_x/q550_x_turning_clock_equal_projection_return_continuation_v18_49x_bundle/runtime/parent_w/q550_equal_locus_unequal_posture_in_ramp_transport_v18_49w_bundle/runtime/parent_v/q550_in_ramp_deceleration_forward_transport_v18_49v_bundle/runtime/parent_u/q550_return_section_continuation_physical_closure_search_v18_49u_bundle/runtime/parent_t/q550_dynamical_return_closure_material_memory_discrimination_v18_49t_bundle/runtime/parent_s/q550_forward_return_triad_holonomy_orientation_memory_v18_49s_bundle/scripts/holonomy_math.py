"""Canonical projector connectors and non-Abelian two-path holonomy.

Objects live in a fixed Euclidean 10D kinetic observer frame, as inherited
from authenticated v18.49r. Eigenvectors may change independent signs.
No uniqueness of a physical closure path is presumed.
"""
import numpy as np
from scipy.linalg import expm
I=np.eye(10)

def sym_projection(axes_or_projectors):
    arr=np.asarray(axes_or_projectors)
    if arr.ndim==2:return arr@arr.T
    return np.sum(arr[[5,6,7]],axis=0)

def canonical_connector(P,Q):
    """Direct rotation mapping projector P onto Q, well-defined away from a 90° principal angle.

    W = polar(QP+(I-Q)(I-P)); its positive polar part does not twist
    within the subspace or its orthogonal complement.
    """
    P=np.asarray(P);Q=np.asarray(Q)
    B=Q@P+(I-Q)@(I-P)
    u,s,vt=np.linalg.svd(B)
    if s.min()<1e-7:raise ValueError('Connector ill-defined near orthogonality')
    W=u@vt
    return W,float(s.min()),float(np.linalg.norm(W@P@W.T-Q))

def integrate_K_cross(getK,q0,q1,n):
    """True ordered exponential, with signed time step for reversal."""
    h=(q1-q0)/n;U=np.eye(10)
    for k in range(n):
        q=q0+(k+.5)*h
        U=expm(h*getK(q))@U
    return U

def principal_so3(H):
    u,s,vt=np.linalg.svd(H)
    R=u@vt
    if np.linalg.det(R)<0:
        u[:,-1]*=-1;R=u@vt
    theta=float(np.arccos(np.clip((np.trace(R)-1)/2.,-1.,1.)))
    return theta, R, float(np.linalg.norm(H.T@H-np.eye(3))),float(np.linalg.det(H)),[float(x) for x in s]

def loop(A0,A1,UA,B0,B1,UB,Aframe):
    C0,g0,e0=canonical_connector(A0,B0)
    C1,g1,e1=canonical_connector(A1,B1)
    Uloop=C0.T@UB.T@C1@UA
    H=Aframe.T@Uloop@Aframe
    angle,R,orth,det,svals=principal_so3(H)
    return {'angle_rad':angle,'angle_deg':float(np.degrees(angle)),
      'subspace_loop_closure':float(np.linalg.norm(Uloop@A0@Uloop.T-A0)),
      'connector_min_singular':min(g0,g1),'connector_max_error':max(e0,e1),
      'subspace_restricted_orthogonality_error':orth,'subspace_restricted_det':det,
      'subspace_restricted_singular_values':svals,'H_raw':H,'Uloop':Uloop,
      'connector_start':C0,'connector_end':C1}
