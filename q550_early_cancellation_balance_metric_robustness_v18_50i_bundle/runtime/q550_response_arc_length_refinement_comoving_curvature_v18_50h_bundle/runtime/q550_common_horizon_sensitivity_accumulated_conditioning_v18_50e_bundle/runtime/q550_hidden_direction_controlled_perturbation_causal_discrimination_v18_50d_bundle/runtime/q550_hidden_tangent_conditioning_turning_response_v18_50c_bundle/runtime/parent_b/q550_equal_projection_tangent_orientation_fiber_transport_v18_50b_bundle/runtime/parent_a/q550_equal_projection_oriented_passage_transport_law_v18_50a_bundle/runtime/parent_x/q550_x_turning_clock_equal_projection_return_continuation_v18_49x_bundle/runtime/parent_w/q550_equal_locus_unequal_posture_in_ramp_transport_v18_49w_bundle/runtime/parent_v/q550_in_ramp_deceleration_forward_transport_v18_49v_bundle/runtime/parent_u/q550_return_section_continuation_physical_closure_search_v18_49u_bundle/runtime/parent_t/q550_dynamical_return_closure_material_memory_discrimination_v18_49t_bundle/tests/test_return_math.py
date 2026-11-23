import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from return_math import velocity_flip,phase_wrap,config_distance,reversal_velocity_mismatch,full_reversed_distance,principal_angles
class TestReturnMath(unittest.TestCase):
    def test_involution(self):
        y=np.linspace(-1,1,11);self.assertTrue(np.allclose(velocity_flip(velocity_flip(y)),y))
    def test_phase_modulo(self):self.assertAlmostEqual(float(phase_wrap(2*np.pi+.3)),.3)
    def test_reversed_state(self):
        y=np.linspace(-.4,1,11);x=velocity_flip(y)
        self.assertLess(config_distance(y,x),1e-14)
        self.assertLess(reversal_velocity_mismatch(y,x),1e-14)
        self.assertLess(full_reversed_distance(y,x),1e-14)
    def test_projector_covariance(self):
        P=np.zeros((10,10));P[:3,:3]=np.eye(3)
        z=np.random.default_rng(2).normal(size=(10,10));Q,_=np.linalg.qr(z)
        A,d=principal_angles(P,P)
        self.assertLess(d,1e-14)
        self.assertLess(max(A),1e-5)
        self.assertAlmostEqual(principal_angles(Q@P@Q.T,Q@P@Q.T)[1],0.,places=12)
if __name__=='__main__':unittest.main()
