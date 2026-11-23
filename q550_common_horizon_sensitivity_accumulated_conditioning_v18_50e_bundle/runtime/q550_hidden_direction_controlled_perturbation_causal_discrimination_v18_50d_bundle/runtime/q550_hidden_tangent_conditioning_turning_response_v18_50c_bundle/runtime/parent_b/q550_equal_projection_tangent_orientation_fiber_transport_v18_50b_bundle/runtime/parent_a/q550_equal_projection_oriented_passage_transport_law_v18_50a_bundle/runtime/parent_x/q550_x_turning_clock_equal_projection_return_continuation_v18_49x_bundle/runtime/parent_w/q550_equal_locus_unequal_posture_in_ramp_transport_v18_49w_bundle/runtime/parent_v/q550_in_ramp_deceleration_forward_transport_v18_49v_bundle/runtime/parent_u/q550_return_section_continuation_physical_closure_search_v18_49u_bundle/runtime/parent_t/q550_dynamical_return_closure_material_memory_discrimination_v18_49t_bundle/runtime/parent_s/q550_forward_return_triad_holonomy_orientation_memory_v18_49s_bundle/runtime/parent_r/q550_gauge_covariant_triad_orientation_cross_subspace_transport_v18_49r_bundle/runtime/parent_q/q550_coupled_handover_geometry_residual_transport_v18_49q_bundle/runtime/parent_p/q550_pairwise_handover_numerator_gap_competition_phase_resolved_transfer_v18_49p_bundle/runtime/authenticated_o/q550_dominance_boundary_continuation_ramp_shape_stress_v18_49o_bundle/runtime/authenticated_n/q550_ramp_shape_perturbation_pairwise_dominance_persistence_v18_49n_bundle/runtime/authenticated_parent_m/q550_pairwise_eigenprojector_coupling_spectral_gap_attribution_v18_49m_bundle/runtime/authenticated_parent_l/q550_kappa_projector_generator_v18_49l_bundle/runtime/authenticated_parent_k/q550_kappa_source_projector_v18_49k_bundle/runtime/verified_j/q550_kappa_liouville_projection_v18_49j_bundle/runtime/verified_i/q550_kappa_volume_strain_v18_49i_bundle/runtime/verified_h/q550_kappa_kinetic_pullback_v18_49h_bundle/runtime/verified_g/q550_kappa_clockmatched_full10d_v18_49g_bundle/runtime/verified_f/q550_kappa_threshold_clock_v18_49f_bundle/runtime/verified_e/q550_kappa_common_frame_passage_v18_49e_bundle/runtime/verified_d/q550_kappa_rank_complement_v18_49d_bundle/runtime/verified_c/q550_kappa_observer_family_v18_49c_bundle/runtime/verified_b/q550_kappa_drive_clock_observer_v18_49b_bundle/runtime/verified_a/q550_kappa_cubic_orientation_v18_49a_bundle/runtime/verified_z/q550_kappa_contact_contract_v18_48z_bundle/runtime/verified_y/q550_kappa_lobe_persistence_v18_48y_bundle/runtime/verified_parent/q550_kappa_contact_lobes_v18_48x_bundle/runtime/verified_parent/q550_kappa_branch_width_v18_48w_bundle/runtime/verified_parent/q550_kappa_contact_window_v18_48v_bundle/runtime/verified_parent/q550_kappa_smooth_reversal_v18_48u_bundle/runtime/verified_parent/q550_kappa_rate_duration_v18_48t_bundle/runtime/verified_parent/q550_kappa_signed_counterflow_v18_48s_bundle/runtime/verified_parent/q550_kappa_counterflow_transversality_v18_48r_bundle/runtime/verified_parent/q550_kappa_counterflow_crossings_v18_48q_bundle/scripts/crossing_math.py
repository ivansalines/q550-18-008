#!/usr/bin/env python3
"""Source-independent mathematical geometry of full-state near-crossings."""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import minimize,minimize_scalar,least_squares
from scipy.interpolate import CubicSpline

def wrap(d):return (np.asarray(d)+np.pi)%(2*np.pi)-np.pi

def shape(y):
    """(log rho1, log rho2, x). Arrays have trailing state dimension=11."""
    a=np.asarray(y,dtype=float)
    z=a[...,8];x=np.where(z>=0,1/(1+np.exp(-np.clip(z,-700,700))),
                       np.exp(np.clip(z,-700,700))/(1+np.exp(np.clip(z,-700,700))))
    return np.stack((a[...,0],a[...,4],x),axis=-1)

def spatial_distance(a,b):return float(np.linalg.norm(shape(a)-shape(b)))

