import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from observer_geometry import (unit,matrices,ratio_from_maps,log_gradient,principal_direction,
                               rotate_observer,half_width,gauge_check)

class GeometryTests(unittest.TestCase):
    def test_linear_maps(self):
        rg=np.random.default_rng(10)
        hb=rg.normal(size=(11,11,11));hc=rg.normal(size=(11,11,11));f=rg.normal(size=11)
        scale=np.exp(rg.normal(size=10));g=unit(rg.normal(size=10))
        b,c=matrices(hb,hc,f,scale)
        direct=np.einsum('i,iab,a,bj->j',g/scale,hb[:10],f,np.diag(np.r_[scale,1.])[:,:10])
        self.assertTrue(np.allclose(b@g,direct,atol=2e-12))
    def test_projective_sign_and_norm(self):
        B=np.eye(10);C=-.95*np.eye(10);g=unit(np.arange(1,11.))
        a=ratio_from_maps(B,C,g)[0]
        self.assertAlmostEqual(a,39.,places=10)
        self.assertAlmostEqual(a,ratio_from_maps(B,C,-2*g)[0],places=10)
    def test_half_width_crossing(self):
        B=np.eye(10);C=np.zeros((10,10));C[0,0]=-.99
        g=np.eye(10)[0];d=np.eye(10)[1]
        target=ratio_from_maps(B,C,g)[0]/2
        wid=half_width(B,C,g,d,target,1)
        self.assertTrue(np.isfinite(wid) and wid>0.)
        th=math.radians(wid)
        self.assertLess(abs(ratio_from_maps(B,C,rotate_observer(g,d,th))[0]-target)/target,1e-8)
    def test_shear_covariance(self):
        rg=np.random.default_rng(44);B=rg.normal(size=(10,10));C=rg.normal(size=(10,10));g=unit(rg.normal(size=10))
        S=np.diag(np.linspace(.4,2.4,10));S[1,6]=.3
        self.assertAlmostEqual(gauge_check(B,C,g,S),ratio_from_maps(B,C,g)[0],places=12)
    def test_null_coupling(self):
        g=np.ones(10)/np.sqrt(10)
        self.assertEqual(ratio_from_maps(np.eye(10),np.zeros((10,10)),g)[0],1.)
        self.assertTrue(ratio_from_maps(np.eye(10),np.zeros((10,10)),g)[4])

if __name__=='__main__':unittest.main()
