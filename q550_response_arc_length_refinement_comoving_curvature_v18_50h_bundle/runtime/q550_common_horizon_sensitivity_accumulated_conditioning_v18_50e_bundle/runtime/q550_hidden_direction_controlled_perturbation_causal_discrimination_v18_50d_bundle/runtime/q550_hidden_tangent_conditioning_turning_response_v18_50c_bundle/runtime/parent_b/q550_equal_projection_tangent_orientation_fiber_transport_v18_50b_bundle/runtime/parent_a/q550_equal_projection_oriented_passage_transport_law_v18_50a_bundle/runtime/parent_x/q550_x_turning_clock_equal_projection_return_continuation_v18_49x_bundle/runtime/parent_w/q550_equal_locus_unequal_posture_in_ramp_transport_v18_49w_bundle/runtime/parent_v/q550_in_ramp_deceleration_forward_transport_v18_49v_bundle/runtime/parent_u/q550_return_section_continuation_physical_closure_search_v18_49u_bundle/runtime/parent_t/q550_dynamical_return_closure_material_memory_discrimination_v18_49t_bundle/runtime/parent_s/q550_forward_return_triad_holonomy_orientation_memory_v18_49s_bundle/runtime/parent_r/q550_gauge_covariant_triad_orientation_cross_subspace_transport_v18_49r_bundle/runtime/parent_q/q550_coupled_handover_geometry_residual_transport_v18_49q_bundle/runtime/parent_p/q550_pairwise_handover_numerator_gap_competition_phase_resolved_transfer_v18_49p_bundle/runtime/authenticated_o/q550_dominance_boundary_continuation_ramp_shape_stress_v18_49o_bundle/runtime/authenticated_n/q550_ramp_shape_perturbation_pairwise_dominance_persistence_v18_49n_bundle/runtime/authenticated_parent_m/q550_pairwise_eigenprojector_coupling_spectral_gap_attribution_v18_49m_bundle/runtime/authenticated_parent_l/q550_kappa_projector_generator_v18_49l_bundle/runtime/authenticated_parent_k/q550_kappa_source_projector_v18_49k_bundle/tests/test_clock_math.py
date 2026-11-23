"""Tests for true sign roots, volume-form dependence and sign-free projectors."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from clock_math import (smooth_root,projector_speed,projector_rates,half_turn_clock,exact_permutation_p)

class TestClockProjector(unittest.TestCase):
 def test_pchip_sign_bracketed_single_root(self):
  x=np.linspace(.35,.65,121);r,n=smooth_root(x,x-.4271)
  self.assertEqual(n,1);self.assertAlmostEqual(r,.4271,places=12)
 def test_no_extrapolated_root(self):
  x=np.linspace(.35,.65,121);r,n=smooth_root(x,x+.001)
  self.assertEqual(n,0);self.assertTrue(np.isnan(r))
 def test_volume_form_can_move_zero(self):
  x=np.linspace(.35,.65,121)
  r,_=smooth_root(x,x-.43);p,_=smooth_root(x,x-.43-.025)
  self.assertAlmostEqual(p-r,.025,places=12)
 def test_line_projector_speed_sign_invariance(self):
  q=np.linspace(0,1,101);a=np.tile(np.eye(10),(len(q),1,1)).copy()
  for i,t in enumerate(q):
   c,s=np.cos(t),np.sin(t);a[i,:2,:2]=[[c,-s],[s,c]]
  _,_,v=projector_speed(q,a)
  self.assertLess(abs(v[50,0]-1),2e-4)
  flipped=a.copy();flipped[::3,:,0]*=-1
  _,_,w=projector_speed(q,flipped)
  self.assertLess(np.max(abs(v-w)),1e-10)
 def test_projector_transport_under_global_orthogonal_gauge(self):
  q=np.linspace(0,1,101);a=np.tile(np.eye(10),(len(q),1,1)).copy()
  u=np.tile(np.arange(1,11,dtype=float),(len(q),1));u/=np.linalg.norm(u,axis=1)[:,None]
  for i,t in enumerate(q):
   c,s=np.cos(t),np.sin(t);a[i,:2,:2]=[[c,-s],[s,c]]
  first=projector_rates(q,u,a)
  rng=np.random.default_rng(21);R,_=np.linalg.qr(rng.normal(size=(10,10)))
  second=projector_rates(q,u@R.T,np.einsum('ij,njk->nik',R,a))
  for x,y in zip(first,second):self.assertTrue(np.allclose(x,y,atol=5e-11))
 def test_speed_half_turn_constant(self):
  q=np.linspace(.35,.65,121);t,T=half_turn_clock(q,np.ones(len(q))*2)
  self.assertAlmostEqual(t,.5,places=12);self.assertAlmostEqual(T,.6,places=12)
 def test_exact_permutation_sample(self):
  x=np.arange(6,dtype=float);r,p=exact_permutation_p(x,x)
  self.assertAlmostEqual(r,1.);self.assertTrue(0<p<=1/300)
 def test_source_split_kinetic_gradient(self):
  from source_math import log_density_gradient,log_kinetic_density
  y=np.array([.3,.2,.4,-.5,-.4,.1,-.3,.7,.2,-.1]);f=np.arange(1,11,dtype=float)*.1
  ep=1e-6
  analytic=log_density_gradient(y)@f
  numeric=(log_kinetic_density(y+ep*f,1.2)-log_kinetic_density(y-ep*f,1.2))/(2*ep)
  self.assertLess(abs(analytic-numeric),2e-9)
if __name__=='__main__':unittest.main()
