"""Algebraic control and phase-width tests; no claim of physical proof."""
import unittest,sys,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ramp_math import designs,FULL_RAMPS,cubic_clock_sign,cubic_phase_excursion,phase_time,subthreshold_intervals
from scipy.integrate import quad
class TestRamps(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(FULL_RAMPS),17)
        self.assertEqual(len(designs(1)),17)
        self.assertEqual(len(designs(.75)),4)
    def test_zero(self):
        for d in designs(1.):
            self.assertAlmostEqual(cubic_phase_excursion(d.ramp,d),0.,places=13)
    def test_full_phase(self):
        for d in designs(1.):
            self.assertAlmostEqual(cubic_phase_excursion(phase_time(.5,d),d),.5,places=13)
    def test_rate_ends(self):
        for d in designs(1.):
            self.assertAlmostEqual(cubic_clock_sign(d.ramp+1e-7,d),-1.)
    def test_half_zero(self):
        for d in designs(1.):
            if d.ramp:
                self.assertAlmostEqual(cubic_clock_sign(d.ramp/2,d),0.,places=14)
    def test_clock_integral(self):
        for d in designs(1.):
            z=quad(lambda t:cubic_clock_sign(t,d),0,d.ramp+0.5,epsabs=1e-11,points=[d.ramp*.5,d.ramp] if d.ramp else None)[0]
            self.assertAlmostEqual(-z,cubic_phase_excursion(d.ramp+.5,d),places=10)
    def test_determinism(self):
        self.assertEqual(designs(1.),designs(1.))
    def test_intervals(self):
        xs=np.linspace(.3,.7,81)
        fun=lambda x:abs(x-.5)
        z=subthreshold_intervals(fun,xs,.05,minq=.5)
        self.assertAlmostEqual(z['total_phase_width'],.1,places=8)
        self.assertEqual(z['number_intervals'],1)
    def test_absent(self):
        z=subthreshold_intervals(lambda x:1.,np.linspace(.3,.7,41),.01,.5)
        self.assertEqual(z['number_intervals'],0)
    def test_multi_intervals(self):
        xs=np.linspace(.3,.7,61)
        fun=lambda x:min(abs(x-.38),abs(x-.62))
        z=subthreshold_intervals(fun,xs,.01,.38)
        self.assertEqual(z['number_intervals'],2)
        self.assertAlmostEqual(z['total_phase_width'],.04,places=8)
if __name__=='__main__':unittest.main()
