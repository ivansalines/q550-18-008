import unittest,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from phase_transport import (unit,minimal_turn,comoving_frames,projector_gap,
                             lag_pairs,best_lag,pulse_centers,impulse_masks,cycling_control)
class CoMovingTests(unittest.TestCase):
 def test_minimal_turn_maps_line(self):
  x=unit([1,2,-1,0]);y=unit([-1,3,.4,1]);R=minimal_turn(x,y)
  self.assertLess(np.linalg.norm(R@x-y),1e-12)
  self.assertLess(np.linalg.norm(R.T@R-np.eye(4)),1e-12)
  self.assertAlmostEqual(np.linalg.det(R),1.,places=12)
 def test_fixed_history_zero_pace(self):
  gg=np.repeat(np.array([[1.,0.,0.]]),5,axis=0)
  Q,quality=comoving_frames(gg)
  self.assertLess(quality['max_line_tracking_error'],1e-12)
  np.testing.assert_allclose(Q,np.broadcast_to(np.eye(3),(5,3,3)))
 def test_projective_flip_invariant(self):
  x=[1.,0.,0.];t=[0.96,0.28,0.]
  R,q=comoving_frames([x,-np.array(t),t]);self.assertLess(q['max_line_tracking_error'],1e-12)
 def test_rotating_bundle_coframe_removes_rigid_rotation(self):
  base=unit([1.,0.,0.]);P0=np.diag([1.,0.,0.]);gg=[];PP=[]
  for a in np.linspace(0,.5,13):
   R=np.array([[math.cos(a),-math.sin(a),0.],[math.sin(a),math.cos(a),0.],[0.,0.,1.]])
   gg.append(R@base);PP.append(R@P0@R.T)
  frames,q=comoving_frames(gg);pulled=np.array([R.T@P@R for P,R in zip(PP,frames)])
  self.assertGreater(projector_gap(PP[0],PP[-1]),0.1)
  self.assertLess(max(projector_gap(p,pulled[0]) for p in pulled),1e-11)
 def test_signed_lag_direction(self):
  rng=np.random.default_rng(281);x=rng.normal(size=40);y=np.r_[np.zeros(2),x[:-2]]
  self.assertEqual(best_lag(lag_pairs(x,y))['lag_steps'],2)
 def test_mask_preserves_timeline(self):
  x=np.arange(40,dtype=float);y=np.r_[np.zeros(2),x[:-2]];mask=np.ones(40,bool);mask[10:13]=False
  z=lag_pairs(x,y,6,mask=mask)
  self.assertEqual(next(r for r in z if r['lag_steps']==2)['pairs'],33)
 def test_pulse_separation(self):
  x=np.zeros(40);x[7]=40;x[8]=25;x[23]=30
  self.assertEqual(pulse_centers(x,2,3),[7,23])
 def test_masks_event_neighborhood(self):
  x=np.arange(40);y=x[::-1];cases=impulse_masks(x,y,2,1)
  for name,mask,j in cases:
   if name.startswith('leave_'):self.assertFalse(mask[j]);self.assertGreaterEqual(mask.sum(),37)
 def test_cyclic_null_noncausal(self):
  rng=np.random.default_rng(9);x=rng.normal(size=40);y=np.roll(x,2)
  p,n=cycling_control(x,y,np.ones(40,bool))
  self.assertTrue(np.isfinite(p));self.assertEqual(n,39)
 def test_fixed_orthogonal_gauge_covariance(self):
  rng=np.random.default_rng(9)
  g=unit(rng.normal(size=5));h=unit(rng.normal(size=5));u=unit(rng.normal(size=5))
  P=np.outer(u,u);R=minimal_turn(g,h);A=np.linalg.qr(rng.normal(size=(5,5)))[0]
  gaugeR=minimal_turn(A@g,A@h)
  self.assertLess(np.linalg.norm(gaugeR-A@R@A.T),1e-12)
  self.assertLess(np.linalg.norm(gaugeR.T@(A@P@A.T)@gaugeR - A@(R.T@P@R)@A.T),1e-12)
if __name__=='__main__':unittest.main()
