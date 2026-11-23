#!/usr/bin/env python3
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from ramp_shapes import SHAPES,validate_shapes,h,area
from run_audit import onset,positive_width,PAIRS,P67
class TestRampShapes(unittest.TestCase):
    def test_all_shapes_are_admissible(self):self.assertTrue(validate_shapes())
    def test_equal_areas_and_endpoints(self):
        for sh in SHAPES:
            self.assertAlmostEqual(area(1,sh),.5,places=11)
            self.assertAlmostEqual(h(0,sh),0,places=11)
            self.assertAlmostEqual(h(1,sh),1,places=11)
    def test_antiderivative(self):
        x=np.linspace(.01,.99,30);eps=1e-6
        for sh in SHAPES:
            np.testing.assert_allclose((area(x+eps,sh)-area(x-eps,sh))/(2*eps),h(x,sh),atol=2e-8,rtol=2e-8)
    def test_clock_compatibility_original(self):
        for x in np.linspace(0,1,50):
            self.assertAlmostEqual(1-2*h(x,'cubic'),1-2*(3*x*x-2*x**3),places=12)
            self.assertAlmostEqual(-x+2*area(x,'cubic'),-x+2*(x**3-.5*x**4),places=12)
    def test_onset_bracket(self):
        x=np.linspace(.35,.65,31);v=x-.525
        estimate,lo,hi=onset(x,v)
        self.assertLessEqual(lo,.525);self.assertGreaterEqual(hi,.525)
        self.assertAlmostEqual(estimate,.525,places=12)
    def test_width(self):
        x=np.linspace(0,1,101)
        self.assertAlmostEqual(positive_width(x,x-.3),.7,places=11)
    def test_pair_index(self):self.assertEqual(PAIRS[P67],(5,6))
if __name__=='__main__':unittest.main()
