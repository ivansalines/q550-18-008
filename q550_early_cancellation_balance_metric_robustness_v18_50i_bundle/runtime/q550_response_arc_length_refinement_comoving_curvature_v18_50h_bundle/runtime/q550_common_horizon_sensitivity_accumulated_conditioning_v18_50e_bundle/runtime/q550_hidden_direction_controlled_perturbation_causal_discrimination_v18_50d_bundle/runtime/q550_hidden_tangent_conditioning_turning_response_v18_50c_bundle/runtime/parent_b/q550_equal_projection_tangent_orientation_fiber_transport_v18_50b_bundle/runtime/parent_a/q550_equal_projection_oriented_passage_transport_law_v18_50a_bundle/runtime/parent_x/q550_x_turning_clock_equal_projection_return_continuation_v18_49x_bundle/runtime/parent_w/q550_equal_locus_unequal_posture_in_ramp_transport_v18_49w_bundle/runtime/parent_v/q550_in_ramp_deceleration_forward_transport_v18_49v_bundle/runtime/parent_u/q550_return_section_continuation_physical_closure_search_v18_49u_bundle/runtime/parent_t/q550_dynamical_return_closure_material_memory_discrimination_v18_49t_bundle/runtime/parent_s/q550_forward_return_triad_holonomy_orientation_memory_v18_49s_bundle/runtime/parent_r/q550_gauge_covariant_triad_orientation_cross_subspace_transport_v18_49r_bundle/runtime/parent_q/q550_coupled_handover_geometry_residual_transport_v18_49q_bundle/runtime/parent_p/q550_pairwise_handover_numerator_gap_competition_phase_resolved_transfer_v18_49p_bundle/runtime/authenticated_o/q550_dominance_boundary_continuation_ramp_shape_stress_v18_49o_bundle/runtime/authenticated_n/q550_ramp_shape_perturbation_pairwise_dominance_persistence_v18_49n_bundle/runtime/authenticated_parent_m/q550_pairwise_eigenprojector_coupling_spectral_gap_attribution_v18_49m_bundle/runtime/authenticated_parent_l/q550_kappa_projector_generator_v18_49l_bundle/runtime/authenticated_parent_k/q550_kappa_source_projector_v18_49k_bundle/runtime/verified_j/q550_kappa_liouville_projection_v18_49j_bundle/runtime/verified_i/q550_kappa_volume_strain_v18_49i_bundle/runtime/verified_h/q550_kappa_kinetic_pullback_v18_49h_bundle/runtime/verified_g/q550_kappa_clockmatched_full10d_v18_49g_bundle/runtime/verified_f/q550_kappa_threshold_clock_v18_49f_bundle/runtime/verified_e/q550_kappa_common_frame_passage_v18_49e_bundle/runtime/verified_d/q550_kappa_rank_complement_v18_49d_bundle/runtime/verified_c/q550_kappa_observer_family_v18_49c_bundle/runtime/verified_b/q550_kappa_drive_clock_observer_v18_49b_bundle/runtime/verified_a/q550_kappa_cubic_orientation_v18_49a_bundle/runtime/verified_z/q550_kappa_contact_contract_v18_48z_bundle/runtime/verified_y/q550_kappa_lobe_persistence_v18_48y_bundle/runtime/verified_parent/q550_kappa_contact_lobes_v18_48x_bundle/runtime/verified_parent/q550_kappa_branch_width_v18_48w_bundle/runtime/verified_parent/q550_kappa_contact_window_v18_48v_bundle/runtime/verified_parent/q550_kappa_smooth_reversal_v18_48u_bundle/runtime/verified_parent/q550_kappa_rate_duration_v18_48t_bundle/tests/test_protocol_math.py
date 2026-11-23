"""Pure mathematical regression tests independent of original Q550 trajectories."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from protocol_math import *
class ProtocolMathTests(unittest.TestCase):
    def test_seven_independent_designs(self):
        ds=designs();self.assertEqual(len(ds),7)
        self.assertEqual(len(set((x.rate,x.duration) for x in ds)),7)
    def test_phase_closed_exact(self):
        self.assertTrue(all(abs(x.rate*x.duration-1)<1e-15 for x in designs()[:3]))
    def test_rate_and_duration_separable(self):
        self.assertEqual(len(set(x.rate for x in designs() if x.duration==1)),3)
        self.assertEqual(len(set(x.duration for x in designs() if x.rate==1)),3)
    def test_nontrivial_common_phase(self):
        lo,hi=common_phase_domain(designs());self.assertGreater(hi-lo,.3)
        for d in designs():
            for q in (lo,hi):
                u=q/(d.rate*d.duration);s=1-q
                self.assertGreaterEqual(u,.25-1e-14);self.assertLessEqual(u,.96+1e-14)
                self.assertGreaterEqual(s,.04-1e-14);self.assertLessEqual(s,.75+1e-14)
    def test_velocity_scaling_endpoints(self):
        y=np.arange(11,dtype=float);self.assertTrue(np.array_equal(prepare_reversal(y,0),y))
        b=prepare_reversal(y,1)
        self.assertTrue(np.array_equal(b[[1,3,5,7,9]],-y[[1,3,5,7,9]]))
        self.assertTrue(np.array_equal(b[[0,2,4,6,8,10]],y[[0,2,4,6,8,10]]))
    def test_half_flip_zeros_only_material_velocities(self):
        y=np.arange(11,dtype=float);b=prepare_reversal(y,.5)
        self.assertTrue(np.array_equal(b[[1,3,5,7,9]],np.zeros(5)))
        self.assertEqual(b[10],y[10])
    def test_flip_symmetric_energy_preparation(self):
        self.assertAlmostEqual(initial_velocity_scale(.25)**2,initial_velocity_scale(.75)**2)
    def test_contiguous_support(self):
        q=np.linspace(.2,.6,9);a=[0,1,1,1,0,1,1,0,0]
        self.assertAlmostEqual(contiguous_phase_support(q,a),.10)
    def test_signed_power(self):
        self.assertEqual(signed_power_opposition(-2,3),1)
        self.assertEqual(signed_power_opposition(-2,-3),0)
        self.assertEqual(signed_power_opposition(0,-3),0)
    def test_threshold_persistence(self):
        q=np.linspace(0,1,11);d=np.array([.02]*3+[.001]*5+[.02]*3)
        met=sample_persistence(q,d,.005)
        self.assertEqual(met['count'],5);self.assertAlmostEqual(met['max_contiguous_phase_width'],.4)
    def test_alpha_invalid(self):
        for alpha in (-.1,1.1):
            with self.assertRaises(ValueError):initial_velocity_scale(alpha)
    def test_no_common_phase_rejected(self):
        from protocol_math import Design
        with self.assertRaises(ValueError):common_phase_domain([Design('a',.1,.1),Design('b',10,10)])
if __name__=='__main__':unittest.main()
