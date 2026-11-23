import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ramp_stress import h,area,properties,ShapeClock
from scipy.integrate import quad
SHAPES=('beta:2:2','beta:3:3','beta:12:12','beta:64:64',
        'beta:2:24','beta:2:100','skew:-3','skew:3',
        'recoil:-4:1','recoil:4:1','recoil:-2:2','recoil:4:2','recoil:2:4')
class StressTests(unittest.TestCase):
    def test_all_shapes_bounded_equal_area(self):
        for s in SHAPES:
            with self.subTest(s=s):self.assertTrue(properties(s)['admissible'])
    def test_cubic_reference(self):
        x=np.linspace(0,1,1001)
        self.assertLess(float(np.max(np.abs(h(x,'beta:2:2')-(3*x*x-2*x*x*x)))),1e-14)
    def test_area_integral_numerical(self):
        for sh in SHAPES:
            with self.subTest(sh=sh):
                for t in (.125,.35,.65,.85):
                    self.assertAlmostEqual(area(t,sh),quad(lambda x:float(h(x,sh)),0,t,epsabs=3e-12)[0],delta=2e-10)
    def test_centered_phase(self):
        for sh in SHAPES:
            self.assertAlmostEqual(area(1.,sh),.5,delta=1e-10)
    def test_shape_categories(self):
        self.assertTrue(properties('beta:64:64')['monotone'])
        self.assertFalse(properties('recoil:4:1')['monotone'])
    def test_clock_equivalence_after_end(self):
        class D:
            def __init__(self,r,k):self.ramp=r;self.kind=k
        class FakeOriginal:
            Design=D
        c=ShapeClock(FakeOriginal())
        for sh in SHAPES:
            d=D(.3,sh)
            self.assertAlmostEqual(c.cubic_phase_excursion(.7,d),.4,delta=1e-15)
            self.assertAlmostEqual(c.cubic_clock_sign(.7,d),-1.,delta=1e-15)
if __name__=='__main__':unittest.main()
