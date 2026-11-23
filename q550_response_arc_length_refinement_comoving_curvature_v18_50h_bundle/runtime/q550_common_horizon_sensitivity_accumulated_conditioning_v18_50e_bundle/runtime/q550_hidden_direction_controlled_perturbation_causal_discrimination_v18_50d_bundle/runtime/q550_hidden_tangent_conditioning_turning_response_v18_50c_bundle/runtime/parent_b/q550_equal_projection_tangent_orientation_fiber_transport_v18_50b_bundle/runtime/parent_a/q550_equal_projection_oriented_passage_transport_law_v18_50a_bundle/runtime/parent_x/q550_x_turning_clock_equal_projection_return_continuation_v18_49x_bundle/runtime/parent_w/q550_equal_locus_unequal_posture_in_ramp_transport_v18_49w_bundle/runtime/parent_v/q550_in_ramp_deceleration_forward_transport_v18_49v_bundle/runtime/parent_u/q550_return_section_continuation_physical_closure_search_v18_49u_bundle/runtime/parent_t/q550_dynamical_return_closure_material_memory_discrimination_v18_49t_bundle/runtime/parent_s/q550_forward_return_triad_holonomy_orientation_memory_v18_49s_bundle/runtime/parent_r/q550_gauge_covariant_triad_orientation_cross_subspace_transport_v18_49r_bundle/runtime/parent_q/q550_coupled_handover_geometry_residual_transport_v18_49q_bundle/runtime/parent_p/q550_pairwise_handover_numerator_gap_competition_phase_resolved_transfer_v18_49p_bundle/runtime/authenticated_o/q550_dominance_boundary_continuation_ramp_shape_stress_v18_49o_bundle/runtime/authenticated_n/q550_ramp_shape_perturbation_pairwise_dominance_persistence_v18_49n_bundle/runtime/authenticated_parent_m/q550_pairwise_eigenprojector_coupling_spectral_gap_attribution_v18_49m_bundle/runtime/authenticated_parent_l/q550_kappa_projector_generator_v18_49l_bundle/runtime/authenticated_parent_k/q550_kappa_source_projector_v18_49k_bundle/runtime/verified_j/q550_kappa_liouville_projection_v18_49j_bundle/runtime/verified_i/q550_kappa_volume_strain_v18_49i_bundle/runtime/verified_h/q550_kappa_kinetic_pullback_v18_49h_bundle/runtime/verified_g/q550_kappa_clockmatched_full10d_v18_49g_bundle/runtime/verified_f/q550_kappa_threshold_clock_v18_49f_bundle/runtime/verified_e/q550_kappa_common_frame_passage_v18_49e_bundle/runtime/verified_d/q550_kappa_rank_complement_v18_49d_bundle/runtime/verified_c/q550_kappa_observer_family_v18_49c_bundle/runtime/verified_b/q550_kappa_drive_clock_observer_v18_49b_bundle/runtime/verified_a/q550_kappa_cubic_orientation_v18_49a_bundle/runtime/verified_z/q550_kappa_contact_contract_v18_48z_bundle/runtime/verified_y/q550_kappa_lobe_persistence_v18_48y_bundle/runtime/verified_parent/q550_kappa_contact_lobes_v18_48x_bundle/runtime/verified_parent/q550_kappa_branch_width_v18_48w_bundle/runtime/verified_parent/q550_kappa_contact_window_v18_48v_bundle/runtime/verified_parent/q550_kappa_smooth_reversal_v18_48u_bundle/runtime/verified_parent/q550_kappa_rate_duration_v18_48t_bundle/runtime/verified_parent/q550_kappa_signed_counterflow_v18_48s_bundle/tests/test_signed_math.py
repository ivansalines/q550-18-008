"""Independent synthetic tests for signed and phase-corresponding geometry."""
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from signed_math import (alignment,projected_chirality,phase_corresponding_tangents,
 signed_contact_derivative,signed_energy_gap_derivative,phase_locked_component_roots)
class SignedMath(unittest.TestCase):
    def test_opposite_chronological(self):
        a=alignment([1,0,0],[-2,0,0]);self.assertAlmostEqual(a['chronological_angle_deg'],180)
        self.assertAlmostEqual(a['phase_corresponding_angle_deg'],0)
    def test_same_chronological(self):
        a=alignment([1,0,0],[2,0,0]);self.assertAlmostEqual(a['chronological_angle_deg'],0)
        self.assertAlmostEqual(a['phase_corresponding_angle_deg'],180)
    def test_sign_change_axis_order(self):
        a=[1,0,0];b=[0,2,0]
        self.assertEqual(projected_chirality(a,b,(0,1)),2)
        self.assertEqual(projected_chirality(a,b,(1,0)),-2)
    def test_phase_synced_scale(self):
        r,f=phase_corresponding_tangents([1,2,3],[2,3,4],.5,2)
        self.assertTrue(np.allclose(f,[-2,-3,-4]))
    def test_phase_locked_derivative(self):
        # R(u)=2u; F(s)=3s, s=1-2u; signed d(half gap squared)/du.
        u=.3;s=1-2*u;gap=np.array([2*u-3*s,0,0]);tr=np.array([2,0,0]);tf=np.array([3,0,0]);
        self.assertAlmostEqual(signed_contact_derivative(gap,tr,tf,2,1),float(gap[0]*8))
    def test_phase_energy_gap_derivative(self):
        self.assertAlmostEqual(signed_energy_gap_derivative(4,-2,.5,2),6)
    def test_one_coordinate_root(self):
        f=lambda s:np.stack((np.asarray(s)*0+0.5,np.asarray(s)*0,np.asarray(s)*0),axis=-1)
        r=lambda u:np.stack((np.asarray(u),np.asarray(u)*0,np.asarray(u)*0),axis=-1)
        roots=phase_locked_component_roots(f,r,1,1,.1,.9,0,nodes=33)
        self.assertEqual(len(roots),1);self.assertAlmostEqual(roots[0],.5)
    def test_no_onecoord_root(self):
        f=lambda s:np.stack((np.asarray(s)*0+3,np.asarray(s)*0,np.asarray(s)*0),axis=-1)
        r=lambda u:np.stack((np.asarray(u),np.asarray(u)*0,np.asarray(u)*0),axis=-1)
        self.assertEqual(phase_locked_component_roots(f,r,1,1,.1,.9,0),[])
    def test_near_parallel_not_zero(self):
        a=alignment([1,0,0],[1,.001,0]);self.assertGreater(a['cross_magnitude'],0)
        self.assertLess(a['chronological_angle_deg'],.1)
    def test_invalid_rate(self):
        with self.assertRaises(ValueError):phase_corresponding_tangents([1,0,0],[0,1,0],0,1)
if __name__=='__main__':unittest.main()
