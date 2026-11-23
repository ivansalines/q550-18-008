"""Dynamic return closure tests in the actual 11D Q550 phase convention."""
import numpy as np
from scipy.optimize import minimize_scalar
I_VEL=np.array([1,3,5,7,9],dtype=int)
I_CONFIG=np.array([0,2,4,6,8,10],dtype=int)
I_PHASE={2,6,10}

def phase_wrap(x):return (np.asarray(x)+np.pi)%(2*np.pi)-np.pi

def difference(a,b,indices):
    a=np.asarray(a,float);b=np.asarray(b,float)
    return np.array([float(phase_wrap(a[i]-b[i])) if i in I_PHASE else float(a[i]-b[i]) for i in indices])

def config_distance(a,b):return float(np.linalg.norm(difference(a,b,I_CONFIG)))

def reversal_velocity_mismatch(a,b):return float(np.linalg.norm(np.asarray(a)[I_VEL]+np.asarray(b)[I_VEL]))

def full_reversed_distance(a,b):
    cfg=difference(a,b,I_CONFIG)
    vel=np.asarray(a)[I_VEL]+np.asarray(b)[I_VEL]
    return float(np.linalg.norm(np.r_[cfg,vel]))

def velocity_flip(y):
    z=np.asarray(y,float).copy();z[I_VEL]*=-1;return z

def signed_phase_displacement(a,b):return float(phase_wrap(float(a)-float(b)))

def best_dynamic_section(forward_state,return_fun,r,total,samples=101):
    grid=np.linspace(r,total,int(samples))
    d=np.array([config_distance(forward_state,return_fun(t)[:11]) for t in grid])
    minima=[0,len(grid)-1]+[i for i in range(1,len(grid)-1) if d[i]<=d[i-1] and d[i]<=d[i+1]]
    candidates=[(float(d[i]),float(grid[i])) for i in minima]
    for i in minima:
        if i in (0,len(grid)-1):continue
        result=minimize_scalar(lambda t:config_distance(forward_state,return_fun(t)[:11]),
                               bounds=(grid[i-1],grid[i+1]),method='bounded',
                               options={'xatol':3e-12})
        candidates.append((float(result.fun),float(result.x)))
    best=min(candidates,key=lambda pair:pair[0])
    return best[1],best[0],len(minima)

def principal_angles(P,Q):
    a,s,b=np.linalg.svd(P);c,u,d=np.linalg.svd(Q)
    # Eigenvalues of projection P identify the common dimension.
    w,v=np.linalg.eigh(.5*(P+P.T));i=np.argsort(w)[-3:];A=v[:,i]
    w,v=np.linalg.eigh(.5*(Q+Q.T));i=np.argsort(w)[-3:];B=v[:,i]
    ss=np.linalg.svd(A.T@B,compute_uv=False)
    theta=np.degrees(np.arccos(np.clip(ss,0,1)))
    return [float(x) for x in np.sort(theta)],float(np.linalg.norm(P-Q))
