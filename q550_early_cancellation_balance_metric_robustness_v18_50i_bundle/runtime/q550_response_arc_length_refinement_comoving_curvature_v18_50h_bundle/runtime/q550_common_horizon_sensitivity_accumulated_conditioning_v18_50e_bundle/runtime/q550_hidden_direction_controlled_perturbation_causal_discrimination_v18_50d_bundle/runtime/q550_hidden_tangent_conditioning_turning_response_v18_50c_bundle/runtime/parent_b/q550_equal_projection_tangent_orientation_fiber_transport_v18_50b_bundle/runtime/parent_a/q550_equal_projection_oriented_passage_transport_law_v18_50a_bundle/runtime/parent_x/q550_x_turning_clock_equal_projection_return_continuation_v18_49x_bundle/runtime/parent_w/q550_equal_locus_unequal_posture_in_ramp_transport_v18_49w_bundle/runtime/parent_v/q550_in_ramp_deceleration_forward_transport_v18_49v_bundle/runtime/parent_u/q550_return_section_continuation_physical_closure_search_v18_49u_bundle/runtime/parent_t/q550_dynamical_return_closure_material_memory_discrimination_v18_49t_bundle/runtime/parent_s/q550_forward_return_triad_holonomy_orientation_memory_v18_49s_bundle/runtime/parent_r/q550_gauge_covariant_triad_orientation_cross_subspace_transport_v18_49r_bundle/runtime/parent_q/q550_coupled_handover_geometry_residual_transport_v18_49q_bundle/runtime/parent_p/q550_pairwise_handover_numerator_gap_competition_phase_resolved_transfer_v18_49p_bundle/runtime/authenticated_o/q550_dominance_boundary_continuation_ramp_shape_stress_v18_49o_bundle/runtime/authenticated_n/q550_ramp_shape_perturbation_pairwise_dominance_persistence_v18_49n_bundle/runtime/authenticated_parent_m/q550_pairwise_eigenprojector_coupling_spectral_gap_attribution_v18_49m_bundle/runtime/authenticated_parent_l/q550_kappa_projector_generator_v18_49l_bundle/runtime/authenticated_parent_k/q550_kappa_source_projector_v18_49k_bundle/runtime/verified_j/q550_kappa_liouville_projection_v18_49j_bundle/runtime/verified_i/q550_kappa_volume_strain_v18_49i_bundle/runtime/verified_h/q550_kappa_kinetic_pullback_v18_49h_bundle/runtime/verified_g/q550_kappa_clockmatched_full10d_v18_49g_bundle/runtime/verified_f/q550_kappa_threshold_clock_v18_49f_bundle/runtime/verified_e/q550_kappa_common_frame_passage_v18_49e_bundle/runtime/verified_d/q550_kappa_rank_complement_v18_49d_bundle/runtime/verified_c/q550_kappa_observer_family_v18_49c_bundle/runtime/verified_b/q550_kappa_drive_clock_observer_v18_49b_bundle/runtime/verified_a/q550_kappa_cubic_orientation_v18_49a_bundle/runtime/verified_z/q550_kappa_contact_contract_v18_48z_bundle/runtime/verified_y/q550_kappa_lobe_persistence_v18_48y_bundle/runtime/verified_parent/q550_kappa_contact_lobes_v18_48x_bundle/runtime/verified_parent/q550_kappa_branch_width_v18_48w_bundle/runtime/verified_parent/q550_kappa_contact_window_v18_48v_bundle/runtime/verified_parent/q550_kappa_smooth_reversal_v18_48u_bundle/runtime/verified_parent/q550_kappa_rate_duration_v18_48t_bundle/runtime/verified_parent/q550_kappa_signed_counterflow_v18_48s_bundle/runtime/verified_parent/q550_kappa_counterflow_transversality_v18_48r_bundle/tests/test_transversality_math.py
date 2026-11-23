import pathlib,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from transversality_math import *
class MathTests(unittest.TestCase):
    def test_tangent_orthogonal(self):
        a=tangent_angles([1,0,0],[0,1,0])
        self.assertAlmostEqual(a['line_angle_deg'],90)
        self.assertAlmostEqual(a['sin_3d'],1)
    def test_unoriented_sign(self):
        a=tangent_angles([1,0,0],[-1,0,0])
        self.assertAlmostEqual(a['line_angle_deg'],0)
        self.assertAlmostEqual(a['chronic_angle_deg'],180)
    def test_phase_closed_retraces_clock(self):
        for rate,dur in [(1.,1.),(.5,2.),(2.,.5)]:
            u=.65;self.assertAlmostEqual(phase_locked_forward_progress(u,rate,dur),1-u)
    def test_fixed_duration_clock(self):
        self.assertAlmostEqual(phase_locked_forward_progress(.5,2,1),0)
        self.assertAlmostEqual(phase_locked_forward_progress(.5,.5,1),.75)
    def test_projection_crossing_with_hidden_separation(self):
        r=np.array([[0,-1],[0,1]])
        f=np.array([[-1,0],[1,0]])
        c=segment_cross_candidates(r,f)
        self.assertEqual(len(c),1)
        self.assertAlmostEqual(c[0][2],.5)
    def test_parallel_not_crossing(self):
        r=np.array([[0,0],[1,0]]);f=np.array([[0,1],[1,1]])
        self.assertEqual(segment_cross_candidates(r,f),[])
    def test_shape_logit(self):
        y=np.zeros(11);y[8]=0;f=np.zeros(11);f[8]=4.
        self.assertAlmostEqual(shape(y)[2],.5)
        self.assertAlmostEqual(shape_tangent(y,f)[2],1.)
    def test_phase_bounds(self):
        lo,hi=phase_locked_bounds(2,1)
        self.assertAlmostEqual(hi,.48)
        self.assertAlmostEqual(lo,.25)
        lo,hi=phase_locked_bounds(.5,1)
        self.assertAlmostEqual(lo,.5)
        self.assertAlmostEqual(hi,.96)
    def test_synthetic_phase_min(self):
        def f(s):
            z=np.zeros(np.asarray(s).shape+(11,));z[...,0]=s
            return z
        def r(u):
            z=np.zeros(np.asarray(u).shape+(11,));z[...,0]=1-u
            return z
        best=phase_locked_min(f,r,1,1)
        self.assertAlmostEqual(best['distance'],0.)
    def test_shapes_vector(self):
        a=np.zeros((5,11));a[:,8]=np.arange(5)
        self.assertEqual(shape(a).shape,(5,3))
if __name__=='__main__':unittest.main()
