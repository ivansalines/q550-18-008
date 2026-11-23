"""Independent algebraic controls of the material-family envelope."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from family_math import envelope,transform_chart,local_lift
class FamilyTests(unittest.TestCase):
 def setUp(self):
  self.rng=np.random.default_rng(1949)
  self.G=self.rng.normal(size=(5,10));self.d=self.rng.normal(size=10)
  self.A=self.rng.normal(size=(10,10));self.M=self.A.T@self.A+np.eye(10)
 def test_subset_monotonicity(self):
  a=envelope(self.G[:2],self.d,self.M)['amplitude']
  b=envelope(self.G,self.d,self.M)['amplitude']
  self.assertLessEqual(a,b+1e-12)
 def test_full_material_bound(self):
  o=envelope(self.G,self.d,self.M)
  self.assertLessEqual(o['amplitude'],o['material_distance']+1e-12)
  self.assertAlmostEqual(o['amplitude']**2+o['orthogonal_residual']**2,o['material_distance']**2,places=10)
 def test_family_basis_change(self):
  h=self.rng.normal(size=(5,5))+np.eye(5)
  a=envelope(self.G,self.d,self.M)['amplitude']
  b=envelope(h@self.G,self.d,self.M)['amplitude']
  self.assertAlmostEqual(a,b,places=10)
 def test_contravariant_coordinates_and_metric(self):
  S=np.diag(np.linspace(.6,1.6,10));S[1,0]=.3;S[4,8]=-.2
  Gp,dp,Mp=transform_chart(self.G,self.d,self.M,S)
  a=envelope(self.G,self.d,self.M)['amplitude']
  b=envelope(Gp,dp,Mp)['amplitude']
  self.assertAlmostEqual(a,b,places=10)
 def test_signed_family_symmetry(self):
  a=envelope(self.G,self.d,self.M)['amplitude']
  b=envelope(self.G,-self.d,self.M)['amplitude']
  self.assertAlmostEqual(a,b,places=12)
 def test_rank_deficient_family(self):
  G=np.vstack([self.G[0],2*self.G[0],-self.G[0]])
  o=envelope(G,self.d,np.eye(10))
  self.assertEqual(o['rank'],1)
  expected=abs(self.G[0]@self.d)/np.linalg.norm(self.G[0])
  self.assertAlmostEqual(o['amplitude'],expected,places=12)
 def test_direct_analytic_envelope(self):
  g=self.G[:2];C=g@np.linalg.solve(self.M,g.T);z=g@self.d
  analytic=float(np.sqrt(z@np.linalg.solve(C,z)))
  self.assertAlmostEqual(analytic,envelope(g,self.d,self.M)['amplitude'],places=11)
 def test_local_angle_lift(self):
  a=np.zeros(11);b=np.zeros(11);a[2]=np.pi-.02;b[2]=-np.pi+.03
  self.assertAlmostEqual(local_lift(a,b)[2],-.05,places=12)
 def test_metric_is_a_choice(self):
  a=envelope(self.G[:2],self.d,np.eye(10))['amplitude']
  b=envelope(self.G[:2],self.d,self.M)['amplitude']
  self.assertGreater(abs(a-b),.001)
if __name__=='__main__':unittest.main()
