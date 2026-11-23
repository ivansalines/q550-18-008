import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from rhythm_math import (projective_angle,projection_loss,lag_correlation,
                         reverse_projector_symmetry,directed_loss,cancellation_signals,score_best)
class RhythmMathTests(unittest.TestCase):
 def test_projective_sign(self):
  x=np.array([1.,0.,0.]);self.assertAlmostEqual(projective_angle(x,-x),0.)
 def test_projective_quarter(self):
  self.assertAlmostEqual(projective_angle([1.,0],[0.,1.]),90.)
 def test_projector_reversal(self):
  p=np.diag([1.,0.,0.]);q=np.diag([0.,1.,0.]);f,b,e=reverse_projector_symmetry(p,q);self.assertAlmostEqual(f,b);self.assertEqual(e,0.)
 def test_frozen_observer_reverse_antisymmetry(self):
  p=np.diag([1.,0.]);q=np.diag([0.,1.]);x=np.array([1.,0.]);a,b=directed_loss(x,x,p,q);self.assertAlmostEqual(a,-b)
 def test_correlations_known_lag(self):
  rng=np.random.default_rng(4);x=rng.normal(size=40);y=np.r_[np.zeros(2),x[:-2]]
  b=score_best(lag_correlation(x,y));self.assertEqual(b['lag_steps'],2);self.assertAlmostEqual(b['correlation'],1.,places=11)
 def test_missing_lag(self):
  res=lag_correlation(np.zeros(20),np.ones(20));self.assertTrue(np.isnan(res[0]['correlation']))
 def test_zero_coupling(self):
  b=np.eye(2);c=np.zeros((2,2));r=cancellation_signals(b,c,[1,0]);self.assertTrue(r['coupling_null']);self.assertAlmostEqual(r['R'],1.)
 def test_true_opposition(self):
  b=np.eye(2);c=-.999*np.eye(2);r=cancellation_signals(b,c,[1,0]);self.assertGreater(r['R'],1000.);self.assertLess(r['opposition_cosine'],-.99999)
if __name__=='__main__':unittest.main()
