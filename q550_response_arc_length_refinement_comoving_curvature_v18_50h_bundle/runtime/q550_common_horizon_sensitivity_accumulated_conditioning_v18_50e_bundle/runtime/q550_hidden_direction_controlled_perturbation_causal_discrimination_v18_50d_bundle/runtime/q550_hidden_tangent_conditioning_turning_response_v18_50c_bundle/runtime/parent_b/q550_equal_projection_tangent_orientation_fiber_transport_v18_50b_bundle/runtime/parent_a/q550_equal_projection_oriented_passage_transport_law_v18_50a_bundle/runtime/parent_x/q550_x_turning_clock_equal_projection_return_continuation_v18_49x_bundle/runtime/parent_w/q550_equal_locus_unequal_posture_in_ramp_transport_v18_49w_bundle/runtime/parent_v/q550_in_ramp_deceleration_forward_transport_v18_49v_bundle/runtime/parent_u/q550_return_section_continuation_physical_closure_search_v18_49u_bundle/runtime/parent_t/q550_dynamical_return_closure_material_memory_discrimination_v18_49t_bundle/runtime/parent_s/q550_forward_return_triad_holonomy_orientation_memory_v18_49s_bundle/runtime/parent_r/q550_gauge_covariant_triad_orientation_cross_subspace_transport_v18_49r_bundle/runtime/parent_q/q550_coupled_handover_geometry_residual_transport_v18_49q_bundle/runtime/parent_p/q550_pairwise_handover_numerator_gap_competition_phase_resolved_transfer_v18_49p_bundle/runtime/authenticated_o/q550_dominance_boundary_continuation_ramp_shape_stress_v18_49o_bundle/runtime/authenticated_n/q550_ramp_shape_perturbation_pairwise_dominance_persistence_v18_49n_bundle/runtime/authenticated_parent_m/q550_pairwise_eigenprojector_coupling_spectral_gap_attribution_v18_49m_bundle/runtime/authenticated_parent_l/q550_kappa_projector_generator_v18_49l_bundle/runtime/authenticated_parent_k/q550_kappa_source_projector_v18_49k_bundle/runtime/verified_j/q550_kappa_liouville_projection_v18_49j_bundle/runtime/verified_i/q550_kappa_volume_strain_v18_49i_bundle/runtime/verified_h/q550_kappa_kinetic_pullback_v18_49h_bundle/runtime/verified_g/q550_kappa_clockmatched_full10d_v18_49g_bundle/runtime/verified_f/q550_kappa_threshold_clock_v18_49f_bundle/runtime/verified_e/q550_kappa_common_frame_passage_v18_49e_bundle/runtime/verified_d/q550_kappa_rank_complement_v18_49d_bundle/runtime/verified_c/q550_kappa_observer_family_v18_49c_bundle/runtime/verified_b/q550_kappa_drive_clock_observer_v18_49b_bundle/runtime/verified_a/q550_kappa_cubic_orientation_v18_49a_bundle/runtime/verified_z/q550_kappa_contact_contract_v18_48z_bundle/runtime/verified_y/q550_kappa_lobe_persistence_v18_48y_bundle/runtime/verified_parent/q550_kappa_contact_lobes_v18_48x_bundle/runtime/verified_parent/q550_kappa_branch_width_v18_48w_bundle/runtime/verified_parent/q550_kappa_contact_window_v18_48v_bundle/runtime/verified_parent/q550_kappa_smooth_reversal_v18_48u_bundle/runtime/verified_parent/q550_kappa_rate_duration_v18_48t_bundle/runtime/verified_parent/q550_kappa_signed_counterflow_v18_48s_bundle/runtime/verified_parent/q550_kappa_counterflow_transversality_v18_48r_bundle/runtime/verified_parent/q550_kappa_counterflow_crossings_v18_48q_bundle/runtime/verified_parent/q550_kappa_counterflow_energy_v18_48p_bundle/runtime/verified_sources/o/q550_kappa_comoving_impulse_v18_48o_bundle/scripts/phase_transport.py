"""Projective-minimal observer transport and impulse-robust finite-history diagnostics.

Co-moving frame is a *chosen discrete SO(n) gauge*, not an integrated physical
cotangent connection. It parallelizes only the transported projective line.
"""
from __future__ import annotations
import math
import numpy as np

def unit(x):
 x=np.asarray(x,dtype=float);n=np.linalg.norm(x)
 if not np.isfinite(n) or n<=1e-250:raise ValueError('Zero/nonfinite observer')
 return x/n

