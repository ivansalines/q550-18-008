import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geometry_math import arc_diagnostics,metric_matrix,safe_angle,cancellation
class GeometryTests(unittest.TestCase):
 def test_straight_path(self):
    p=[(i/4,np.array([i,0,0,0]),np.zeros(4),np.array([i,0,0,0])) for i in range(5)]
    P,S,a=arc_diagnostics(p,np.eye(4));self.assertAlmostEqual(a['arc5'],4);self.assertAlmostEqual(a['arc3'],4);self.assertAlmostEqual(a['straightness'],1)
 def test_loop_lower_bound(self):
    p=[(i/4,np.array([x,y,0.,0.]),np.zeros(4),np.array([x,y,0.,0.])) for i,(x,y) in enumerate([(0,0),(1,0),(1,1),(0,1),(0,0)])]
    P,S,a=arc_diagnostics(p,np.eye(4));self.assertAlmostEqual(a['arc5'],4);self.assertTrue(a['arc3']<=a['arc5']);self.assertAlmostEqual(a['arc2'],0)
 def test_decomposition_tangent(self):
    p=[(i/4,np.array([i,0.,0.,0.]),np.array([0.,i,0.,0.]),np.array([i,i,0.,0.])) for i in range(5)]
    P,S,a=arc_diagnostics(p,np.eye(4))
    for seg in S:self.assertAlmostEqual(seg['local_signed_advance']+seg['transported_signed_advance'],seg['length'])
 def test_change_time_param_only(self):
    p=[(i/4,np.array([i,(-1)**i,0.,0.]),np.zeros(4),np.array([i,(-1)**i,0.,0.])) for i in range(5)]
    a=arc_diagnostics(p,np.eye(4))[2]['arc5']
    p2=[(i*i/16,L,T,R) for i,(tau,L,T,R) in enumerate(p)]
    b=arc_diagnostics(p2,np.eye(4))[2]['arc5'];self.assertAlmostEqual(a,b)
 def test_metric_convention(self):
    self.assertGreater(np.linalg.norm(np.sqrt(np.diag(metric_matrix('declared_diagonal_stress')))*np.array([0,0,1,0])),1.)
 def test_cancellation(self):
    self.assertAlmostEqual(cancellation(np.array([1.,0,0,0]),np.array([-1.,0,0,0])),1.)
 def test_angle(self):self.assertAlmostEqual(safe_angle(np.array([1,0]),np.array([0,1])),90.)
if __name__=='__main__':unittest.main()
