"""Q550 v18.50k -- fixed-chart geometric identities, not physical constitutive laws.

C(b,c) = 1 - ||L+T||/(||L||+||T||), where b=||T||/||L|| and
c=<L,T>/(||L|| ||T||) in a declared positive-definite fixed metric.
u=ln b, theta=acos c, H=sin(theta/2)/cosh(u/2).
C=1-sqrt(1-H**2).  H is symmetric under interchange L <-> T.
For b>0,-1<c<1, H>0:
d ln H/dxi = orientation_gain + imbalance_cost,
orientation_gain=-cprime/[2(1-c)],
imbalance_cost=-(b-1)*bprime/[2*b*(b+1)].
At b=1 imbalance_cost is exactly zero, regardless of bprime.
"""
from __future__ import annotations
import math


def cancellation(b,c):
    return 1-math.sqrt(max(0.0,1+b*b+2*b*c))/(1+b)

def gate_fields(b,c,bprime,cprime):
    if not(b>0 and -1<c<1):
        raise ValueError('Require positive b and nondegenerate angle')
    u=math.log(b)
    theta=math.acos(c)
    h=math.sin(theta/2)/math.cosh(u/2)
    c_gate=1-math.sqrt(max(0.0,1-h*h))
    orient=-cprime/(2*(1-c))
    imbalance=-(b-1)*bprime/(2*b*(b+1))
    log_gate_rate=orient+imbalance
    return dict(u=u,theta=theta,theta_degrees=math.degrees(theta),
       h=h,cancellation=c_gate,orientation_log_gain=orient,
       imbalance_log_cost=imbalance,log_gate_rate=log_gate_rate,
       h_rate=h*log_gate_rate,
       c_rate=h*h*log_gate_rate/math.sqrt(1-h*h))
