"""Metric-covariant envelope of a FINITE-DIMENSIONAL transported covector family.

M is a declared SPD tangent-coordinate metric, G columns are material covectors.
A(G,d;M)=sup_{g in col(G), g^T M^-1 g=1} abs(g^T d).
In exact arithmetic A^2 = z^T C^+ z with z=G^T d, C=G^T M^-1 G.
Numerical implementation orthonormalizes the metric-whitened columns,
using an explicit rank cutoff. A is basis-invariant only for fixed col(G).
It does NOT make the chosen metric or family intrinsically physical.
"""
from __future__ import annotations
import numpy as np

def envelope(g_rows,delta,metric,rank_tol=1e-10):
 """Returns amplitude, full material metric distance, fraction, rank, singular spectrum."""
 g=np.atleast_2d(np.asarray(g_rows,float));d=np.asarray(delta,float);m=np.asarray(metric,float)
 if g.shape[1]!=len(d) or m.shape!=(len(d),len(d)):raise ValueError('Incompatible dimensions')
 chol=np.linalg.cholesky(m)
 # Row covector g maps into Euclidean metric dual as L^-1 g ; d maps to L^T d.
 w=np.linalg.solve(chol,g.T)
 u,s,_=np.linalg.svd(w,full_matrices=False)
 keep=s>s[0]*rank_tol if len(s) and s[0]>0 else np.zeros_like(s,dtype=bool)
 if not np.any(keep):raise ValueError('Family completely unresolved under rank cutoff')
 # w= L^-1 G, so g^T d = w^T L^T d.
 xd=chol.T@d
 amp=float(np.linalg.norm(u[:,keep].T@xd))
 full=float(np.linalg.norm(xd))
 residual=float(np.sqrt(max(0.,full*full-amp*amp)))
 return {'amplitude':amp,'material_distance':full,'orthogonal_residual':residual,
         'fraction':amp/full if full>1e-30 else 0.,'rank':int(np.sum(keep)),
         'singular_values':s.tolist(),'rank_threshold':rank_tol,
         'relative_singular_floor':float(s[-1]/s[0]) if s[0]>0 else 0.}

def transform_chart(g_rows,delta,metric,s):
 """y'=S y, g'=S^-T g, M'=S^-T M S^-1? Not for tangent metric:
 tangent metric M'=S^-T M S^-1, yes; dual g' = S^-T g."""
 s=np.asarray(s,float);i=np.linalg.inv(s)
 return np.asarray(g_rows)@i,np.asarray(s)@np.asarray(delta),i.T@np.asarray(metric)@i

def local_lift(back,forward):
 """10D finite separation, with shortest signed principal branch for 2 phases."""
 d=(np.asarray(back,float)-np.asarray(forward,float))[:10].copy()
 for i in (2,6):d[i]=(d[i]+np.pi)%(2*np.pi)-np.pi
 return d

def bracket_hull(g_rows,delta,metric,rtol=1e-10):
 """Sign interval for metric-unit observer family: [-A,+A]."""
 a=envelope(g_rows,delta,metric,rtol)['amplitude']
 return -a,a
