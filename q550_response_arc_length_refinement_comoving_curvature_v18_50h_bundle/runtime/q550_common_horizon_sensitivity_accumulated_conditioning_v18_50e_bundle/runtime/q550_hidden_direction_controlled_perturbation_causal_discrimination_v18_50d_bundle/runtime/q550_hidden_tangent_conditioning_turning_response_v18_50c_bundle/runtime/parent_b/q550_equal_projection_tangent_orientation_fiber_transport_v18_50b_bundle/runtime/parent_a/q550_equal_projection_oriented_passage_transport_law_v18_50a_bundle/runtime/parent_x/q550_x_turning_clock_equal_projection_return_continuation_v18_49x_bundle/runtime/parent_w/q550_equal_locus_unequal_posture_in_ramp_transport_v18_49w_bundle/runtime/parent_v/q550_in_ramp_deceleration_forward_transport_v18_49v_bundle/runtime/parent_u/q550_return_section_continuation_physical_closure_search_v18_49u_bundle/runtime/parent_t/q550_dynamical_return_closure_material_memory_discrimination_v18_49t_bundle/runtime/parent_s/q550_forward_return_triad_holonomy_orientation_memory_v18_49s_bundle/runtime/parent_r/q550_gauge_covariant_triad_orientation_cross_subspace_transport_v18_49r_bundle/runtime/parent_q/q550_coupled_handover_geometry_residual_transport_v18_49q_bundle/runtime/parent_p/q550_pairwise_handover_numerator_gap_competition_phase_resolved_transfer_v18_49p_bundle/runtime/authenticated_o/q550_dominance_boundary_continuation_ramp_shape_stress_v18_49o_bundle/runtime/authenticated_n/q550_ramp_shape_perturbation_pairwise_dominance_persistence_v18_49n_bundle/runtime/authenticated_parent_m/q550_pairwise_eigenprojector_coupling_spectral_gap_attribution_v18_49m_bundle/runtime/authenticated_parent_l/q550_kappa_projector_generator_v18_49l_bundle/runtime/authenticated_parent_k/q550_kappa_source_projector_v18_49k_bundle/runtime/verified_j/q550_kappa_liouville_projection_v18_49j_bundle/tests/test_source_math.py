import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from source_math import log_kinetic_density,log_density_gradient,occupation,rate_occupation_split,alternate_volume_shift
from kinetic_metric import embedding_and_jac
class TestLiouvilleProjection(unittest.TestCase):
 def test_exact_density(self):
  y=np.array([.4,.1,.8,.2,-.2,-.3,1.2,.1,.35,-.04])
  for tau in (.5,1.,2.):
   _,J=embedding_and_jac(y,1.4,tau)
   self.assertAlmostEqual(np.linalg.slogdet(J)[1],log_kinetic_density(y,1.4,tau),places=12)
 def test_gradient_finite_difference(self):
  y=np.array([.4,.1,.8,.2,-.2,-.3,1.2,.1,.35,-.04]);grad=log_density_gradient(y)
  for i in range(10):
   eps=1e-6;aa=y.copy();bb=y.copy();aa[i]+=eps;bb[i]-=eps
   self.assertLess(abs((log_kinetic_density(aa,1.4)-log_kinetic_density(bb,1.4))/(2*eps)-grad[i]),3e-9)
 def test_occupations_complete(self):
  a=np.eye(10);u=np.arange(1,11,dtype=float);self.assertAlmostEqual(occupation(u,a).sum(),1.)
 def test_projector_rate_balance(self):
  q=np.linspace(0,1,101);u=np.column_stack([np.cos(q),np.sin(q),np.zeros((len(q),8))]);a=np.tile(np.eye(10),(len(q),1,1))
  p,dp,di,ba=rate_occupation_split(q,u,a)
  self.assertLess(np.max(np.abs(dp[2:-2]-di[2:-2]-ba[2:-2])),2e-4)
  self.assertLess(np.max(abs(ba)),1e-12)
 def test_projector_sign_invariance(self):
  q=np.linspace(0,1,51);u=np.column_stack([np.cos(q),np.sin(q),np.zeros((len(q),8))]);a=np.tile(np.eye(10),(len(q),1,1))
  x=rate_occupation_split(q,u,a);a[::3,:,0]*=-1;y=rate_occupation_split(q,u,a)
  for i in (0,1,2,3):self.assertTrue(np.allclose(x[i],y[i],atol=1e-10))
 def test_alternative_volume_form(self):
  a=np.zeros(10);b=np.zeros(10);b[0]=.25;b[4]=-.3
  self.assertAlmostEqual(alternate_volume_shift(a,b,2.),1.1)
 def test_density_tau_constant(self):
  a=np.zeros(10);b=a.copy();b[0]=.3
  self.assertAlmostEqual(log_kinetic_density(b,1.,2.)-log_kinetic_density(a,1.,2.),
   log_kinetic_density(b,1.,.5)-log_kinetic_density(a,1.,.5))
if __name__=='__main__':unittest.main()
