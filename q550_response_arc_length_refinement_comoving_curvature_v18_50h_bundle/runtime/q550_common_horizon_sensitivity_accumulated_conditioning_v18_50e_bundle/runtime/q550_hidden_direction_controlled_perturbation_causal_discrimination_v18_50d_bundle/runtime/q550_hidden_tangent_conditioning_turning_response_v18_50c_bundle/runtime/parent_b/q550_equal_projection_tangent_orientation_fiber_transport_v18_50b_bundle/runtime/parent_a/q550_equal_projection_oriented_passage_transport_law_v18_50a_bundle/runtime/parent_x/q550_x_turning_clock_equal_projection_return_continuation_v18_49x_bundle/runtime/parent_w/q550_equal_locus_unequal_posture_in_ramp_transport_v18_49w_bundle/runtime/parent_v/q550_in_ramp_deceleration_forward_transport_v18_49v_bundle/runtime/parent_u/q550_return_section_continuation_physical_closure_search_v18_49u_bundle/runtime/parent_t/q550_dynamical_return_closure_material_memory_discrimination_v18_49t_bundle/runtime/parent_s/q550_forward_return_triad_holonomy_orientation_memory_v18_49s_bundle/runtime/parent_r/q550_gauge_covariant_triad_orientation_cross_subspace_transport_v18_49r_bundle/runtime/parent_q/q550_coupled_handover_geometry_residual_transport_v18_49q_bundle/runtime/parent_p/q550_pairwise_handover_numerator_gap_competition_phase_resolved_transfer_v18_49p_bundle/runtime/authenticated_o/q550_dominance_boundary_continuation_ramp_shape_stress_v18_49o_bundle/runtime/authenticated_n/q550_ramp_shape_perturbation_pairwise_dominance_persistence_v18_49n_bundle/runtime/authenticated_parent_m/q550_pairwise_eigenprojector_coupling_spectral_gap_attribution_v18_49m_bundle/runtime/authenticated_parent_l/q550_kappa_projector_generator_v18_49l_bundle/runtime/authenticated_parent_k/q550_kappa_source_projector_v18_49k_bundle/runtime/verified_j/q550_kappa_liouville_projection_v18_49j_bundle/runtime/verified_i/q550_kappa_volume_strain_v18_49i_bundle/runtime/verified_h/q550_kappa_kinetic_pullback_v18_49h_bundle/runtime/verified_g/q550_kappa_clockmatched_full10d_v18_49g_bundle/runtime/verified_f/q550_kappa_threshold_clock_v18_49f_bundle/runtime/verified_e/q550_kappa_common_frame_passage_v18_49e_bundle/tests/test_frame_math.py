"""Independent algebraic tests of frame, duality and marker orientation."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from frame_math import physical_to_initial,orthonormal_family,common_decomposition,oriented_crossings,passage_pairs,gauge_test
class Tests(unittest.TestCase):
 def test_linear_duality(self):
  rng=np.random.default_rng(91);F=np.eye(10)+.02*rng.normal(size=(10,10))
  g0=rng.normal(size=(5,10));gt=np.linalg.solve(F.T,g0.T).T
  delta=rng.normal(size=10);u,err=physical_to_initial(F,delta,gt,g0)
  self.assertLess(err,1e-13);np.testing.assert_allclose(u,np.linalg.solve(F,delta))
 def test_full_family(self):
  U,s,k=orthonormal_family(np.eye(10),1e-10)
  o=common_decomposition(np.arange(10,dtype=float),U)
  self.assertEqual(k,10);self.assertAlmostEqual(o['hidden'],0.,places=12)
 def test_rank_truncation(self):
  g=np.diag([1.,1e-2,1e-4,1e-6,1e-8,1e-10,1e-12,1e-14,1e-16,1e-18])
  U,s,k=orthonormal_family(g[:5],1e-5);self.assertEqual(k,3)
 def test_shape_pairing(self):
  U,_,_=orthonormal_family(np.eye(10)[:5],1e-10)
  d=np.arange(10,dtype=float);o=common_decomposition(d,U)
  self.assertLess(o['balance_error'],1e-14)
 def test_oriented_events(self):
  xs=np.linspace(0,1,202)
  f=lambda x:(x-.2)*(x-.4)*(x-.6)*(x-.8)
  r=oriented_crossings(f,xs,0.)
  self.assertEqual(len(r),4)
  self.assertEqual([v['orientation'] for v in r],['entry','exit','entry','exit'])
  self.assertEqual(len(passage_pairs(r)),2)
 def test_gauge_covariance(self):
  rng=np.random.default_rng(7);F=np.eye(10)+.02*rng.normal(size=(10,10))
  g0=rng.normal(size=(5,10));gt=np.linalg.solve(F.T,g0.T).T
  delta=rng.normal(size=10)
  self.assertLess(gauge_test(F,g0,gt,delta),1e-12)
if __name__=='__main__':unittest.main()
