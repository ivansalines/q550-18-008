"""Finite difference decomposition for normalized directions in a declared fixed diagonal chart."""
import numpy as np

def unit(v,scale):
    v=np.asarray(v,float)/np.asarray(scale,float)
    n=np.linalg.norm(v)
    if n<1e-12 or not np.isfinite(n):raise ValueError('Zero/invalid hidden direction')
    return v/n

def centered(p,m,e):return (np.asarray(p,float)-np.asarray(m,float))/(2*e)

def angle(a,b):return float(np.degrees(np.arccos(np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)),-1,1))))

def central_directional(fun,y,v,step=1e-6):
    v=np.asarray(v,float);n=np.linalg.norm(v)
    if n<1e-12:return np.zeros_like(fun(y))
    eps=step/max(1,n)
    return centered(fun(y+eps*v),fun(y-eps*v),eps)

def split_response(direction,y,transported_delta,x_index=8,step=1e-6):
    delta=np.asarray(transported_delta,float)
    e=np.zeros(len(y));e[x_index]=1.
    frozen=central_directional(direction,y,e,step)
    accumulated=central_directional(direction,y,delta-e,step)
    total=central_directional(direction,y,delta,step)
    return frozen,accumulated,total,float(np.linalg.norm(total-frozen-accumulated))
