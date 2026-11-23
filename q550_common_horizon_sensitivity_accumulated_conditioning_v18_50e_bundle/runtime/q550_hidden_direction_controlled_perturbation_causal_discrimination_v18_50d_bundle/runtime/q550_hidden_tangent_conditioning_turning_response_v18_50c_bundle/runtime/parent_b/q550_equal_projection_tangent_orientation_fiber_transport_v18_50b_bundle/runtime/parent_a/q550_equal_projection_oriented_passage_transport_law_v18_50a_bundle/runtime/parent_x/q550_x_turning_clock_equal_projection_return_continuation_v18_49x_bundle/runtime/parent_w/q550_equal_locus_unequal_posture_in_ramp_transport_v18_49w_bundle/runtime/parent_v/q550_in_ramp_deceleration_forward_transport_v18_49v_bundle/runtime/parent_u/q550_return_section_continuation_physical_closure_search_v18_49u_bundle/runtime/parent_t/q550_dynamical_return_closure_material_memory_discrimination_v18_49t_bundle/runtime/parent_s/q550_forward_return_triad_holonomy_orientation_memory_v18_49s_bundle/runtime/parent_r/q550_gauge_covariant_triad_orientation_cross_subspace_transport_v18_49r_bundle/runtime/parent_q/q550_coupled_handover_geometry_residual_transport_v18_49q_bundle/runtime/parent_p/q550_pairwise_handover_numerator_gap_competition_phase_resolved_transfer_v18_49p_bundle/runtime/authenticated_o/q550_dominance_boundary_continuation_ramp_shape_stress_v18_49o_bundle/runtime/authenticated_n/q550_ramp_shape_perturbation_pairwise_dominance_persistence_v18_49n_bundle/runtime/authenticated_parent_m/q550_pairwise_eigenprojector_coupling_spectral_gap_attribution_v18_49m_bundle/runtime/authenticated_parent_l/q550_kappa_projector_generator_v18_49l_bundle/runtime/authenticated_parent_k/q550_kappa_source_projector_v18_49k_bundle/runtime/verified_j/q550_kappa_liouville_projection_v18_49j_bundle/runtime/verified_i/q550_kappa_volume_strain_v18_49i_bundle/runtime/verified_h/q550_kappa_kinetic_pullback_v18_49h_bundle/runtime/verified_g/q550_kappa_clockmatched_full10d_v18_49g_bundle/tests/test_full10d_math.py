"""Independent identities of the v18.49g geometry calculations."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from full10d_math import spherical_path,chart_covariance_error,unit,metric_cos,project_outside_basis
class FullOrientationTests(unittest.TestCase):
 def test_great_circle(self):
  t=np.linspace(0,np.pi/4,81)
  p=np.column_stack([np.cos(t),np.sin(t),np.zeros_like(t)])
  m=spherical_path(p)
  self.assertAlmostEqual(m['length_deg'],45,places=6)
  self.assertAlmostEqual(m['endpoint_deg'],45,places=6)
 def test_bent_path_excess_positive(self):
  p=np.array([[1.,0,0],[.8,.6,0],[.8,0,.6],[1.,0,0]])
  m=spherical_path(p)
  self.assertGreater(m['length_deg'],90)
  self.assertLess(m['endpoint_deg'],1e-5)
 def test_chart_metric_covariance(self):
  t=np.linspace(0,1,30)
  p=np.column_stack([np.cos(t),np.sin(t),.2*t,.03*t*t,np.ones_like(t)])
  self.assertLess(chart_covariance_error(p),2e-5)
 def test_norm_and_projector(self):
  e=np.eye(10)[:2].T
  v=np.arange(10.)
  h=project_outside_basis(v,e)
  self.assertAlmostEqual(e.T[0]@h,0)
  self.assertAlmostEqual(e.T[1]@h,0)
 def test_reverse_path_same_scalar(self):
  t=np.linspace(0,1.1,50)
  p=np.column_stack([np.cos(t),np.sin(t),.02*t])
  a=spherical_path(p);b=spherical_path(p[::-1])
  self.assertAlmostEqual(a['length_deg'],b['length_deg'],places=8)
  self.assertAlmostEqual(a['endpoint_deg'],b['endpoint_deg'],places=8)
 def test_metric_cos(self):
  a=np.array([1.,0.]);b=np.array([0.,2.]);m=np.diag([2.,.5])
  self.assertAlmostEqual(metric_cos(a,b,m),0.)
if __name__=='__main__':unittest.main()
