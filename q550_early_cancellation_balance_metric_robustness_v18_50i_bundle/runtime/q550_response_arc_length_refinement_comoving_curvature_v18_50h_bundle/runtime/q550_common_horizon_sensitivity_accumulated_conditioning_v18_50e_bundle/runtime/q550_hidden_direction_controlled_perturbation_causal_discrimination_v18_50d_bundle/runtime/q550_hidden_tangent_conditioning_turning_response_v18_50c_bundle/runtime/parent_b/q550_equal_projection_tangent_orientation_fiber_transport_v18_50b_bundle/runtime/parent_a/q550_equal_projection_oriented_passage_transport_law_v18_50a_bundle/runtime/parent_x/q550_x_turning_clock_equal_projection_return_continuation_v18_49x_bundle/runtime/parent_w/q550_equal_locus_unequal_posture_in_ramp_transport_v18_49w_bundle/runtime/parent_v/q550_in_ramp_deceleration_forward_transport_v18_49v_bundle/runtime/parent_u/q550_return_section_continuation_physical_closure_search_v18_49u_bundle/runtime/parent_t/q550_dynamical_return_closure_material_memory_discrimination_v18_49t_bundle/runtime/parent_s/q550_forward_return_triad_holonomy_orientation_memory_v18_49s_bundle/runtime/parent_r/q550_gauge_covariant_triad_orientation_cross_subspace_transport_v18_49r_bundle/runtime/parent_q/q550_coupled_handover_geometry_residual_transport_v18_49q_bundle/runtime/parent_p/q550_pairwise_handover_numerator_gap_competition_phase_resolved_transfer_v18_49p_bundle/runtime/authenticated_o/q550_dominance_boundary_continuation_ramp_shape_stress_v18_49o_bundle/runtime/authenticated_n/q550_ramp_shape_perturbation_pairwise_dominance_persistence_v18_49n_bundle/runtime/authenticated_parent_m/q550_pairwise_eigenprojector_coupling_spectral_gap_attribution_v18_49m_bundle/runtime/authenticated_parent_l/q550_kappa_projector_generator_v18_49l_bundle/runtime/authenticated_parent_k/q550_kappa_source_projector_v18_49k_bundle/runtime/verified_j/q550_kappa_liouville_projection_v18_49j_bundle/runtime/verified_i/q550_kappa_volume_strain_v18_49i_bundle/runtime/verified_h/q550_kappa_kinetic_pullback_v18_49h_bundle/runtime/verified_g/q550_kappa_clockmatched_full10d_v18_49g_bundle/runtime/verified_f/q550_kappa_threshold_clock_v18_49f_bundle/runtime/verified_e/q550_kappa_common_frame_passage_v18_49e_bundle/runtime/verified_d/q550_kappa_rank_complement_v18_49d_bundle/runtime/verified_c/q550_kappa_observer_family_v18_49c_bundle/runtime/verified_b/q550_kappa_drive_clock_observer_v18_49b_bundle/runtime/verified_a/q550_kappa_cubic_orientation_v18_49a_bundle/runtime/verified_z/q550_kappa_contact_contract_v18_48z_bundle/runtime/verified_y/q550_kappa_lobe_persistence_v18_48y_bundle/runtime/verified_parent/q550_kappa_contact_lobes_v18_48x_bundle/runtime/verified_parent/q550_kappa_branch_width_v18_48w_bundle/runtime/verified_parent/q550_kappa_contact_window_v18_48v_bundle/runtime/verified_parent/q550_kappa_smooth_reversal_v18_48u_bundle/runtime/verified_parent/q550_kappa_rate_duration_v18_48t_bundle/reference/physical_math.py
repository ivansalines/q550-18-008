#!/usr/bin/env python3
"""Physical-support mechanical balance from the ORIGINAL Q550 RHS.

Time tau: d/dxi = (2*pi*slope/x) * d/dtau for the material coordinates.
The externally imposed drive control in tau is Theta_dot = +/-x (or 0).
The state y=(log rho1,v1,theta1,omega1,log rho2,v2,theta2,omega2,
             logit(x),v_z,Theta); v_i and omega_i are tau velocities,
             x_dot=x(1-x)*v_z.

The selected mechanical energy is not asserted to be a conserved total energy:
E=T+U(rho1)+U(rho2)+V_barrier(x)+kappa0*x*rho1*rho2*cos(delta).
Its exact balance includes a nonconservative x force, imposed drive work,
and damping. Every term is explicitly derived from the historical equations.
"""
from __future__ import annotations
import math
import numpy as np
ALPHA,BETA,GAMMA=1.,.8,.2

