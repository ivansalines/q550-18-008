import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_audit import curve_metric
class TestRefinement(unittest.TestCase):
    def test_straight_line(self):
        p=np.array([[0.,0.],[1.,0.],[2.,0.]])
        a,d,t=curve_metric(p)
        self.assertAlmostEqual(a,2);self.assertAlmostEqual(d,2);self.assertAlmostEqual(t,0)
    def test_monotone_under_refinement(self):
        x=np.linspace(0,1,33)
        p=np.column_stack((x,x*x))
        prev=0
        for n in (5,9,17,33):
            a,_,_=curve_metric(p[::32//(n-1)])
            self.assertGreaterEqual(a+1e-12,prev);prev=a
    def test_curve_exceeds_chord(self):
        p=np.array([[0,0],[1,1],[2,0]],float)
        a,d,_=curve_metric(p);self.assertGreater(a,d)
    def test_zero_before_kick(self):
        p=np.zeros((3,4));a,d,t=curve_metric(p)
        self.assertEqual((a,d,t),(0.,0.,0.))
if __name__=='__main__':unittest.main()
