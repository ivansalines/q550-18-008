"""Synthetic algebraic controls. They do not prove Q550 physical attribution."""
import importlib.util, pathlib, unittest
import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('q550_o',ROOT/'scripts/run_audit.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class SourceConnectionTests(unittest.TestCase):
    def test_metric_compatible_connection(self):
        rng=np.random.default_rng(50)
        B=np.c_[np.eye(4),rng.normal(size=(4,6))*.1]
        Bdot=rng.normal(size=(4,10))*.02
        J=rng.normal(size=(10,10))*.2
        K,diag=mod.projected_transport(B,Bdot,J,1e-8)
        W=mod.model_observer(B,0.1)
        h=1e-5
        Wdot=(mod.model_observer(B+h*Bdot,.1)-mod.model_observer(B-h*Bdot,.1))/(2*h)
        gamma,omega,err=mod.candidate_connection(K,W,Wdot)
        self.assertLess(err,1e-10)
        self.assertLess(np.linalg.norm(omega.T@W+W@omega),1e-10)
        self.assertEqual(diag['retained_rank'],4)
        self.assertLess(diag['right_inverse_defect'],1e-10)

    def test_projected_generator_does_not_require_response(self):
        B=np.c_[np.eye(4),np.zeros((4,6))]
        J=np.diag(np.linspace(-.5,.5,10))
        K,diag=mod.projected_transport(B,np.zeros_like(B),J,1e-8)
        self.assertLess(np.linalg.norm(K-J[:4,:4]),1e-12)
        self.assertLess(diag['projection_leakage_fraction'],1e-12)

    def test_hidden_complement_nonclosure_is_not_suppressed(self):
        B=np.c_[np.eye(4),np.zeros((4,6))]
        J=np.zeros((10,10));J[0,4]=3;J[1,5]=-2
        K,diag=mod.projected_transport(B,np.zeros_like(B),J,1e-8)
        self.assertLess(np.linalg.norm(K),1e-12)
        self.assertGreater(diag['projection_leakage_fraction'],.99)

    def test_passive_rechart_at_full_rank(self):
        rng=np.random.default_rng(65)
        B=np.c_[np.eye(4),rng.normal(size=(4,6))*.4]
        Bdot=rng.normal(size=(4,10))*.1
        J=rng.normal(size=(10,10))*.2
        S=np.array([[2.,.4,0.,0.],[0.,.8,.2,0.],[0.,0.,1.3,.3],[0.,0.,0.,.7]])
        K,_=mod.projected_transport(B,Bdot,J,1e-9)
        K2,_=mod.projected_transport(S@B,S@Bdot,J,1e-9)
        self.assertLess(np.linalg.norm(K2-S@K@np.linalg.inv(S)),1e-11)
        W=np.linalg.inv(B@B.T);W2=np.linalg.inv((S@B)@(S@B).T)
        self.assertLess(np.linalg.norm(W2-np.linalg.inv(S).T@W@np.linalg.inv(S)),1e-11)

    def test_probe_identifiability_is_insufficient(self):
        rng=np.random.default_rng(3)
        X=rng.normal(size=(4,2));np.linalg.svd(X)
        P=np.eye(4)-X@np.linalg.pinv(X)
        K=rng.normal(size=(4,4));D=rng.normal(size=(4,4))@P
        self.assertLess(np.linalg.norm((K+D)@X-K@X),1e-12)
        self.assertGreater(np.linalg.norm(D),1e-2)

if __name__=='__main__':unittest.main()
