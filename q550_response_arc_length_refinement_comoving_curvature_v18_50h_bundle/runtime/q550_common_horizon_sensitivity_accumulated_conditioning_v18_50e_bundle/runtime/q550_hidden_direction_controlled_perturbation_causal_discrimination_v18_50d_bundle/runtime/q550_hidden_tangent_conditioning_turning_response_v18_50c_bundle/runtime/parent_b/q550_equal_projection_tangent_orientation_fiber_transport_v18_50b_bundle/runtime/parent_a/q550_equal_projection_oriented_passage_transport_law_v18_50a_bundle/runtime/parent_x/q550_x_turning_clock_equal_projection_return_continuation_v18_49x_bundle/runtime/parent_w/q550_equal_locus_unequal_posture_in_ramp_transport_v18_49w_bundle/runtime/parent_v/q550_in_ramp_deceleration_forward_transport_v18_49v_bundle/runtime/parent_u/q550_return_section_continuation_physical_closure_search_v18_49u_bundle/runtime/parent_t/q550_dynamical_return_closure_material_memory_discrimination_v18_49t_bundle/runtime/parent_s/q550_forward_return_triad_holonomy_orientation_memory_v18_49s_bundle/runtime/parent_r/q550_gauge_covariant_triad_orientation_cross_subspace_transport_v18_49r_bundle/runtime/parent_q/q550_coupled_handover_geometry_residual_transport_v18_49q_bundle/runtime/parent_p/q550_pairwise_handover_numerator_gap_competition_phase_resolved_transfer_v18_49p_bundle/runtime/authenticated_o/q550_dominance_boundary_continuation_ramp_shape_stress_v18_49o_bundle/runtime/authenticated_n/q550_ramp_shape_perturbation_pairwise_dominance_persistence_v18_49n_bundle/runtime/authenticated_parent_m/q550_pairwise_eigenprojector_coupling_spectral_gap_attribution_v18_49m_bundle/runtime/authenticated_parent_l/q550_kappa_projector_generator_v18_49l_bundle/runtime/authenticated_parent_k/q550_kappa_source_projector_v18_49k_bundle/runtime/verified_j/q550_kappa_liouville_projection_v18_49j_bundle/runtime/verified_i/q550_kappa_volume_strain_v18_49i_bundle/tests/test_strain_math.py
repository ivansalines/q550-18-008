import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from strain_math import factor,fixed_metric_volume,line_angle,subspace_angles,anisotropic_length,volume_form_coordinate_change
from kinetic_metric import embedding_and_jac,material_metric
class StrainMathTests(unittest.TestCase):
 def test_polar_kinetic_jacobian(self):
  y=np.array([.3,.1,.2,.3,-.1,.2,.9,-.3,.2,.4])
  H,J=embedding_and_jac(y,1.2,1.0);h=1e-6
  for j in range(10):
   delta=np.zeros(10);delta[j]=h
   d=(embedding_and_jac(y+delta,1.2)[0]-embedding_and_jac(y-delta,1.2)[0])/(2*h)
   self.assertLess(np.max(abs(d-J[:,j])),2e-9)
 def test_isotropic_expansion(self):
  f=np.diag([2.,3.,1.]+[.8]*7);sig,ax,sgn,log=factor(f)
  self.assertAlmostEqual(log,np.sum(np.log(sig)),places=12)
  self.assertAlmostEqual(np.exp(log),abs(np.linalg.det(f)),places=12)
 def test_metric_volume_chart(self):
  d0=np.diag(np.linspace(.4,2.,10));d1=np.diag(np.linspace(2.,.3,10))
  f=np.eye(10)+.2*np.eye(10,k=1);G0=np.diag(np.linspace(.3,2,10));G1=np.diag(np.linspace(2,.4,10))
  self.assertLess(volume_form_coordinate_change(f,G0,G1,d0,d1),1e-12)
 def test_metric_volume_tau(self):
  y=np.array([.3,.1,.2,.3,-.1,.2,.9,-.3,.2,.4]);z=y+.05
  f=np.eye(10)+.03*np.eye(10,k=1)
  logs=[]
  for tau in (.5,1.,2.):
   _,j0=embedding_and_jac(y,1.2,tau);_,j1=embedding_and_jac(z,1.2,tau)
   logs.append(fixed_metric_volume(f,j0,j1))
  self.assertLess(np.ptp(logs),2e-14)
 def test_subspace_and_sign_free_axes(self):
  u=np.eye(10)[:,:3];w=u@np.diag([-1,1,-1]);self.assertLess(max(subspace_angles(u,w)),2e-6)
  self.assertLess(line_angle(u[:,0],-w[:,0]),1e-5)
 def test_metric_stretch(self):
  f=np.diag([3.,2.]+[1.]*8);s,u,_,_=factor(f)
  self.assertAlmostEqual(anisotropic_length(s,u,np.eye(10)[0]),3,places=12)
 def test_gauge_strain(self):
  from strain_math import gauge_strain_check
  y=np.array([.3,.1,.2,.3,-.1,.2,.9,-.3,.2,.4]);f=np.eye(10)+.04*np.eye(10,k=1)
  self.assertLess(gauge_strain_check(f,material_metric(y,1.2),material_metric(y+.1,1.2),y,y+.1),2e-13)
if __name__=='__main__':unittest.main()
