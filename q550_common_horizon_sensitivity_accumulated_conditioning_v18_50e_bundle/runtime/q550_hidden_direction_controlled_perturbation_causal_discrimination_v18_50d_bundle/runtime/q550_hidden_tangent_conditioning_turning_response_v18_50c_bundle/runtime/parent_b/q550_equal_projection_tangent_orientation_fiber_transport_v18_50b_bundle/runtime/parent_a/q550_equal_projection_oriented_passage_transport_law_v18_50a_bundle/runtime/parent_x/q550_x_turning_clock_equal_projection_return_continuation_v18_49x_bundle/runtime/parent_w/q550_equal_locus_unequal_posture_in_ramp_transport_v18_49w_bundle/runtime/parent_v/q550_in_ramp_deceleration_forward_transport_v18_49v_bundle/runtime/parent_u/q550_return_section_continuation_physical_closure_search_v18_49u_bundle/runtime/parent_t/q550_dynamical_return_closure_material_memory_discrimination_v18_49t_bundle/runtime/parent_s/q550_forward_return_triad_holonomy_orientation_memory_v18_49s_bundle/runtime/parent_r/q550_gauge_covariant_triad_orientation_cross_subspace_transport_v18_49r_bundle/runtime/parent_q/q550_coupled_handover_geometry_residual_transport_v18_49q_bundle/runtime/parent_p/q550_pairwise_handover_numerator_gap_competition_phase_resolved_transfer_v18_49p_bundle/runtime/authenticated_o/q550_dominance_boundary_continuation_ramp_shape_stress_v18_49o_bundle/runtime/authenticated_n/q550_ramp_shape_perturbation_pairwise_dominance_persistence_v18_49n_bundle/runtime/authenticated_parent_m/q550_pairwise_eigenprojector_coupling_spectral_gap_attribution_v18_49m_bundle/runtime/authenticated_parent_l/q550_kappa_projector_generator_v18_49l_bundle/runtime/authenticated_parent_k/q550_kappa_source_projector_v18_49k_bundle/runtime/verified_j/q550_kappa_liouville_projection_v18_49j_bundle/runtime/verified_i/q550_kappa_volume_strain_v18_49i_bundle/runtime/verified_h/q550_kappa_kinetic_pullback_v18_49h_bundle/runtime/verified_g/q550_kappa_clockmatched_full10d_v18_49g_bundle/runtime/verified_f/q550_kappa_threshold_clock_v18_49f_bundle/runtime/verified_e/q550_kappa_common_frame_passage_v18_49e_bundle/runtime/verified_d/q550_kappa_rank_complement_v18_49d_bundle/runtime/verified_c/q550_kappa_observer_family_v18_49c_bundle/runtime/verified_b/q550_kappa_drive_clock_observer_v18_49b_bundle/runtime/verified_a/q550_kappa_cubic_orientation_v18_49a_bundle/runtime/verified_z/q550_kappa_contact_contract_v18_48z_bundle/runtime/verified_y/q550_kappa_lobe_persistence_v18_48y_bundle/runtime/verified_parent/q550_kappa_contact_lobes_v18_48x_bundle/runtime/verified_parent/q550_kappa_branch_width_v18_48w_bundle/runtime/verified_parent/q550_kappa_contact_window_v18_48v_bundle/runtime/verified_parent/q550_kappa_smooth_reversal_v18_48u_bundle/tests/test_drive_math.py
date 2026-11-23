"""Independent mathematical controls for v18.48u."""
import sys,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from drive_math import *
class Tests(unittest.TestCase):
    def test_uniqueness(self):self.assertEqual(len(set(d.name for d in designs())),len(designs()))
    def test_initial_final_signs(self):
        for d in designs()[1:]:
            self.assertAlmostEqual(clock_sign(0,d),1.)
            self.assertAlmostEqual(clock_sign(d.duration,d),-1.)
    def test_zero_area_prelude(self):
        for d in designs()[1:]:
            x,_=quad(lambda t:clock_sign(t,d),0,d.prelude,points=[d.ramp/2,d.ramp/2+d.dwell] if d.kind=='stop' else None,epsabs=1e-13)
            self.assertLess(abs(x),1e-12,d.name)
            self.assertLess(abs(phase_excursion(d.prelude,d)),1e-12)
    def test_integral_agrees_with_primitive(self):
        for d in designs():
            for t in (.03,.12,d.prelude+.37):
                z,_=quad(lambda a:-clock_sign(a,d),0,t,epsabs=1e-11,limit=200)
                self.assertLess(abs(z-phase_excursion(t,d)),1e-9,(d.name,t))
    def test_phase_lock(self):
        for d in designs():
            for q in (.31,.57,.719):
                t=same_phase_time(q,d)
                self.assertAlmostEqual(phase_excursion(t,d),q)
                self.assertAlmostEqual(clock_sign(t,d),-1.)
    def test_zero_crossing(self):
        for d in designs()[1:]:
            self.assertAlmostEqual(clock_sign(d.prelude/2,d),0.,places=12) if d.kind!='stop' else self.assertEqual(clock_sign(d.ramp/2+d.dwell/2,d),0.)
    def test_velocity_prep(self):
        a=np.arange(11,dtype=float)
        self.assertTrue(np.array_equal(prepare_reversal(a,0),a))
        self.assertTrue(np.array_equal(prepare_reversal(a,1)[[1,3,5,7,9]],-a[[1,3,5,7,9]]))
        self.assertTrue(np.array_equal(prepare_reversal(a,.5)[[1,3,5,7,9]],np.zeros(5)))
    def test_persistence(self):
        a=width_under_threshold(np.linspace(.2,.4,5),[.02,.001,.001,.01,.02],.005)
        self.assertAlmostEqual(a['fraction'],.4)
        self.assertAlmostEqual(a['longest_q_span'],.05)
    def test_signed_power(self):
        self.assertEqual(signed_power_opposition(-2,1),1)
        self.assertEqual(signed_power_opposition(-2,-1),0)
        self.assertEqual(signed_power_opposition(0,1),0)
    def test_instant_reference(self):
        d=designs()[0];self.assertEqual(d.duration,1)
        self.assertEqual(clock_sign(.2,d),-1.)
        self.assertAlmostEqual(phase_excursion(.5,d),.5)
    def test_no_phase_ambiguity(self):
        for d in designs():
            with self.assertRaises(ValueError):same_phase_time(0.,d)
            with self.assertRaises(ValueError):same_phase_time(1.1,d)
if __name__=='__main__':unittest.main()
