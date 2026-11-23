"""Independent mpmath second-order automatic differentiation of ORIGINAL support RHS.

No finite differences. Derives F0 and coefficient K directly from the physical
11D model's equations. Input double samples are exact binary values lifted to mp.
This is a numerical high-precision recomputation, not an interval proof.
"""
from __future__ import annotations
import mpmath as mp

N=11
class Jet:
    def __init__(self,x,g=None,H=None):
        self.x=mp.mpf(x)
        self.g=g if g is not None else [mp.mpf('0')]*N
        self.H=H if H is not None else [[mp.mpf('0') for _ in range(N)] for _ in range(N)]
    @classmethod
    def var(cls,val,index):
        g=[mp.mpf('0')]*N;g[index]=mp.mpf('1')
        return cls(val,g)
    def __add__(self,b):
        b=_jet(b);return Jet(self.x+b.x,[a+c for a,c in zip(self.g,b.g)],[[self.H[i][j]+b.H[i][j] for j in range(N)] for i in range(N)])
    __radd__=__add__
    def __neg__(self):return Jet(-self.x,[-z for z in self.g],[[-v for v in row] for row in self.H])
    def __sub__(self,b):return self+-_jet(b)
    def __rsub__(self,b):return _jet(b)+-self
    def __mul__(self,b):
        b=_jet(b)
        return Jet(self.x*b.x,[self.g[i]*b.x+b.g[i]*self.x for i in range(N)],
          [[self.H[i][j]*b.x+b.H[i][j]*self.x+self.g[i]*b.g[j]+b.g[i]*self.g[j]
             for j in range(N)] for i in range(N)])
    __rmul__=__mul__
    def compose(self,val,d,dd):
        return Jet(val,[d*a for a in self.g],[[d*self.H[i][j]+dd*self.g[i]*self.g[j] for j in range(N)] for i in range(N)])
    def inv(self):return self.compose(1/self.x,-1/self.x**2,2/self.x**3)
    def __truediv__(self,b):return self*_jet(b).inv()
    def __rtruediv__(self,b):return _jet(b)*self.inv()
    def __pow__(self,p):
        p=mp.mpf(p);return self.compose(self.x**p,p*self.x**(p-1),p*(p-1)*self.x**(p-2))
    def exp(self):
        v=mp.exp(self.x);return self.compose(v,v,v)
    def sin(self):return self.compose(mp.sin(self.x),mp.cos(self.x),-mp.sin(self.x))
    def cos(self):return self.compose(mp.cos(self.x),-mp.sin(self.x),-mp.cos(self.x))
def _jet(a):return a if isinstance(a,Jet) else Jet(a)

def model_jets(y,kap,params,slope):
    q=[Jet.var(mp.mpf(float(v)),i) for i,v in enumerate(y)]
    y1,v1,t1,w1,y2,v2,t2,w2,z,vz,TH=q
    p=mp.pi;rho1=y1.exp();rho2=y2.exp();x=1/(1+(-z).exp());g=x*(1-x)
    er=mp.mpf(params.e_reserve); gamma_r=mp.mpf(params.gamma_rho)
    gam_x=mp.mpf(params.gamma_x); barrier=mp.mpf(params.barrier_B)
    mu=mp.mpf(params.mu_x);mass=mp.mpf(params.m_x);phi=mp.mpf(params.phi0)
    delta=t1+t2-phi-TH
    coupling=[Jet(0) for _ in range(N)]
    coupling[1]=-2*p*(y2-y1).exp()*delta.cos()
    coupling[3]=+2*p*(y2-y1).exp()*delta.sin()
    coupling[5]=-2*p*(y1-y2).exp()*delta.cos()
    coupling[7]=+2*p*(y1-y2).exp()*delta.sin()
    def du(rho):return 2*rho-mp.mpf('2.4')*rho**2+mp.mpf('0.8')*rho**3-er**2/rho**3
    def dv(xx):return -barrier*(1/xx-1/(1-xx))
    qc=2*p/x
    base=[Jet(0) for _ in range(N)]
    base[0]=qc*v1
    base[1]=qc*(w1**2-du(rho1)/rho1-gamma_r*v1-v1**2)
    base[2]=qc*w1
    base[3]=qc*(-2*v1*w1)
    base[4]=qc*v2
    base[5]=qc*(w2**2-du(rho2)/rho2-gamma_r*v2-v2**2)
    base[6]=qc*w2
    base[7]=qc*(-2*v2*w2)
    base[8]=qc*vz
    base[9]=qc*((-dv(x)+mu*rho1*rho2*delta.sin()-gam_x*g*vz)/(mass*g)-(1-2*x)*vz**2)
    base[10]=Jet(2*p)
    scale=mp.mpf(slope);k=mp.mpf(kap)
    return [scale*(b+k*c) for b,c in zip(base,coupling)],[scale*b for b in base],[scale*k*c for c in coupling]

def high_precision_matrices(y,kappa,params,slope,chart_scale,dps=75):
    with mp.workdps(dps):
        ff,bb,cc=model_jets(y,kappa,params,slope)
        sc=[mp.mpf(float(x)) for x in chart_scale]
        Lb=mp.matrix(10,10);Lc=mp.matrix(10,10)
        for j in range(10):
            for i in range(10):
                Lb[j,i]=sc[j]/sc[i]*sum(bb[i].H[a][j]*ff[a].x for a in range(11))
                Lc[j,i]=sc[j]/sc[i]*sum(cc[i].H[a][j]*ff[a].x for a in range(11))
        return Lb,Lc

def hp_singular_values(M):
    # mp.svd_r computes SVD without loss of precision from squaring conditioning.
    _,s,_=mp.svd_r(M);return [s[i] for i in range(len(s))]
