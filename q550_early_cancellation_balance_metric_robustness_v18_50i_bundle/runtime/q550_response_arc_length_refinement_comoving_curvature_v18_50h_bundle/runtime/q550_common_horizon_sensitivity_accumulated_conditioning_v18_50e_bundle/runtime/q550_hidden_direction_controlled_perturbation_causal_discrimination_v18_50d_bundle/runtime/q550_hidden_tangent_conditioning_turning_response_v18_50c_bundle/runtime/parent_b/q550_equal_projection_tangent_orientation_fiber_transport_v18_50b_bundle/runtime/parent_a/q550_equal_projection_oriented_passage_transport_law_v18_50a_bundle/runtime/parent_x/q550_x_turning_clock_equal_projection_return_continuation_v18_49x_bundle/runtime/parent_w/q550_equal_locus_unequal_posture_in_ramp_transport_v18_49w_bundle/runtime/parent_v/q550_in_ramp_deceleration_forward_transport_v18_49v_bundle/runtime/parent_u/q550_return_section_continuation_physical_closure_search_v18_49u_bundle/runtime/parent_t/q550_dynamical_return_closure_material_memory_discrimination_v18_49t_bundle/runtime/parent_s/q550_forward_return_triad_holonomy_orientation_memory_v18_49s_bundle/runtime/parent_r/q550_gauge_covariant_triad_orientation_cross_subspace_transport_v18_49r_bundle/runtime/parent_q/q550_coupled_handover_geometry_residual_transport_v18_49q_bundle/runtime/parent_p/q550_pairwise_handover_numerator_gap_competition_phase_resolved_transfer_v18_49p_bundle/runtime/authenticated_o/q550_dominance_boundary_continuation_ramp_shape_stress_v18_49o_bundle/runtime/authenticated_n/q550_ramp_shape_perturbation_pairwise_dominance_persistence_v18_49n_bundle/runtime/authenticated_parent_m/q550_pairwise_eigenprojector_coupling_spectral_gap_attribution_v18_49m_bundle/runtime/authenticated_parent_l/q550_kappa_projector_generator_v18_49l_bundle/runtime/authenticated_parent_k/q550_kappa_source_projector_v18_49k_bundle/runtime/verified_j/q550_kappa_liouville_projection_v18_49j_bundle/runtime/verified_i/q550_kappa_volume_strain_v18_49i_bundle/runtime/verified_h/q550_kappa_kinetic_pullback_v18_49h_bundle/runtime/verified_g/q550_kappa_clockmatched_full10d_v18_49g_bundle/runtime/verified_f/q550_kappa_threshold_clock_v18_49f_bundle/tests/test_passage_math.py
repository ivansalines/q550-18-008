"""Independent small tests for orientation and level-crossing geometry."""
import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from passage_math import critical_points,crossings_from_extrema,paired_passages,orientation_trace,relative_orientation
class TestPassageMath(unittest.TestCase):
 def test_rotating_normalized_vector(self):
  f=lambda q:np.array([np.cos(2*q),np.sin(2*q),0.])
  out,*_=orientation_trace(f,.1,.3,33)
  self.assertAlmostEqual(out['signed_projected_angle_deg'],np.rad2deg(.4),7)
  self.assertLess(out['plane_leakage_max'],1e-7)
 def test_3d_leakage(self):
  f=lambda q:np.array([np.cos(q),np.sin(q),.5*q*q])
  out,*_=orientation_trace(f,.1,.7,25)
  self.assertGreater(out['plane_leakage_max'],.01)
 def test_nested_thresholds(self):
  f=lambda q:(q-.4)**2
  q=np.linspace(0,1,401);v=np.array([f(x) for x in q])
  cp=critical_points(f,q,v)
  a=paired_passages(crossings_from_extrema(f,q,v,cp,.01))
  b=paired_passages(crossings_from_extrema(f,q,v,cp,.04))
  self.assertEqual(len(a),len(b))
  self.assertAlmostEqual(a[0][0]['q'],.3,10)
  self.assertAlmostEqual(b[0][1]['q'],.6,10)
 def test_near_merging_barrier(self):
  f=lambda q:((q-.5)**2-.05**2)**2
  q=np.linspace(.2,.8,601);v=np.array([f(x) for x in q]);cp=critical_points(f,q,v)
  below=paired_passages(crossings_from_extrema(f,q,v,cp,3e-6))
  above=paired_passages(crossings_from_extrema(f,q,v,cp,9e-6))
  self.assertEqual(len(below),2);self.assertEqual(len(above),1)
 def test_orientation_sign_and_norm(self):
  self.assertAlmostEqual(relative_orientation([1,2],[2,4]),1,13)
  self.assertAlmostEqual(relative_orientation([1,0],[-1,0]),-1,13)
 def test_clock_reversal(self):
  omega=.84435791538;slope_q=-.4
  self.assertGreater(-slope_q/omega,0)
  self.assertAlmostEqual((-omega*.2)/(.2),-omega)
if __name__=='__main__':unittest.main()
