"""Independent exact algebraic controls for pairwise rank-projector couplings."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from generator_math import spectral_generator,constant_orthogonal_gauge
from pairwise_math import PAIRS,pair_spectrum,shapley_pair_attribution,gap_only_and_num_only
class TestPairwise(unittest.TestCase):
 def make(self,seed=3,scale=1.):
  rng=np.random.default_rng(seed)
  a,_=np.linalg.qr(rng.normal(size=(10,10)))
  W=rng.normal(size=(10,10));W=(W-W.T)*.5
  D=np.diag(np.linspace(2.,.4,10)*scale)
  B=D@a.T;Bdot=B@W
  return B,Bdot
 def test_45_pairs(self):
  o=spectral_generator(*self.make());p=pair_spectrum(o)
  self.assertEqual(len(PAIRS),45)
  self.assertAlmostEqual(p['total_K_frob_sq'],o['generator_frobenius']**2,places=10)
 def test_shapley_exact(self):
  a=pair_spectrum(spectral_generator(*self.make(3)))
  b=pair_spectrum(spectral_generator(*self.make(5)))
  x=shapley_pair_attribution(a,b)
  self.assertLess(x['closure_error'],1e-12)
  self.assertLess(abs(np.sum(x['numerator_attribution']+x['gap_attribution'])-(x['final_norm_sq']-x['initial_norm_sq'])),1e-11)
 def test_orthogonal_frame(self):
  B,Bd=self.make(8)
  R,_=np.linalg.qr(np.random.default_rng(9).normal(size=(10,10)))
  x=pair_spectrum(spectral_generator(B,Bd))
  y=pair_spectrum(spectral_generator(*constant_orthogonal_gauge(B,Bd,R)))
  self.assertLess(np.max(abs(x['pair_K_frob_sq']-y['pair_K_frob_sq'])),1e-12)
 def test_gap_only(self):
  before={'numerator':np.ones(45),'gap':np.ones(45)*2}
  after={'numerator':np.ones(45),'gap':np.ones(45)}
  p=shapley_pair_attribution(before,after)
  self.assertAlmostEqual(float(np.sum(p['numerator_attribution'])),0.,places=10)
  self.assertGreater(float(np.sum(p['gap_attribution'])),0.)
 def test_numerator_only(self):
  before={'numerator':np.ones(45),'gap':np.ones(45)*2}
  after={'numerator':np.ones(45)*2,'gap':np.ones(45)*2}
  p=shapley_pair_attribution(before,after)
  self.assertAlmostEqual(float(np.sum(p['gap_attribution'])),0.,places=10)
  self.assertGreater(float(np.sum(p['numerator_attribution'])),0.)
 def test_counterfactual_endpoints(self):
  a=pair_spectrum(spectral_generator(*self.make(7)))
  b=pair_spectrum(spectral_generator(*self.make(12)))
  c=gap_only_and_num_only(a,b)
  self.assertAlmostEqual(c['base']**2,a['total_K_frob_sq'],places=10)
  self.assertAlmostEqual(c['both']**2,b['total_K_frob_sq'],places=10)
if __name__=='__main__':unittest.main()
