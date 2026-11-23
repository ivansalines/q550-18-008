import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tangent_math import cosine,range_scales,equal_x_opposed,fiber_fraction,five_state_and_tangent,ten_chart_and_tangent
class CheckTangent(unittest.TestCase):
 def test_cosine_metric(self):
  self.assertAlmostEqual(cosine([1,0],[-1,0]),-1)
  self.assertAlmostEqual(cosine([1,1],[-1,1]),0)
  self.assertAlmostEqual(cosine([1,1],[-1,1],[.1,10]),-0.9998000199980001)
 def test_metric_scale(self):
  s=range_scales([[0,1],[0,1],[0,1]])
  self.assertTrue(np.all(s>0))
 def test_opposed(self):
  self.assertEqual(equal_x_opposed(.1,-.2),'opposed')
  self.assertEqual(equal_x_opposed(.1,.2),'same')
  self.assertEqual(equal_x_opposed(0.,.2),'grazing')
 def test_fiber(self):
  self.assertAlmostEqual(fiber_fraction([0,2,3],[1,1,1]),1)
  self.assertAlmostEqual(fiber_fraction([2,0,0],[1,1,1]),0)
 def test_chain_rule(self):
  y=np.zeros(11);y[8]=.3;f=np.ones(11);J=np.eye(11)
  z,v=five_state_and_tangent(y,f,J);t,w=ten_chart_and_tangent(y,f)
  self.assertAlmostEqual(z[0],t[8]);self.assertAlmostEqual(v[0],w[8]);self.assertEqual(len(v),5);self.assertEqual(len(w),10)
if __name__=='__main__':unittest.main()
