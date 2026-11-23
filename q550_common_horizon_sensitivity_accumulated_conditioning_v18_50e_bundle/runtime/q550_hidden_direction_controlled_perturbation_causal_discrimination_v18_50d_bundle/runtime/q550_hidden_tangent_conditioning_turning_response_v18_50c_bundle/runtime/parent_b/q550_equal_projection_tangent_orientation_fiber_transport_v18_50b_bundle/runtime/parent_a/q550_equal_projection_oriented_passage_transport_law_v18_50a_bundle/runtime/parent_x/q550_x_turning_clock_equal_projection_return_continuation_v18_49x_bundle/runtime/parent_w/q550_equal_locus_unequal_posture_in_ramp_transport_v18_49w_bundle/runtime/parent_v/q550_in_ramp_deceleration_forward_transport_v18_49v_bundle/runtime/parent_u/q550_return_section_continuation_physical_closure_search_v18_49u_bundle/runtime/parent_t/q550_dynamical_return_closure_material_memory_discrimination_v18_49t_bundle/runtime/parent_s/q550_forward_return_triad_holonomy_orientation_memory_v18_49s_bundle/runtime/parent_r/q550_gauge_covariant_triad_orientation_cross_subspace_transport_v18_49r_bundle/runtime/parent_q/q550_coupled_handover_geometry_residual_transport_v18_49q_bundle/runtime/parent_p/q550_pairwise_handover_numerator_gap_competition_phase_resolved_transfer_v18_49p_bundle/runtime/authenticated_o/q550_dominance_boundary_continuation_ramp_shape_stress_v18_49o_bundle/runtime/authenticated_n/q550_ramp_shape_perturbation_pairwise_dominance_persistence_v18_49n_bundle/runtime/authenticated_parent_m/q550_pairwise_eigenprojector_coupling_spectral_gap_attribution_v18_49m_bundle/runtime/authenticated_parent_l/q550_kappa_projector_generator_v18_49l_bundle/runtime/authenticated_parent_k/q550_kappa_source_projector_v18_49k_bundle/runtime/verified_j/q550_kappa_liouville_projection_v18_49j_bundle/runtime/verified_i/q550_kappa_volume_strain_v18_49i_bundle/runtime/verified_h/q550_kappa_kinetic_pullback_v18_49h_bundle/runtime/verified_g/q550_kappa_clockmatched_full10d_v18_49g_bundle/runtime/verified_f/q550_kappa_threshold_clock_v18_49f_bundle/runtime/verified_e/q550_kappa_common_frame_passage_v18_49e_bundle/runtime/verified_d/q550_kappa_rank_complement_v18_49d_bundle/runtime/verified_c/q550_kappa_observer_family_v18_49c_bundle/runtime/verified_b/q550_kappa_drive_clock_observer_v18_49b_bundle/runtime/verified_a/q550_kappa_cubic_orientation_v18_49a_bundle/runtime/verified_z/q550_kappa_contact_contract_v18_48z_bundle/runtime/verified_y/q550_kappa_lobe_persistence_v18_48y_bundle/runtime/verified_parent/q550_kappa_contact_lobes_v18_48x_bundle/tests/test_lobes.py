import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import lobe_math as m
import numpy as np
class LobeTests(unittest.TestCase):
    def test_two_lobes_and_merge(self):
        q=np.linspace(.1,.9,3201)
        f=lambda t: min(abs(t-.35),abs(t-.65))
        g=lambda t: abs(t-.5)
        a=m.analyze(q,np.array([f(x) for x in q]),.045,f)
        b=m.analyze(q,np.array([g(x) for x in q]),.09,g)
        self.assertEqual(a['component_count'],2)
        self.assertEqual(b['component_count'],1)
        self.assertEqual(m.merger_diagnostic(a,b),'INTERIOR_TWO_TO_ONE_NUMERICAL_MERGER')
    def test_one_lobe_truncated(self):
        q=np.linspace(.1,.9,1001)
        f=lambda x:abs(x-.104)
        d=m.analyze(q,np.abs(q-.104),.05,f)
        self.assertTrue(d['touches_left_boundary'])
        self.assertEqual(m.merger_diagnostic(d,d),'NO_TWO_TO_ONE_EVENT_IN_PAIR')
    def test_exact_threshold_refinement(self):
        q=np.linspace(.1,.9,200)
        f=lambda t:abs(t-.5)
        a=m.intervals(q,[f(x) for x in q],.1,f)
        self.assertAlmostEqual(a[0][0],.4,11)
        self.assertAlmostEqual(a[0][1],.6,11)
    def test_logistic_consistency(self):
        self.assertAlmostEqual(float(m.logit_to_x(np.array([0]))[0]),.5)
        self.assertLess(float(m.logit_to_x(np.array([-1000]))[0]),1e-100)
    def test_shaped_rows(self):
        v=np.zeros((3,11));v[:,0]=[1,2,3];v[:,4]=4
        out=m.shapes(v)
        self.assertEqual(out.shape,(3,3))
        np.testing.assert_allclose(out[:,2],.5)
if __name__=='__main__':unittest.main()
