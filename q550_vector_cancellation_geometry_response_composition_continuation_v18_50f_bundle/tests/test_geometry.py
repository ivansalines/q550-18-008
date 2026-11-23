"""Run with python -m unittest discover -s tests -v"""
import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geometry_math import ledger,angular_change
class TestGeometry(unittest.TestCase):
 def test_closure(self):
  l=np.array([1.,2.,0.,0.]);t=np.array([-0.5,0.,3.,0.]);x=ledger(l,t,l+t)
  self.assertAlmostEqual(x['observed_vs_split_abs'],0.)
 def test_opposite(self):
  x=ledger([1,0,0,0],[-.5,0,0,0]);self.assertAlmostEqual(x['alignment_cos'],-1.)
  self.assertAlmostEqual(x['cancellation_fraction'],2./3.)
 def test_orthogonal_rotation(self):
  l=np.array([1.,2.,.3,-.5]);t=np.array([-1.,.4,3.,2.]);q,_=np.linalg.qr(np.array([[1.,2.,3.,4.],[2.,1.,0.,3.],[1.,0.,1.,2.],[4.,1.,3.,2.]]))
  a=ledger(l,t);b=ledger(q@l,q@t)
  for name in ['local_norm','transported_norm','resultant_norm','alignment_cos','cancellation_fraction','gram_determinant']:
   self.assertAlmostEqual(a[name],b[name],places=11)
 def test_zero_transported(self):
  self.assertIsNone(ledger([1,0,0,0],[0,0,0,0])['alignment_cos'])
 def test_angle(self):
  self.assertAlmostEqual(angular_change([1,0],[0,1]),90.)
if __name__=='__main__':unittest.main()
