"""Pairwise geometric comparisons: zero conventions are explicit, no artificial gauge flip."""
import numpy as np

def logistic(z):
    z=float(z)
    return 1/(1+np.exp(-z)) if z>=0 else np.exp(z)/(1+np.exp(z))

def wrap_angle(x):return np.arctan2(np.sin(x),np.cos(x))

def so3_angle_deg(A,B):
    if A is None or B is None:return None
    C=A.T@B
    return float(np.degrees(np.arccos(np.clip((np.trace(C)-1)/2,-1.,1.))))

def compare(a,b,spans):
    """a/b have 11D states, common-frame triad projectors and transported SO(3) posture."""
    ya,yb=a['state'],b['state'];xa,xb=logistic(ya[8]),logistic(yb[8]);dx=abs(xa-xb)
    dr=float(np.linalg.norm(ya[[0,4]]-yb[[0,4]]))
    # Coordinate scale (not physical metric). Always report unscaled measurements too.
    loc=np.array([ya[0]-yb[0],ya[4]-yb[4],xa-xb],float)
    scaled=float(np.linalg.norm(loc /spans))
    dtheta=float(np.linalg.norm(wrap_angle(ya[[2,6]]-yb[[2,6]])))
    dstate=float(np.linalg.norm(ya[:10]-yb[:10]))
    out={'sigma_a':a['sigma'],'sigma_b':b['sigma'],'delta_sigma':b['sigma']-a['sigma'],
         'theta_lift_gap':float(abs(ya[10]-yb[10])),
         'x_abs_gap':dx,'x_gap_over_span':dx/spans[2],
         'radial_logrho_gap':dr,'locus_xyz_scaled_gap':scaled,
         'posture_theta_pair_gap_rad':dtheta,'full_state_10d_gap':dstate,
         'energy_gap':float(abs(a['energy']-b['energy'])),
         'cross_frame_triad_SO3_angle_deg':so3_angle_deg(a['R'],b['R'])}
    if a['S'] is not None and b['S'] is not None:
        s=np.linalg.svd(a['A'].T@b['A'],compute_uv=False)
        out['triad_projector_frobenius_gap']=float(np.linalg.norm(a['S']-b['S']))
        out['max_triad_principal_angle_deg']=float(np.degrees(np.arccos(np.clip(min(s),-1,1))))
    else:
        out['triad_projector_frobenius_gap']=None
        out['max_triad_principal_angle_deg']=None
    return out

def near_decision(p,x_tol=.10,locus_tol=.20,min_sep=.20):
    eligible=p['delta_sigma']>=min_sep-1e-12
    return eligible and p['x_gap_over_span']<=x_tol, eligible and p['locus_xyz_scaled_gap']<=locus_tol
