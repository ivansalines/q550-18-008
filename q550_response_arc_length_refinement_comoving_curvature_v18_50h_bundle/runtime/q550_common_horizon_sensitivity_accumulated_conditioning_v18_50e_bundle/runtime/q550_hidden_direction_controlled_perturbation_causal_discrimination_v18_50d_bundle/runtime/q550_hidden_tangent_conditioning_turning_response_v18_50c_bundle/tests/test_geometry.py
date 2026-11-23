import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from geometry import direction_geometry,unit_tangent,secant_angle
class TestGeometry(unittest.TestCase):
 def test_constant(self):
  t=np.linspace(0,1,121);h=np.tile([1.,2.,-1.,3.],(len(t),1))
  _,_,k,_=direction_geometry(t,h,np.ones(4));self.assertLess(float(max(k)),1e-10)
 def test_circle(self):
  t=np.linspace(0,1,1001);h=np.column_stack((np.cos(2*t),np.sin(2*t),0*t,0*t))
  _,_,k,o=direction_geometry(t,h,np.ones(4))
  self.assertLess(float(np.max(abs(k[10:-10]-2))),1e-4)
  self.assertLess(float(np.max(abs(o[10:-10,0]-2))),1e-4)
 def test_rotation_invariance(self):
  t=np.linspace(0,1,101);h=np.column_stack((np.cos(t),np.sin(t),np.cos(t*2),np.sin(t*2)))
  rng=np.random.default_rng(35);q,_=np.linalg.qr(rng.normal(size=(4,4)))
  _,_,k,_=direction_geometry(t,h,np.ones(4));_,_,k2,_=direction_geometry(t,h@q,np.ones(4))
  self.assertLess(float(max(abs(k-k2))),1e-10)
 def test_common_scaling_invariance(self):
  t=np.linspace(0,1,101);h=np.column_stack((t+1,t**2+1,t**3+.1,t**4+2))
  _,_,k,_=direction_geometry(t,h,[1,2,3,4]);_,_,k2,_=direction_geometry(t,3*h,[3,6,9,12])
  self.assertLess(float(max(abs(k-k2))),1e-10)
 def test_reversal(self):
  t=np.linspace(0,1,151);h=np.column_stack((1+t,2-t,t*t,1+t**3))
  _,_,k,_=direction_geometry(t,h,np.ones(4))
  _,_,kr,_=direction_geometry(t,h[::-1],np.ones(4))
  self.assertLess(float(max(abs(k[::-1]-kr))),1e-9)
if __name__=='__main__':unittest.main()
