import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from pair_math import logistic,wrap_angle,compare,near_decision,so3_angle_deg
class Tests(unittest.TestCase):
 def test_logistic(self):
  self.assertAlmostEqual(logistic(-15),1-logistic(15))
 def test_wrap(self):
  self.assertAlmostEqual(wrap_angle(2*np.pi+.12),.12)
 def test_same_projector_ignore_gauge(self):
  A=np.eye(10)[:,:3]; B=A@np.diag([-1,1,-1]);y=np.zeros(11)
  p=compare({'state':y,'S':A@A.T,'A':A,'R':np.eye(3),'sigma':.2,'energy':0},
            {'state':y,'S':B@B.T,'A':B,'R':np.eye(3),'sigma':.8,'energy':0},np.ones(3))
  self.assertLess(p['triad_projector_frobenius_gap'],1e-14)
  self.assertLess(p['max_triad_principal_angle_deg'],1e-7)
 def test_near_locus_requires_time_gap(self):
  p={'delta_sigma':.01,'x_gap_over_span':0,'locus_xyz_scaled_gap':0}
  self.assertEqual(near_decision(p), (False,False))
 def test_SO3_polar_comp(self):
  self.assertAlmostEqual(so3_angle_deg(np.eye(3),np.eye(3)),0)
if __name__=='__main__':unittest.main()
