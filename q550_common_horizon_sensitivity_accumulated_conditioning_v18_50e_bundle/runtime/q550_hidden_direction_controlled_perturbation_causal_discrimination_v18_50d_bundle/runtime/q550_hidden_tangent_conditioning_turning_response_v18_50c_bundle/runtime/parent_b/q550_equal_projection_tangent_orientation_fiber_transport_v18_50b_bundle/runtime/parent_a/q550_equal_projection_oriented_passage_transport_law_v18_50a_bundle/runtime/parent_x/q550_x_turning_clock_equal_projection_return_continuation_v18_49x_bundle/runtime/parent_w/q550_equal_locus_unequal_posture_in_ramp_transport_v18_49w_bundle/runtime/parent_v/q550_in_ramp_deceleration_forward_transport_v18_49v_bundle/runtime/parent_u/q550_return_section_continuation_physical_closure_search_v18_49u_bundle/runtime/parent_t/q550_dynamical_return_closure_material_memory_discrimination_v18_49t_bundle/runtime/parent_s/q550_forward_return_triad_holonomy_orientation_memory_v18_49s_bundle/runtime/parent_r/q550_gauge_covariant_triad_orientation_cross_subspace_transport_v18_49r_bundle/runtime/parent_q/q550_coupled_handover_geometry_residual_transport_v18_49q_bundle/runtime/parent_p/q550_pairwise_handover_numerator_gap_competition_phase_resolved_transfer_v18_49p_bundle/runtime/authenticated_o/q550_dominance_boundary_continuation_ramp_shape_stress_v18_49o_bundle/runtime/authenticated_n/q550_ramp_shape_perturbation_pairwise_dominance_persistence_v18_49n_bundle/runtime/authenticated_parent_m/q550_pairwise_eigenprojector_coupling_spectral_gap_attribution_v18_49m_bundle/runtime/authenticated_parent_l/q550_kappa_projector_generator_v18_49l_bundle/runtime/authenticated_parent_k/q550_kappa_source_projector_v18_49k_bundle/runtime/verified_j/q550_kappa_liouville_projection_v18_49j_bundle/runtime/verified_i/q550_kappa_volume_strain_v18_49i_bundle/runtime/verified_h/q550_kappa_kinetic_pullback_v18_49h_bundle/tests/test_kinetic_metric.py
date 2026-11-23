"""Unit tests for Q550 exact kinetic pullback and S9 curvature."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from scipy.linalg import eigh
from kinetic_metric import embedding_and_jac,kinetic_energy,material_metric,nonlinear_chart_gauge
from curvature_math import path_angles,sphere_curvature,unit
class TestMetric(unittest.TestCase):
 def setUp(self):self.y=np.array([.6,.3,.4,-.1,.9,-.2,.8,.4,-.6,.15]);self.mx=1.7
 def test_embedded_cartesian_kinetic(self):
  h,j=embedding_and_jac(self.y,self.mx);r1=np.exp(self.y[0]);r2=np.exp(self.y[4]);x=1/(1+np.exp(-self.y[8]));
  true=.5*(r1*r1*(self.y[1]**2+self.y[3]**2)+r2*r2*(self.y[5]**2+self.y[7]**2)+self.mx*(x*(1-x)*self.y[9])**2)
  self.assertAlmostEqual(kinetic_energy(self.y,self.mx),true,places=13)
 def test_jacobian_independent_difference(self):
  h,j=embedding_and_jac(self.y,self.mx)
  for i in range(10):
   v=np.zeros(10);v[i]=1e-6
   fd=(embedding_and_jac(self.y+v,self.mx)[0]-embedding_and_jac(self.y-v,self.mx)[0])/(2e-6)
   self.assertLess(np.max(np.abs(fd-j[:,i])),3e-10)
 def test_metric_positive(self):self.assertGreater(np.linalg.eigvalsh(material_metric(self.y,self.mx))[0],1e-8)
 def test_theta_periodicity(self):
  y=self.y.copy();y[2]+=2*np.pi
  self.assertLess(np.max(abs(embedding_and_jac(y,self.mx)[0]-embedding_and_jac(self.y,self.mx)[0])),1e-12)
 def test_eigenvalue_covariance_nonlinear_chart(self):
  y1=self.y+.03*np.arange(10);F=np.eye(10)+np.eye(10,k=1)*.015
  G0=material_metric(self.y,self.mx);G1=material_metric(y1,self.mx)
  ev=eigh(F.T@G1@F,G0,eigvals_only=True)
  FF,gg0,gg1=nonlinear_chart_gauge(F,G0,G1,self.y,y1)
  ev2=eigh(FF.T@gg1@FF,gg0,eigvals_only=True)
  np.testing.assert_allclose(ev2,ev,rtol=2e-12,atol=2e-12)
 def test_metric_scale_is_a_choice(self):
  a=material_metric(self.y,self.mx,.5);b=material_metric(self.y,self.mx,2.)
  self.assertGreater(np.linalg.norm(a-b),1e-2)
 def test_spherical_geodesic_curvature(self):
  q=np.linspace(0,.7,201);v=np.zeros((len(q),10));v[:,0]=np.cos(q);v[:,1]=np.sin(q)
  self.assertLess(sphere_curvature(v,q)['maximum'],1e-8)
 def test_non_geodesic_and_direction_reversal(self):
  q=np.linspace(-.1,.7,301);v=np.zeros((len(q),10));v[:,0]=np.cos(q);v[:,1]=np.sin(q);v[:,2]=.3*np.sin(2*q)
  c=sphere_curvature(v,q);self.assertGreater(c['median'],.05)
  a=path_angles(v);b=path_angles(v[::-1]);self.assertAlmostEqual(a['excess_deg'],b['excess_deg'],places=12)
if __name__=='__main__':unittest.main()
