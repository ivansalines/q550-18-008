"""Independent synthetic tests of projectors, strain rates, and gauge behavior."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from generator_math import spectral_generator,log_strain_sum_rule,constant_orthogonal_gauge,kinetic_frame_derivative
from kinetic_metric import embedding_and_jac
class TestGenerator(unittest.TestCase):
    @staticmethod
    def rotating_frame(t):
        A=np.eye(10);c=np.cos(t);s=np.sin(t);A[:2,:2]=[[c,-s],[s,c]]
        D=np.diag(np.linspace(2.,.48,10));B=D@A.T
        W=np.zeros((10,10));W[0,1]=-1.;W[1,0]=1.
        # A'=W A, B'=D*(A')^T= -D A^T W
        Bdot=-B@W
        return B,Bdot,W
    def test_exact_rotating_singular_directions(self):
        B,Bdot,W=self.rotating_frame(.42)
        o=spectral_generator(B,Bdot)
        self.assertLess(np.linalg.norm(o['generator']-W),1e-12)
        self.assertAlmostEqual(o['speed'][0],1.,places=10)
        self.assertAlmostEqual(o['speed'][1],1.,places=10)
        self.assertLess(abs(o['log_volume_rate']),1e-12)
        self.assertLess(abs(log_strain_sum_rule(o)),1e-12)
    def test_diagonal_stretch_no_rotation(self):
        B=np.diag(np.linspace(3.,.6,10));rates=np.linspace(.1,-.17,10)
        o=spectral_generator(B,np.diag(rates)@B)
        self.assertLess(np.linalg.norm(o['generator']),1e-12)
        self.assertLess(max(o['speed']),1e-12)
        self.assertAlmostEqual(o['log_volume_rate'],sum(rates),places=12)
    def test_fd_independent_rotating_projector(self):
        t=.43;delta=1e-5
        o=spectral_generator(*self.rotating_frame(t)[:2]);p=spectral_generator(*self.rotating_frame(t+delta)[:2])
        m=spectral_generator(*self.rotating_frame(t-delta)[:2]);fd=(p['projectors'][0]-m['projectors'][0])/(2*delta)
        self.assertLess(np.linalg.norm(o['projector_dot'][0]-fd),1e-9)
    def test_orthogonal_basis_gauge(self):
        B,Bdot,_=self.rotating_frame(.33)
        rng=np.random.default_rng(39);R,_=np.linalg.qr(rng.normal(size=(10,10)))
        o=spectral_generator(B,Bdot)
        p=spectral_generator(*constant_orthogonal_gauge(B,Bdot,R))
        self.assertLess(np.linalg.norm(p['generator']-R@o['generator']@R.T),1e-11)
        self.assertLess(np.linalg.norm(p['eigenvalues']-o['eigenvalues']),1e-11)
    def test_time_dependent_gauge_connection_required(self):
        B,Bdot,_=self.rotating_frame(.41)
        o=spectral_generator(B,Bdot)
        Z=np.zeros((10,10));Z[2,3]=-.4;Z[3,2]=.4
        theta=.21;R=np.eye(10);c=np.cos(theta);s=np.sin(theta);R[2:4,2:4]=[[c,-s],[s,c]]
        Rdot=Z@R
        # Moving coordinate basis: B'=B R^T, derivative includes B Rdot^T.
        Bm=B@R.T;Bmd=Bdot@R.T+B@Rdot.T
        om=spectral_generator(Bm,Bmd)
        # Partial time derivative has a gauge term; the connection-corrected
        # generator recovers geometric transport under the gauge map.
        self.assertLess(np.linalg.norm((om['generator']-Z)-R@o['generator']@R.T),1e-11)
        self.assertGreater(np.linalg.norm(om['generator']-R@o['generator']@R.T),.3)
    def test_near_degenerate_axes_rejected(self):
        B=np.diag([1.,1.+1e-9]+list(np.linspace(.9,.2,8)))
        with self.assertRaises(ValueError):spectral_generator(B,np.eye(10)*.01)
    def test_kinetic_embedding_directional_derivative(self):
        y=np.array([.3,.2,.5,-.3,-.2,.1,.6,.4,.7,.2]);dy=np.linspace(.1,-.3,10)
        val=kinetic_frame_derivative(y,dy,1.7,1.,embedding_and_jac)
        e=1e-6;_,jp=embedding_and_jac(y+e*dy,1.7);_,jm=embedding_and_jac(y-e*dy,1.7)
        self.assertLess(np.linalg.norm(val-(jp-jm)/(2*e)),2e-9)
    def test_strain_and_rotation_decouple(self):
        B,Bdot,W=self.rotating_frame(.5)
        o=spectral_generator(B,Bdot)
        self.assertGreater(o['generator_frobenius'],1.)
        self.assertLess(np.linalg.norm(o['sigma_rate']),1e-12)
if __name__=='__main__':unittest.main()
