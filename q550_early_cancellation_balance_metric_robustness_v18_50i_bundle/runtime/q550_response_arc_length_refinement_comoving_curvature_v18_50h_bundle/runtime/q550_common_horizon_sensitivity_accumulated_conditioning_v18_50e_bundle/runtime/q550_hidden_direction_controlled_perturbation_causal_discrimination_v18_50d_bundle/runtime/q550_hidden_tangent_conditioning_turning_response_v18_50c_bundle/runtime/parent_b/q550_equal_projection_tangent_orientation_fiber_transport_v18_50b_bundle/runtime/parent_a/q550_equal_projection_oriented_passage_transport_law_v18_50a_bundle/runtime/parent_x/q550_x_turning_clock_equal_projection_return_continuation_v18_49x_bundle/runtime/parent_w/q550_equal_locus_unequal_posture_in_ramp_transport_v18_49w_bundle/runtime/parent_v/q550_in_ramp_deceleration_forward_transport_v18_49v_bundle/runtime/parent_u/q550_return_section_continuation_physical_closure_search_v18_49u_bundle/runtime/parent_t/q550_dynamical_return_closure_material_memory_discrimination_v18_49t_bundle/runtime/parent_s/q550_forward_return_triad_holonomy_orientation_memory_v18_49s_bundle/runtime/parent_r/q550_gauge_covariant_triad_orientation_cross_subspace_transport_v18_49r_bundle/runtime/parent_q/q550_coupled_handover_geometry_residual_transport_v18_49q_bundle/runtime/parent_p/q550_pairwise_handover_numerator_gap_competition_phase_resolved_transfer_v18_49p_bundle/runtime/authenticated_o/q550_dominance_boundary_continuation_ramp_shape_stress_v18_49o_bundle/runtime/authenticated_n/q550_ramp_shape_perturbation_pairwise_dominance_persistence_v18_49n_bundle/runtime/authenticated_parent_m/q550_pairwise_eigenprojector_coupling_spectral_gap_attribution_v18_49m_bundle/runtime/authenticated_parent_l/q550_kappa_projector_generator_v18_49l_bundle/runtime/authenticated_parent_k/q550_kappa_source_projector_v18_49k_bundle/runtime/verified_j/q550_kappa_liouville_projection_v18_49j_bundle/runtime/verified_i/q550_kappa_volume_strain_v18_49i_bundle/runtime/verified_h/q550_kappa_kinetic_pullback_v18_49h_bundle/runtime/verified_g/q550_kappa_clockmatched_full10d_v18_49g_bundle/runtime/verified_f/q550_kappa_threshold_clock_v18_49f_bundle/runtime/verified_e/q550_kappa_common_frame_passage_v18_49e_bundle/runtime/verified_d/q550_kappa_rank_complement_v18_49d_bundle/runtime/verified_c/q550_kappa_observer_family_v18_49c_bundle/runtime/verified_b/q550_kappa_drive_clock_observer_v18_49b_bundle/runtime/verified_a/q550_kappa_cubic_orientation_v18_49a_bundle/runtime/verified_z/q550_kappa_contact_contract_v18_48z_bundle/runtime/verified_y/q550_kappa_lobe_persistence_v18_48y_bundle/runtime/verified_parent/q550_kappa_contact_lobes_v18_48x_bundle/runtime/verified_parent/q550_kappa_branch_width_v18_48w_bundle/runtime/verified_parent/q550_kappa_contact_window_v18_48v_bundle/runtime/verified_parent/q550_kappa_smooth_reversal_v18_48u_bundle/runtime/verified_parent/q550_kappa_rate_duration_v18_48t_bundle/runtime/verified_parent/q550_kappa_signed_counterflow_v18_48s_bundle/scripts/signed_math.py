#!/usr/bin/env python3
"""Mathematically explicit oriented contact, phase synchronization, energy ledger."""
from __future__ import annotations
import math
import numpy as np
from scipy.optimize import brentq

def alignment(t_rev,t_fwd):
    """Chronological vs equal-drive-phase orientation in one declared 3D chart."""
    a=np.asarray(t_rev,float);b=np.asarray(t_fwd,float)
    da=np.linalg.norm(a);db=np.linalg.norm(b)
    if min(da,db)<1e-14:raise ValueError('Degenerate tangents')
    cos=float(np.clip(np.dot(a,b)/(da*db),-1,1))
    return dict(chronological_cos=cos,chronological_angle_deg=float(np.degrees(np.arccos(cos))),
                phase_corresponding_cos=-cos,phase_corresponding_angle_deg=float(np.degrees(np.arccos(-cos))),
                cross_magnitude=float(np.linalg.norm(np.cross(a,b))/(da*db)))

def projected_chirality(t_rev,t_fwd,axes):
    """Signed determinant; changing axis order reverses chirality."""
    a=np.asarray(t_rev,float)[list(axes)];b=np.asarray(t_fwd,float)[list(axes)]
    return float(a[0]*b[1]-a[1]*b[0])

def phase_corresponding_tangents(tr,tf,rate,duration):
    """s(u)=1-a*u, so forward tangent in return-time parametrization is -a*tf."""
    a=rate*duration
    if a<=0:raise ValueError('Nonpositive return phase speed')
    return np.asarray(tr,float),-a*np.asarray(tf,float)

def signed_contact_derivative(shape_delta,tr,tf,rate,duration):
    """Derivative of (||R(u)-F(1-a*u)||^2)/2, same external drive phase."""
    a=rate*duration
    return float(np.dot(shape_delta,np.asarray(tr)+a*np.asarray(tf)))

def signed_energy_gap_derivative(power_rev_per_xi,power_fwd_per_xi,rate,duration):
    """Derivative of E_R(u)-E_F(1-rate*duration*u)."""
    return float(duration*power_rev_per_xi+rate*duration*power_fwd_per_xi)

def phase_locked_component_roots(fwd_shape,rev_shape,rate,duration,lo,hi,component,nodes=401):
    """Find bracketed zeros of a single shape component with external drive phase matched."""
    xs=np.linspace(lo,hi,nodes)
    vals=np.asarray(rev_shape(xs))[:,component]-np.asarray(fwd_shape(1-rate*duration*xs))[:,component]
    result=[]
    fun=lambda u:float(np.asarray(rev_shape(float(u)))[component]-np.asarray(fwd_shape(float(1-rate*duration*u)))[component])
    for j in range(len(xs)-1):
        if vals[j]==0:root=float(xs[j])
        elif vals[j]*vals[j+1]<0:root=float(brentq(fun,float(xs[j]),float(xs[j+1]),xtol=1e-13))
        else:continue
        if not result or abs(root-result[-1])>1e-9:result.append(root)
    if vals[-1]==0 and (not result or abs(float(xs[-1])-result[-1])>1e-9):result.append(float(xs[-1]))
    return result
