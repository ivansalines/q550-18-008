import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from chart_math import local_chart,inverse_chart,reparam_jet,recover_physical_cubic,root_derived_skew
class TestChart(unittest.TestCase):
    def test_inverse_for_both_orientations(self):
        x=np.linspace(-.03,.03,60)
        for e in (-1,1):
            for b in (-1.,-.5,0.,.5,1.):
                np.testing.assert_allclose(inverse_chart(local_chart(x,e,b),e,b),x,rtol=0,atol=2e-16)
    def test_affine_orientation(self):
        self.assertEqual(reparam_jet(-5.,6.,-1,0.),(-5.,-6.))
    def test_monotone_nonlinear_can_remove_cubic(self):
        C=-5.;D=6.;b=D/(3*C)
        c2,d3=reparam_jet(C,D,1,b)
        self.assertEqual(c2,C);self.assertAlmostEqual(d3,0.,places=12)
    def test_magnitude_coordinate_reconstruction(self):
        for e in (-1,1):
            for b in (-1.0,0.0,.4):
                c2,d3=reparam_jet(-5.47,5.8,e,b)
                self.assertAlmostEqual(recover_physical_cubic(c2,d3,e,b),5.8,places=12)
    def test_midpoint_skew_sign(self):
        self.assertGreater(root_derived_skew(-.01+.001,.01+.001,0.,1e-4,-5.),0.)
    def test_fold_reject(self):
        with self.assertRaises(ValueError):local_chart(np.array([.03]),1,-100.)
if __name__=='__main__':unittest.main()
