import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from continuation_math import refinements,branch_key,sign_of,sign_transitions,phase_minimum,differences
class ContinuationTests(unittest.TestCase):
    def test_ramps(self):
        for f,b in [('phaseblind_x',0),('phaseblind_x',1),('phasecov_x',0),('phasecov_x',1)]:
            s=refinements(f,b)
            self.assertEqual(len(s),8);self.assertEqual(len(set(s)),8)
            self.assertTrue(all(x>0 for x in s))
    def test_seeds(self):
        self.assertEqual(refinements('phasecov_x',0)[0],.02)
        self.assertEqual(refinements('phaseblind_x',0)[-1],.30)
    def test_names(self):
        with self.assertRaises(ValueError):branch_key('synthetic')
    def test_sign(self):
        self.assertEqual([sign_of(x) for x in [-1,0,1]],[-1,0,1])
    def test_sign_floor(self):
        self.assertEqual(sign_of(1e-13),0)
    def test_sign_transition(self):
        v=[{'r':0.,'w':-1.},{'r':.1,'w':2.},{'r':.2,'w':3.}]
        self.assertEqual(len(sign_transitions(v,'r','w')),1)
    def test_gap(self):
        self.assertEqual(differences([1,2],[3,4])['median_3D'],1.5)
    def test_gap_reject(self):
        with self.assertRaises(ValueError):differences([-1],[1])
    def test_scalar_min(self):
        q=np.linspace(.2,.8,21);g=(q-.53)**2
        d,x=phase_minimum(lambda z:(z-.53)**2,q,g)
        self.assertLess(d,1e-18);self.assertAlmostEqual(x,.53,places=8)
if __name__=='__main__':unittest.main()
