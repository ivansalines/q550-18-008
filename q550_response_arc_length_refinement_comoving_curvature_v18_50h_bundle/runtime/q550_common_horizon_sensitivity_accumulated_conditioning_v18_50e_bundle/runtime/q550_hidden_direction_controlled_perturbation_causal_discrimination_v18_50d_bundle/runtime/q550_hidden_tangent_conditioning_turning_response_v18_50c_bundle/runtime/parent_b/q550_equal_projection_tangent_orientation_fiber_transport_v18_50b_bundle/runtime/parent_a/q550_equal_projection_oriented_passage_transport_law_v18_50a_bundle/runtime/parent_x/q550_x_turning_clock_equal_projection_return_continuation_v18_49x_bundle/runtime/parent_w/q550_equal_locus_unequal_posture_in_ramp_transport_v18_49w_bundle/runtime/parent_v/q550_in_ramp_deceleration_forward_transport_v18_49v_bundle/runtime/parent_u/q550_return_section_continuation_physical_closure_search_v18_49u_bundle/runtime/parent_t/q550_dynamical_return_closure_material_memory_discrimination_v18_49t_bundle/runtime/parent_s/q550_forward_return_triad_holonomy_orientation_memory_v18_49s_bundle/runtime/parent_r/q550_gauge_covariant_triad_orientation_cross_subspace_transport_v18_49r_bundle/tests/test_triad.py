import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from triad_math import decompose,parts_from_eigenaxes,chi,gauge_flip,aligned_triad,transport_cross,IN
class Tests(unittest.TestCase):
 def test_blocks(self):
  rng=np.random.default_rng(3);A=rng.normal(size=(10,10));K=A-A.T
  P=np.einsum('ij,ik->ijk',np.eye(10),np.eye(10))
  d=decompose(K,P)
  self.assertLess(d['closure'],1e-12)
  self.assertLess(d['cross_derivative_closure'],1e-12)
  self.assertAlmostEqual(d['frac_internal']+d['frac_cross']+d['frac_external'],1)
 def test_sign_gauge(self):
  rng=np.random.default_rng(6);A,_=np.linalg.qr(rng.normal(size=(10,10)))
  w=rng.normal(size=(10,10));w=w-w.T
  base=parts_from_eigenaxes(A,w)
  for _ in range(10):
   a,om=gauge_flip(A,w,rng.choice([-1,1],size=10));new=parts_from_eigenaxes(a,om)
   self.assertLess(max(np.linalg.norm(base[k]-new[k]) for k in base),1e-12)
  c,den=chi(base[(5,6)],base[(6,7)],base[(5,7)])
  self.assertGreater(den,0);self.assertAlmostEqual(abs(c),1,places=12)
 def test_continuous_alignment(self):
  rng=np.random.default_rng(1);A,_=np.linalg.qr(rng.normal(size=(10,10)))
  ref=A[:,IN]; flipped=A*rng.choice([-1,1],size=(1,10))
  aligned,_,_=aligned_triad(flipped,ref)
  self.assertLess(np.linalg.norm(aligned-ref),1e-12)
 def test_cross_zero(self):
  self.assertLess(np.linalg.norm(transport_cross([np.zeros((10,10))]*10,.001)-np.eye(10)),1e-12)
if __name__=='__main__':unittest.main()
