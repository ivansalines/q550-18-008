import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from ramp_math import poly_sign,finite_motion,coordinate_gap,x_from_z
class TestRampMath(unittest.TestCase):
 def test_zero(self):self.assertAlmostEqual(float(poly_sign([.5])[0]),0.)
 def test_ends(self):
  self.assertAlmostEqual(float(poly_sign([0])[0]),1.)
  self.assertAlmostEqual(float(poly_sign([1])[0]),-1.)
 def test_reversed(self):
  ss=poly_sign(np.linspace(0,1,101));self.assertTrue(np.all(np.diff(ss)<0))
 def test_path(self):self.assertTrue(np.allclose(finite_motion([[0.]*11,[3.]+[0.]*10]),[0,3]))
 def test_logistic(self):self.assertAlmostEqual(x_from_z(0),.5)
 def test_locus(self):self.assertAlmostEqual(coordinate_gap(np.zeros(11),np.zeros(11))[0],0.)
