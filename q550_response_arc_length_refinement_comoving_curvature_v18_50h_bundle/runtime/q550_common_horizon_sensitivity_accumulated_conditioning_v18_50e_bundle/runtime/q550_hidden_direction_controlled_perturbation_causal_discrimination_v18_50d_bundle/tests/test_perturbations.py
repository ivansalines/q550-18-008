import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from perturbation_math import pulse,unit,centered,direction_angle
class MathematicalTests(unittest.TestCase):
 def test_pulse_endpoints(self):
  for t in [.1,.4]:self.assertEqual(pulse(t,.1,.4,.02),(0.,0.))
 def test_pulse_zero_rate_midpoint(self):
  self.assertAlmostEqual(pulse(.25,.1,.4,.02)[1],0.,places=12)
 def test_pulse_signs(self):
  self.assertGreater(pulse(.175,.1,.4,.02)[1],0)
  self.assertLess(pulse(.325,.1,.4,.02)[1],0)
 def test_orientation_normalized(self):
  u=unit([2,0,0,0],[2,1,1,1]);self.assertAlmostEqual(float(np.linalg.norm(u)),1)
 def test_direction_angle(self):
  self.assertAlmostEqual(direction_angle(np.array([1.,0]),np.array([0.,1.])),90.)
 def test_symmetric_response(self):
  self.assertTrue(np.allclose(centered([0,0],[.1,.4],[-.1,-.4],.1),[1,4]))
if __name__=='__main__':unittest.main()
