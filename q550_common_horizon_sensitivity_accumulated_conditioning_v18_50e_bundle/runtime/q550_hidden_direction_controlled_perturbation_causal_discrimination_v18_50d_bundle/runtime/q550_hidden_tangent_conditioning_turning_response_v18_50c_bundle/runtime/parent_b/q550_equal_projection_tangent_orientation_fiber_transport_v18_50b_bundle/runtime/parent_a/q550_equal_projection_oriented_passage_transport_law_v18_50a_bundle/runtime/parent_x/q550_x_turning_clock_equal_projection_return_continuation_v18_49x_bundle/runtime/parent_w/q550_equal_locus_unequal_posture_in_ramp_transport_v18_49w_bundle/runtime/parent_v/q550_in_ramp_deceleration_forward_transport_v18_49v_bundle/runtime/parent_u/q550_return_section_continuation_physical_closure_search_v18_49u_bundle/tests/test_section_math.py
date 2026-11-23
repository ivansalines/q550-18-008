import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from section_math import residual,metrics,vector_scores,strict_gate
class TestMatching(unittest.TestCase):
 def test_exact_reversal(self):
  a=np.array([.1,.2,.3,.4,.5,.6,.7,.8,.9,1.,1.1]);b=a.copy();b[[1,3,5,7,9]]*=-1
  self.assertLess(metrics(a,b)['full'],1e-14)
 def test_periodic_lift(self):
  a=np.zeros(11);b=np.zeros(11);b[10]=2*np.pi
  self.assertLess(metrics(a,b)['config'],1e-12)
  self.assertAlmostEqual(metrics(a,b)['unwrapped_theta_turns'],1)
 def test_joint_vectorization(self):
  a=np.ones(11);b=a.copy();b[[1,3,5,7,9]]*=-1
  c,v,f=vector_scores([a],[b]);self.assertAlmostEqual(float(f[0,0]),0)
 def test_no_closure_from_geometry_alone(self):
  d={'config':0,'velocity':1,'energy_difference':0,'spectral_projector_distance':0,'minimum_relative_gap':.1,'unwrapped_theta_turns':0}
  self.assertFalse(strict_gate(d,dict(config=1e-4,velocity=1e-4,energy=1e-5,projector=1e-3,spectral_gap=1e-6,phase_lift_turns=1e-3)))
 def test_no_spectral_imputation(self):
  d={'config':0,'velocity':0,'energy_difference':0,'spectral_projector_distance':None,'minimum_relative_gap':None}
  self.assertFalse(strict_gate(d,dict(config=1e-4,velocity=1e-4,energy=1e-5,projector=1e-3,spectral_gap=1e-6)))
if __name__=='__main__':unittest.main()
