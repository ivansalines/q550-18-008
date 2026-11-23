"""Boundary tests using exact synthetic curves, no Q550 labels."""
import sys, pathlib, unittest, numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'reference')]
from crossing_math import wrap,shape,spatial_distance,state_differences,matched_progress_min,free_pair_min
class GeometryTests(unittest.TestCase):
    def test_periodic_phase(self):
        self.assertAlmostEqual(float(wrap(2*np.pi+.123)),.123,places=12)
    def test_shape_logit(self):
        y=np.zeros(11);self.assertTrue(np.allclose(shape(y),[0,0,.5]))
    def test_shape_not_phase(self):
        x=np.zeros(11);y=x.copy();y[2]=1.;y[6]=1.;y[10]=.7
        d=state_differences(x,y,lambda y,k,p:float(y[2]),0,None)
        self.assertAlmostEqual(d['shape_distance'],0)
        self.assertGreater(d['full11D_chart_delta_L2'],1.)
        self.assertNotEqual(d['energy_delta'],0)
    def test_turnaround_exclusion_progress(self):
        def f(s):
            s=np.asarray(s);a=np.zeros(s.shape+(11,));a[...,0]=s
            return a
        def r(u):
            u=np.asarray(u);a=np.zeros(u.shape+(11,));a[...,0]=1+u
            return a
        a=matched_progress_min(f,r,lambda y,k,p:0,0,None,cutoff=.06)
        self.assertGreater(a['shape_distance'],.119)
    def test_true_free_curve_in_3D(self):
        def f(s):
            s=np.asarray(s);a=np.zeros(s.shape+(11,));a[...,0]=s-.4
            return a
        def r(u):
            u=np.asarray(u);a=np.zeros(u.shape+(11,));a[...,0]=u-.3
            return a
        q=free_pair_min(f,r,lambda y,k,p:0,0,None)
        self.assertLess(q['shape_distance'],1e-7)
    def test_nontrivial_pair_phase_mismatch(self):
        def f(s):
            s=np.asarray(s);a=np.zeros(s.shape+(11,));a[...,0]=s-.4;a[...,2]=s
            return a
        def r(u):
            u=np.asarray(u);a=np.zeros(u.shape+(11,));a[...,0]=u-.3;a[...,2]=u+1
            return a
        q=free_pair_min(f,r,lambda y,k,p:0,0,None)
        self.assertLess(q['shape_distance'],1e-7)
        self.assertGreater(abs(q['theta1_delta_rad']),.05)
if __name__=='__main__':unittest.main()
