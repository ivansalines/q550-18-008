import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from passage_math import integrate_rates,integrate_passage,signed_polyline_area,projector_gap,transversality
import numpy as np
class TestPassage(unittest.TestCase):
 def test_area_symmetric_lobe(self):
  t=np.linspace(0,1,1001);x=.5+t*(1-t); theta=t
  assert abs(integrate_rates(t,x,np.ones_like(t),.5)-1/6)<1e-10
 def test_reversed_area(self):
  t=np.linspace(0,1,101);x=.5+t*(1-t);th=t
  a=signed_polyline_area(x,th,.5);b=signed_polyline_area(x[::-1],th[::-1],.5)
  assert abs(a+b)<1e-13
 def test_integral_constant_rate(self):
  t=np.linspace(0,1,101);x=.5+t*(1-t);th=t*2
  assert abs(integrate_passage(t,x,th,.5)-1/3)<1e-10
 def test_gauge_orthogonal_projector(self):
  P=np.diag([1.,1.,0.,0.]);Q=np.diag([1.,0.,1.,0.]);a=projector_gap(P,Q)
  s=np.array([[0,1.,0,0],[-1.,0,0,0],[0,0,0,1.],[0,0,-1.,0]])
  assert abs(a-projector_gap(s@P@s.T,s@Q@s.T))<1e-13
 def test_transversality(self):
  assert transversality(.2,-.3)=='opposed'
  assert transversality(.2,.3)=='same_direction'
if __name__=='__main__':unittest.main()
