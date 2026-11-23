import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_audit import compose,locate_peak,normalized
class GeometryAudit(unittest.TestCase):
 def test_perfect_parallel(self):
  z=compose(np.array([1.,0.]),np.array([1.,0.]));self.assertAlmostEqual(z['cancellation'],0)
 def test_perfect_antiparallel(self):
  z=compose(np.array([1.,0.]),np.array([-1.,0.]));self.assertAlmostEqual(z['cancellation'],1)
 def test_off_axis(self):
  z=compose(np.array([1.,0.]),np.array([-1.,1.]));self.assertTrue(0<z['cancellation']<1)
 def test_common_chart_scale(self):
  a=np.array([1.,3.,-2.,4.]);s=np.array([1.,2.,3.,4.])
  self.assertTrue(np.allclose(normalized(a/s),normalized(a/(s*8))))
 def test_peak_interior(self):
  p=locate_peak([{'horizon_xi':1,'cancellation':.1,'T_over_L':2,'LT_cos':-1}, {'horizon_xi':2,'cancellation':.5,'T_over_L':1,'LT_cos':-.5},{'horizon_xi':3,'cancellation':.2,'T_over_L':3,'LT_cos':-.1}]);self.assertTrue(p['interior']);self.assertEqual(p['bracket'],(1,3))
if __name__=='__main__':unittest.main()
