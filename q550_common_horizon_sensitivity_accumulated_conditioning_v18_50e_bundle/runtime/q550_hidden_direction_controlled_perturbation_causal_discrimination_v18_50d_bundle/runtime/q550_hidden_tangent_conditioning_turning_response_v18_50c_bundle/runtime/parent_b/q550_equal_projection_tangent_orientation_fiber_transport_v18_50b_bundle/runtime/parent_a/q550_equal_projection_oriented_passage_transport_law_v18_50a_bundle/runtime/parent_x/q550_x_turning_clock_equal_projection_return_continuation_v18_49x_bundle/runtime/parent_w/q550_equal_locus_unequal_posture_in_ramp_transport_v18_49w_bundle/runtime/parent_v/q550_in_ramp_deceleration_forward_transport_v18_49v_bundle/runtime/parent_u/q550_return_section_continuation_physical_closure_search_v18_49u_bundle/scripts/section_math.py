"""Phase-aware matching, candidate optimization and strictly separated gates."""
import numpy as np
from scipy.optimize import minimize
I_CONFIG=np.array([0,2,4,6,8,10],dtype=int)
I_VEL=np.array([1,3,5,7,9],dtype=int)
ANGLE=np.array([2,6,10],dtype=int)

def wrap(x):return (np.asarray(x)+np.pi)%(2*np.pi)-np.pi

def residual(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    dc=b[I_CONFIG]-a[I_CONFIG]
    dc[[1,3,5]]=wrap(dc[[1,3,5]])
    dv=b[I_VEL]+a[I_VEL]  # v_return = -v_forward at matched configuration
    return dc,dv

def metrics(a,b,energy_a=None,energy_b=None):
    dc,dv=residual(a,b)
    return dict(config=float(np.linalg.norm(dc)),velocity=float(np.linalg.norm(dv)),
        full=float(np.linalg.norm(np.r_[dc,dv])),
        unwrapped_theta_turns=float((np.asarray(b)[10]-np.asarray(a)[10])/(2*np.pi)),
        energy_difference=(None if energy_a is None or energy_b is None else float(energy_b-energy_a)))

def vector_scores(forward_states,return_states):
    aa=np.asarray(forward_states,float)[:,None,:]
    bb=np.asarray(return_states,float)[None,:,:]
    dc=bb[:,:,I_CONFIG]-aa[:,:,I_CONFIG]
    dc[:,:,[1,3,5]]=wrap(dc[:,:,[1,3,5]])
    dv=bb[:,:,I_VEL]+aa[:,:,I_VEL]
    cfg=np.linalg.norm(dc,axis=2);vel=np.linalg.norm(dv,axis=2)
    return cfg,vel,np.hypot(cfg,vel)

def best_candidates(fwd,back,r,anchor_bounds,phase_bounds,ns,nt,seeds=5):
    sgrid=np.linspace(*anchor_bounds,ns)
    qgrid=np.linspace(*phase_bounds,nt)
    tgrid=r+qgrid
    af=[fwd(float(s))[:11] for s in sgrid]
    bf=[back(float(t))[:11] for t in tgrid]
    C,V,F=vector_scores(af,bf)
    out=[]
    for label,Z in [('configuration',C),('velocity',V),('joint_full_state',F)]:
        # Find several independent starting seeds; pick the best converged result.
        initial=[]
        for idx in np.argsort(Z.ravel()):
            i,j=np.unravel_index(int(idx),Z.shape)
            if any(abs(i-ii)<2 and abs(j-jj)<3 for ii,jj in initial):continue
            initial.append((i,j))
            if len(initial)>=seeds:break
        candidates=[]
        for i,j in initial:
            def fn(x):
                ac=fwd(float(x[0]))[:11];bc=back(float(x[1]))[:11]
                dc,dv=residual(ac,bc)
                z=dc if label=='configuration' else (dv if label=='velocity' else np.r_[dc,dv])
                return float(z@z)
            result=minimize(fn,[float(sgrid[i]),float(tgrid[j])],method='L-BFGS-B',
                bounds=[anchor_bounds,(r+phase_bounds[0],r+phase_bounds[1])],
                options={'maxiter':90,'ftol':1e-13,'gtol':1e-10, 'maxls':30})
            x=result.x
            ac=fwd(float(x[0]))[:11];bc=back(float(x[1]))[:11]
            dat=metrics(ac,bc)
            dat.update({'objective':label,'anchor_time':float(x[0]),'return_time':float(x[1]),
                'return_phase':float(x[1]-r),'optimized_objective_sq':float(result.fun),
                'optimization_success':bool(result.success),'grid_initial_score':float(Z[i,j]),
                'boundary_hit':bool(min(x[0]-anchor_bounds[0],anchor_bounds[1]-x[0],
                    x[1]-(r+phase_bounds[0]),r+phase_bounds[1]-x[1])<1e-5)})
            candidates.append(dat)
        out.append(min(candidates,key=lambda d:d[{'configuration':'config','velocity':'velocity','joint_full_state':'full'}[label]]))
    return out

def strict_gate(d,tol,require_lift=False):
    if d.get('spectral_projector_distance') is None or d.get('minimum_relative_gap') is None:
        return False
    check=(d['config'] <= tol['config'] and d['velocity'] <= tol['velocity'] and
        abs(d['energy_difference']) <= tol['energy'] and
        d['spectral_projector_distance'] <= tol['projector'] and
        d['minimum_relative_gap']>=tol['spectral_gap'])
    if require_lift:check=check and abs(d['unwrapped_theta_turns'])<=tol['phase_lift_turns']
    return bool(check)