def physical_data(y,kappa,p):
    l1,v1,t1,w1,l2,v2,t2,w2,z,vz,Theta=map(float,y)
    rho1,rho2=math.exp(l1),math.exp(l2)
    # Numerically stable logistic function.
    x=1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))
    g=x*(1-x);xdot=g*vz
    delta=t1+t2-p.phi0-Theta
    return rho1,rho2,x,g,xdot,delta,math.sin(delta),math.cos(delta)

def energy(y,kappa,p):
    r1,r2,x,g,xd,delta,sd,cd=physical_data(y,kappa,p)
    v1,w1,v2,w2=float(y[1]),float(y[3]),float(y[5]),float(y[7])
    def U(r):return ALPHA*r*r-BETA*r**3+GAMMA*r**4+.5*p.e_reserve**2/r**2
    kin=.5*(r1*r1*(v1*v1+w1*w1)+r2*r2*(v2*v2+w2*w2)+p.m_x*xd*xd)
    barrier=-p.barrier_B*math.log(x*(1-x))
    return kin+U(r1)+U(r2)+barrier+kappa*x*r1*r2*cd

def power_terms(y,kappa,p,slope,clock_sign):
    """Return power (dE/dxi) contributions in signed xi, ordered:
    drive, radial damping, x damping, x-nonconservative work.
    This is an EXACT differential identity in real arithmetic for the
    historical 11D RHS under Theta'=clock_sign*2*pi*slope.
    """
    r1,r2,x,g,xd,delta,sd,cd=physical_data(y,kappa,p)
    q=(2*math.pi*slope)/x
    rdot1,rdot2=r1*float(y[1]),r2*float(y[5])
    thetadot_tau=clock_sign*x
    phase_drive=kappa*x*r1*r2*sd*thetadot_tau
    damping_r=-p.gamma_rho*(rdot1*rdot1+rdot2*rdot2)
    damping_x=-p.gamma_x*xd*xd
    source_x=xd*r1*r2*(p.mu_x*sd+kappa*cd)
    return q*np.array([phase_drive,damping_r,damping_x,source_x],float)

def rhs_from_original(y,kappa,p,slope,clock_sign,support,audit):
    """Original original-support source function; change ONLY drive clock."""
    f=slope*np.asarray(support.support_rhs_float(y,kappa0=kappa,params=p,audit=audit),float)
    f[10]=clock_sign*(2*math.pi*slope)
    return f

def signed_displacement(a,b,scale=None):
    """Endpoint displacement in physical coordinates (phase modulo 2*pi)."""
    a=np.asarray(a,float);b=np.asarray(b,float)
    d=a-b
    for i in (2,6,10):d[i]=((d[i]+math.pi)%(2*math.pi))-math.pi
    if scale is None:
        return float(np.linalg.norm(d))
    return float(np.linalg.norm(d/np.r_[np.asarray(scale,float),1.]))

def physical_shape_distance(a,b):
    """Dimensionless geometry-only separation, not a material Riemann metric."""
    r1a,r2a,xa,*_=physical_data(a,0,type('Params',(),{'phi0':0.})())
    r1b,r2b,xb,*_=physical_data(b,0,type('Params',(),{'phi0':0.})())
    return math.sqrt((math.log(r1a/r1b))**2+(math.log(r2a/r2b))**2+(xa-xb)**2)
