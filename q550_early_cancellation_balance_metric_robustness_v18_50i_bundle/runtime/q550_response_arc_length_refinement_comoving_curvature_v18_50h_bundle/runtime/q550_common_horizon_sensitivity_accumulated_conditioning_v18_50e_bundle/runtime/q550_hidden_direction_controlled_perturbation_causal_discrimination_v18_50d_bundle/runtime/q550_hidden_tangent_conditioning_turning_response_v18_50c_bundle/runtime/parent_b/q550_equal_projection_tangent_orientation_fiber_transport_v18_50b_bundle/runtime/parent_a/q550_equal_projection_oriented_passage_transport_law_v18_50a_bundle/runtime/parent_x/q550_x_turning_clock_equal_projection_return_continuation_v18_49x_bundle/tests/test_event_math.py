import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from event_math import scan_sign_roots,classify_turn,logistic,matched_locus,turns_to_degrees
class TestEvents(unittest.TestCase):
 def test_max(self):
  f=lambda t: 2*(.35-t)
  roots=scan_sign_roots(f,0,1,47)
  self.assertEqual(len(roots),1);self.assertAlmostEqual(roots[0],.35,11)
  self.assertEqual(classify_turn(f,roots[0],(0,1)),'maximum')
 def test_equal_projection(self):
  f=lambda t: (t-.3)*(t-.8)
  roots=scan_sign_roots(f,0,1,53)
  self.assertEqual(len(roots),2)
  self.assertAlmostEqual(roots[0],.3,11);self.assertAlmostEqual(roots[1],.8,11)
 def test_locus(self):
  a=np.zeros(10);b=np.zeros(10);b[4]=1
  self.assertAlmostEqual(matched_locus(a,b,np.ones(3)),1.)
 def test_angle(self):
  self.assertAlmostEqual(turns_to_degrees(np.eye(3)),0.)
 def test_logistic(self):
  self.assertAlmostEqual(logistic(0),.5)
  self.assertGreater(logistic(300),.99)
if __name__=='__main__':unittest.main()
