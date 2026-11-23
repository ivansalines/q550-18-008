import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from principal_geometry import principal,source_active_subspaces,evaluate_shared_direction,projected_line_angle
class Geometry(unittest.TestCase):
    def test_internal_basis_change(self):
        u=np.eye(10)[:,:3];r=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
        m=principal(u,u@r)
        self.assertLess(m['frobenius_gap'],1e-14)
        self.assertLess(max(m['angles_deg']),1e-6)
    def test_dimension_forced_overlap(self):
        u=np.eye(10)[:,:6];v=np.eye(10)[:,4:]
        self.assertEqual(principal(u,v)['mandatory_intersection_dimension'],2)
    def test_orthogonal_gap(self):
        u=np.eye(10)[:,:2];v=np.eye(10)[:,2:4]
        self.assertAlmostEqual(principal(u,v)['spectral_gap'],1.,places=12)
    def test_false_2d_crossing(self):
        u=np.eye(10)[0]+np.eye(10)[2];u=u/np.linalg.norm(u)
        v=np.eye(10)[0]+np.eye(10)[3];v=v/np.linalg.norm(v)
        ang,a,b=projected_line_angle(u,v,(0,1))
        self.assertAlmostEqual(ang,0.,places=12)
        self.assertAlmostEqual(float(np.rad2deg(np.arccos(abs(u@v)))),60.,places=12)
    def test_source_nonzero_cancel(self):
        B=np.eye(10);C=-np.eye(10)
        sub=source_active_subspaces(B,C,1e-6,.01)
        self.assertEqual(sub['near_rank'],10)
        z=evaluate_shared_direction(B,C,B,C,np.eye(10)[0])
        self.assertGreater(z['source_a'],0)
        self.assertEqual(z['resultant_a'],0)
    def test_basis_projector_vs_line(self):
        u=np.eye(10)[:,:3];v=u@np.linalg.qr(np.array([[1.,1.,2.],[1.,2.,0.],[0.,2.,1.]]))[0]
        self.assertLess(principal(u,v)['frobenius_gap'],1e-13)
if __name__=='__main__':unittest.main()
