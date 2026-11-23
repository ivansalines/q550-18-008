import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from observer_math import dual_field,diagonal_covariance,shape_gradient,projective_angle
class CheckDual(unittest.TestCase):
 def test_dual_identity(self):
  j=np.array([[.1,2.],[-.7,.3]]);g=np.array([3.,5.]);v=np.array([7.,11.]);dg,dv=dual_field(j,g,v)
  self.assertAlmostEqual(float(dg@v+g@dv),0.,places=11)
 def test_multichannel(self):
  j=np.array([[1.,2.],[3.,4.]]);g=np.array([[1.,0.],[0.,2.]]);v=np.array([1.,-3.]);dg,dv=dual_field(j,g,v)
  np.testing.assert_allclose(dg.T@v+g.T@dv,0,atol=1e-13)
 def test_covariance(self):
  g=np.array([3.,-2.]);v=np.array([.5,4.]);self.assertAlmostEqual(diagonal_covariance(g,v,[2.,.3]),0.,places=13)
 def test_shape_gradient(self):
  a=np.zeros(11);b=np.zeros(11);a[0]=.3;a[4]=-.2;a[8]=.5
  grad,d=shape_gradient(a,b)
  for k in [0,4,8]:
   h=1e-6;aa=a.copy();aa[k]+=h;bb=a.copy();bb[k]-=h
   fd=(shape_gradient(aa,b)[1]-shape_gradient(bb,b)[1])/(2*h)
   self.assertAlmostEqual(grad[k],fd,places=8)
 def test_angles(self):
  self.assertAlmostEqual(projective_angle([1,0],[-1,0]),0.,places=10)
  self.assertAlmostEqual(projective_angle([1,0],[0,1]),90.,places=10)
if __name__=='__main__':unittest.main()
