import importlib.util, pathlib, sys, unittest
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('d_math',ROOT/'scripts/subspace_math.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_orthogonal_decomposition(self):
  a=m.subspace(np.eye(10)[:5],np.arange(1,11),np.eye(10),1e-8)
  self.assertLess(a['identity_error'],1e-13)
  self.assertAlmostEqual(a['amplitude']**2,55.)
 def test_rank_sweep(self):
  g=np.eye(10)[:5].copy();g[4]*=1e-8
  ranks=[m.subspace(g,np.ones(10),np.eye(10),x)['rank'] for x in [1e-4,1e-6,1e-10,1e-12]]
  self.assertEqual(ranks,[4,4,5,5])
 def test_principal_angle_geometry(self):
  U=np.eye(10)[:2]
  a=m.subspace(U,np.ones(10),np.eye(10),1e-10)
  b=m.subspace(U[::-1],np.ones(10),np.eye(10),1e-10)
  self.assertLess(m.compare(a,b)['projector_frobenius_gap'],1e-12)
 def test_full_extension(self):
  s=np.eye(10)[:5]
  full=m.independent_extension(s)
  self.assertEqual(np.linalg.matrix_rank(full),10)
  a=m.subspace(full,np.ones(10),np.eye(10),1e-10)
  self.assertLess(a['residual'],1e-11)
 def test_metric_covariance(self):
  rs=np.random.default_rng(5)
  g=rs.normal(size=(4,10));d=rs.normal(size=10)
  S=np.diag(np.geomspace(.5,2,10));M=np.diag(np.geomspace(1,2,10))
  amp=m.subspace(g,d,M,1e-10)['amplitude']
  amp2=m.subspace(g@np.linalg.inv(S),S@d,np.linalg.inv(S).T@M@np.linalg.inv(S),1e-10)['amplitude']
  self.assertAlmostEqual(amp,amp2,places=11)
 def test_rank_jump(self):
  a=m.subspace(np.eye(10)[:2],np.ones(10),np.eye(10),1e-10)
  b=m.subspace(np.eye(10)[:3],np.ones(10),np.eye(10),1e-10)
  self.assertEqual(m.compare(a,b)['rank_jump'],1)
if __name__=='__main__':unittest.main()
