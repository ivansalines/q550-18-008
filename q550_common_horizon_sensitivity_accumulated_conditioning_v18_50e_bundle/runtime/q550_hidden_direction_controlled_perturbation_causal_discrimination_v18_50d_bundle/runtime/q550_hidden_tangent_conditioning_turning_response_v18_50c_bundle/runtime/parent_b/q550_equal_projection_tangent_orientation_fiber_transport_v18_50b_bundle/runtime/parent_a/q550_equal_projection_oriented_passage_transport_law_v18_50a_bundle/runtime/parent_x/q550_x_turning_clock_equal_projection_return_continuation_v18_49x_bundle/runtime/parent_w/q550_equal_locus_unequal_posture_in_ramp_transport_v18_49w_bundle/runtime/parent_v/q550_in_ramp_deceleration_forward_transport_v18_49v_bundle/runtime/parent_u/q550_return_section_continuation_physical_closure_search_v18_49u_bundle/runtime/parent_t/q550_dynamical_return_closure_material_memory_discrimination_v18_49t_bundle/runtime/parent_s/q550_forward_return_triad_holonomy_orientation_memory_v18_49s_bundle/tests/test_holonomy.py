import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from scipy.linalg import expm
from holonomy_math import canonical_connector,integrate_K_cross,loop
class Tests(unittest.TestCase):
    def test_identity_connector(self):
        P=np.diag([1,1,1]+[0]*7)
        W,s,e=canonical_connector(P,P)
        self.assertLess(np.linalg.norm(W-np.eye(10)),1e-12)
        self.assertLess(e,1e-12)
    def test_direct_rotated_subspace(self):
        P=np.diag([1,1,1]+[0]*7)
        J=np.zeros((10,10));J[0,3]=.3;J[3,0]=-.3
        Q=expm(J)@P@expm(-J)
        W,s,e=canonical_connector(P,Q)
        self.assertLess(e,1e-11)
        self.assertGreater(s,.9)
        self.assertLess(np.linalg.norm(W.T@W-np.eye(10)),1e-11)
    def test_reversal_zero(self):
        P=np.diag([1,1,1]+[0]*7)
        A=np.eye(10)[:,:3]
        J=np.zeros((10,10));J[1,5]=.02;J[5,1]=-.02
        # Artificial common constant generator; identical tracks have zero loop holonomy.
        U=expm(.02*J)
        Q=U@P@U.T
        a=loop(P,Q,U,P,Q,U,A)
        self.assertLess(a['angle_deg'],1e-5)
    def test_numerical_reverse(self):
        J=np.zeros((10,10));J[1,4]=.6;J[4,1]=-.6
        f=integrate_K_cross(lambda q:J,.63,.65,21)
        b=integrate_K_cross(lambda q:J,.65,.63,21)
        self.assertLess(np.linalg.norm(b@f-np.eye(10)),1e-12)
if __name__=='__main__':unittest.main()
