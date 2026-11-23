import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from gauge_math import (align_rotation,frames_from_velocities,chart_hessian,push_forward_tensor,
                        projection,covector_transform,corrected_norm,ratio,connection_identity)
class GaugeTests(unittest.TestCase):
 def test_minimal_rotation(self):
  u=np.arange(1,11,dtype=float);v=u[::-1].copy()
  R=align_rotation(u,v)
  np.testing.assert_allclose(R@(u/np.linalg.norm(u)),v/np.linalg.norm(v),atol=1e-12)
  np.testing.assert_allclose(R.T@R,np.eye(10),atol=1e-12)
 def test_moving_rotation(self):
  v=np.stack([np.arange(1,11,dtype=float)+.01*i*np.arange(10) for i in range(8)])
  frames=frames_from_velocities(v)
  for S,x in zip(frames,v):
   np.testing.assert_allclose(S@(x/np.linalg.norm(x)),np.eye(10)[0],atol=1e-10)
 def test_full_tensor_covariance(self):
  rng=np.random.default_rng(4);H=rng.standard_normal((11,11,11));H=(H+H.transpose(0,2,1))/2
  w=rng.uniform(.2,2,11);C=chart_hessian(H,w)
  G=np.eye(11);G[:10,:10]=np.diag(np.linspace(.5,2.0,10));G[0,5]=.4
  g=rng.normal(size=11);v=rng.normal(size=11)
  base=projection(C,g,v)
  Hg=push_forward_tensor(C,G)
  new=projection(Hg,np.linalg.solve(G.T,g),G@v)
  np.testing.assert_allclose(new,covector_transform(base,G[:10,:10]),atol=1e-10)
 def test_sheared_cometric(self):
  rng=np.random.default_rng(3);b=rng.normal(size=10);c=-.98*b+.07*rng.normal(size=10)
  S=np.diag(np.linspace(.4,2.,10));S[1,4]=1.2
  bp=covector_transform(b,S);cp=covector_transform(c,S)
  a=(corrected_norm(bp,S)+corrected_norm(cp,S))/corrected_norm(bp+cp,S)
  self.assertAlmostEqual(a,ratio(b,c),places=10)
 def test_connection(self):
  rng=np.random.default_rng(6);G=np.eye(11);G[:10,:10]=np.diag(np.linspace(.6,2.,10));
  D=rng.normal(size=(11,11));D[-1,:]=0;D[:,-1]=0
  J=rng.normal(size=(11,11));g=rng.normal(size=11)
  self.assertLess(connection_identity(G,D,J,g),1e-12)
if __name__=='__main__':unittest.main()