def state_differences(a,b,energy_function,kappa,params):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    phases=wrap(a[[2,6,10]]-b[[2,6,10]])
    vel=a[[1,3,5,7,9]]-b[[1,3,5,7,9]]
    dg=shape(a)-shape(b)
    return {'shape_distance':float(np.linalg.norm(dg)),
            'logrho1_delta':float(dg[0]),'logrho2_delta':float(dg[1]),'x_delta':float(dg[2]),
            'theta1_delta_rad':float(phases[0]),'theta2_delta_rad':float(phases[1]),
            'Theta_delta_rad':float(phases[2]),'velocity_delta_L2':float(np.linalg.norm(vel)),
            'tau_velocity_delta_components':';'.join(f'{v:.15g}' for v in vel),
            'full11D_chart_delta_L2':float(np.linalg.norm(np.r_[dg[0],vel[0],phases[0],vel[1],dg[1],vel[2],phases[1],vel[3],a[8]-b[8],vel[4],phases[2]])),
            'energy_delta':float(energy_function(a,kappa,params)-energy_function(b,kappa,params))}

def matched_progress_min(fwd_eval,rev_eval,energy_fn,kappa,params,cutoff=.06):
    """Closest distance at common normalized progress, excluding turnaround."""
    grid=np.linspace(cutoff,1,241)
    gaps=np.linalg.norm(shape(rev_eval(grid))-shape(fwd_eval(1-grid)),axis=-1)
    candidates=[(float(gaps[0]),float(grid[0])),(float(gaps[-1]),1.)]
    for i in range(1,len(grid)-1):
        if gaps[i]<=gaps[i-1] and gaps[i]<=gaps[i+1]:
            sol=minimize_scalar(lambda u: spatial_distance(rev_eval(u),fwd_eval(1-u)),
                                bounds=(float(grid[i-1]),float(grid[i+1])),method='bounded',
                                options={'xatol':1e-12})
            candidates.append((float(sol.fun),float(sol.x)))
    _,u=min(candidates)
    y=rev_eval(u);z=fwd_eval(1-u)
    result=dict(comparison='progress_matched',return_progress=u,forward_progress=1-u,
                normalized_progress_offset=0.,**state_differences(y,z,energy_fn,kappa,params))
    result['interior_minimum']=bool(cutoff+1e-6<u<1-1e-6)
    result['local_minima_found']=max(0,len(candidates)-2)
    return result

def free_pair_min(fwd_eval,rev_eval,energy_fn,kappa,params,
                  return_bounds=(.25,.96),forward_bounds=(.04,.75)):
    """Near-crossing minimization with fast high-density ODE-output interpolants.

    Builds cubic *shape* interpolants from 501 genuine dense-output IVP nodes.
    Starts 16 non-identical multistart optimizations with analytical Jacobian,
    then refines three selected basins against TRUE dense 11D IVP evaluations.
    Reports the independent true-IVP shape gap, not a spline-predicted gap.
    This is not a globally certified minimum.
    """
    ugrid=np.linspace(0,1,501)
    sr=CubicSpline(ugrid,shape(rev_eval(ugrid)),axis=0)
    sf=CubicSpline(ugrid,shape(fwd_eval(ugrid)),axis=0)
    us=np.linspace(*return_bounds,61);ss=np.linspace(*forward_bounds,61)
    aa=sr(us);bb=sf(ss)
    grid=np.linalg.norm(aa[:,None,:]-bb[None,:,:],axis=-1)
    picks=np.argsort(grid.ravel())[:12]
    starts=[(float(us[i]),float(ss[j])) for i,j in (np.unravel_index(k,grid.shape) for k in picks)]
    for u in np.linspace(*return_bounds,5):
        i=np.argmin(abs(us-u));j=np.argmin(grid[i]);starts.append((float(us[i]),float(ss[j])))
    candidates=[]
    for u,s in starts:
        def resid(t):return sr(t[0])-sf(t[1])
        def jac(t):return np.column_stack((sr(t[0],1),-sf(t[1],1)))
        solution=least_squares(resid,[u,s],jac=jac,bounds=([return_bounds[0],forward_bounds[0]],
            [return_bounds[1],forward_bounds[1]]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=80)
        candidates.append((float(np.linalg.norm(resid(solution.x))),solution.x.copy()))
    best=(math.inf,None)
    for _,seed in sorted(candidates,key=lambda x:x[0])[:3]:
        def truefun(t):
            dr=shape(rev_eval(float(t[0])))-shape(fwd_eval(float(t[1])))
            return float(np.dot(dr,dr))
        trial=minimize(truefun,seed,method='L-BFGS-B',bounds=[return_bounds,forward_bounds],
            options={'maxiter':100,'ftol':1e-15,'gtol':1e-12})
        d=float(truefun(trial.x))
        if d<best[0]:best=(d,trial.x.copy())
    u,s=map(float,best[1]);y=rev_eval(u);z=fwd_eval(s)
    approximated=float(np.linalg.norm(sr(u)-sf(s)))
    truegap=float(np.linalg.norm(shape(y)-shape(z)))
    result=dict(comparison='asynchronous_free_pair',return_progress=u,forward_progress=s,
                normalized_progress_offset=float(u+s-1),
                **state_differences(y,z,energy_fn,kappa,params))
    result['interior_minimum']=bool(return_bounds[0]+1e-6<u<return_bounds[1]-1e-6
                                    and forward_bounds[0]+1e-6<s<forward_bounds[1]-1e-6)
    result['local_minima_found']=len(starts)
    result['interpolant_gap_error_at_min']=abs(truegap-approximated)
    return result
