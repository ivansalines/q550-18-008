#!/usr/bin/env python3
"""Exact coordinate-chain identities for a scalar barrier at a stationary point.

Important: the physical anti-drive phase q is a specifically calibrated clock.
An arbitrary nonlinear chart s is not a physical phase measurement.
"""
from __future__ import annotations
import math
import numpy as np

def local_chart(x,orientation=1,beta=0.):
    """s=e*(x+beta*x*x/2), e in {-1,+1}; local monotonicity 1+beta*x>0."""
    if orientation not in (-1,1):raise ValueError('Invalid orientation')
    x=np.asarray(x,dtype=float)
    if np.any(1+beta*x<=0.):raise ValueError('Folded chart')
    return orientation*(x+.5*beta*x*x)

def inverse_chart(s,orientation=1,beta=0.):
    """Numerically stable inverse chart on its local monotone branch."""
    if orientation not in (-1,1):raise ValueError('Invalid orientation')
    w=orientation*np.asarray(s,dtype=float)
    disc=1+2*beta*w
    if np.any(disc<=0.):raise ValueError('Outside local chart')
    return 2*w/(1+np.sqrt(disc))

def reparam_jet(c2,c3,orientation=1,beta=0.):
    """Derivative chain rule at the stationary barrier: q'(0)=e,q''(0)=-beta."""
    return c2, orientation*(c3-3*c2*beta)

def recover_physical_cubic(c2,transformed_c3,orientation=1,beta=0.):
    return orientation*transformed_c3+3*c2*beta

def midpoint_shift(left,right,barrier):
    return .5*(left+right)-barrier

def root_derived_skew(left,right,qb,delta,c2):
    """Physical oriented finite-threshold estimator: 3*C^2*m/delta -> D3."""
    m=midpoint_shift(left,right,qb)
    return 3*c2*c2*m/delta

def ratio_from_roots(left,right,delta,c2):
    return abs(c2)*(right-left)**2/(8*delta)