def minimal_turn(u,v):
 """Unique identity-on-complement minimal SO(n) rotation carrying unit u to v.

u and v must not be antipodal (projective sign alignment occurs upstream).
"""
 u=unit(u);v=unit(v);c=float(np.clip(u@v,-1.,1.));t=v-c*u;s=float(np.linalg.norm(t))
 eye=np.eye(len(u))
 if c < -1+1e-11:raise ValueError('Ambiguous antipodal transport')
 if s < 1e-13:return eye
 w=t/s
 out=eye+(c-1)*(np.outer(u,u)+np.outer(w,w))+s*(np.outer(w,u)-np.outer(u,w))
 return out

def comoving_frames(observers):
 """Frames R_i: R_i@g_0 = +/- g_i, with minimal-step projective transport.

Every R_i acts in the fixed chart. Use R_i.T @ P_i @ R_i for pullback.
"""
 g=[unit(x) for x in observers];aligned=[g[0]]
 for x in g[1:]:aligned.append(x if x@aligned[-1]>=0 else -x)
 frames=[np.eye(len(g[0]))];errors=[]
 for x,y in zip(aligned[:-1],aligned[1:]):
  O=minimal_turn(x,y)
  frames.append(O@frames[-1]);errors.append(np.linalg.norm(O@x-y))
 max_ortho=max(np.linalg.norm(R.T@R-np.eye(len(g[0])),'fro') for R in frames)
 max_track=max(np.linalg.norm(R@aligned[0]-gi) for R,gi in zip(frames,aligned))
 return np.asarray(frames),dict(max_step_line_error=max(errors,default=0.),max_orthogonality_error=max_ortho,max_line_tracking_error=max_track)

def projector_gap(P,Q):return float(np.linalg.norm(P-Q,'fro'))

def lag_pairs(x,y,max_lag=6,min_pairs=12,mask=None):
 """Lag > 0 means y occurs later than x; a mask does not compress time."""
 x=np.asarray(x,float);y=np.asarray(y,float)
 if x.shape!=y.shape:raise ValueError('Signal shapes differ')
 good=np.ones(len(x),dtype=bool) if mask is None else np.asarray(mask,bool)
 if good.shape!=x.shape:raise ValueError('Mask shape mismatch')
 ans=[]
 for k in range(-max_lag,max_lag+1):
  ia=np.arange(max(0,-k),len(x)-max(0,k));ib=ia+k
  valid=good[ia]&good[ib]&np.isfinite(x[ia])&np.isfinite(y[ib]);aa=x[ia[valid]];bb=y[ib[valid]]
  if len(aa)<min_pairs or np.std(aa)<1e-13 or np.std(bb)<1e-13:corr=float('nan')
  else:
   aa=aa-aa.mean();bb=bb-bb.mean();corr=float((aa@bb)/(np.linalg.norm(aa)*np.linalg.norm(bb)))
  ans.append(dict(lag_steps=k,pairs=len(aa),correlation=corr))
 return ans

def best_lag(scan):
 valid=[z for z in scan if np.isfinite(z['correlation'])]
 return max(valid,key=lambda z:(abs(z['correlation']),-abs(z['lag_steps']))) if valid else None

def pulse_centers(values,max_count=4,exclusion_radius=1):
 x=np.asarray(values,float);order=sorted(range(len(x)),key=lambda i:-abs(x[i]) if np.isfinite(x[i]) else float('inf'))
 out=[]
 for i in order:
  if not np.isfinite(x[i]):continue
  if all(abs(i-j)>exclusion_radius for j in out):out.append(i)
  if len(out)>=max_count:break
 return out

def impulse_masks(x,y,max_impulses=4,rad=1):
 """Cut entire local pulse neighborhoods WITHOUT collapsing sample indices."""
 x=np.asarray(x,float);y=np.asarray(y,float);N=len(x)
 cases=[('full',np.ones(N,bool),-1),('interior_80',np.array([(0.1*N)<=i<(0.9*N) for i in range(N)]),-1),('interior_60',np.array([(0.2*N)<=i<(0.8*N) for i in range(N)]),-1)]
 centers_x=pulse_centers(x,max_impulses,2*rad+1)
 centers_y=pulse_centers(y,max_impulses,2*rad+1)
 for src,cs in [('driver',centers_x),('response',centers_y)]:
  for j,i in enumerate(cs):
   mask=np.ones(N,bool);mask[max(0,i-rad):min(N,i+rad+1)]=False
   cases.append((f'leave_{src}_pulse{j+1}',mask,i))
 return cases

def cycling_control(x,y,mask,max_lag=6):
 """Descriptive cyclic controls with a fixed time mask; not an IID p-value."""
 obs=best_lag(lag_pairs(x,y,max_lag,mask=mask))
 if obs is None:return float('nan'),0
 vals=[]
 for s in range(1,len(y)):
  test=best_lag(lag_pairs(x,np.roll(y,s),max_lag,mask=mask))
  if test is not None:vals.append(abs(test['correlation']))
 return ((1+sum(v>=abs(obs['correlation']) for v in vals))/(1+len(vals)) if vals else float('nan')),len(vals)
