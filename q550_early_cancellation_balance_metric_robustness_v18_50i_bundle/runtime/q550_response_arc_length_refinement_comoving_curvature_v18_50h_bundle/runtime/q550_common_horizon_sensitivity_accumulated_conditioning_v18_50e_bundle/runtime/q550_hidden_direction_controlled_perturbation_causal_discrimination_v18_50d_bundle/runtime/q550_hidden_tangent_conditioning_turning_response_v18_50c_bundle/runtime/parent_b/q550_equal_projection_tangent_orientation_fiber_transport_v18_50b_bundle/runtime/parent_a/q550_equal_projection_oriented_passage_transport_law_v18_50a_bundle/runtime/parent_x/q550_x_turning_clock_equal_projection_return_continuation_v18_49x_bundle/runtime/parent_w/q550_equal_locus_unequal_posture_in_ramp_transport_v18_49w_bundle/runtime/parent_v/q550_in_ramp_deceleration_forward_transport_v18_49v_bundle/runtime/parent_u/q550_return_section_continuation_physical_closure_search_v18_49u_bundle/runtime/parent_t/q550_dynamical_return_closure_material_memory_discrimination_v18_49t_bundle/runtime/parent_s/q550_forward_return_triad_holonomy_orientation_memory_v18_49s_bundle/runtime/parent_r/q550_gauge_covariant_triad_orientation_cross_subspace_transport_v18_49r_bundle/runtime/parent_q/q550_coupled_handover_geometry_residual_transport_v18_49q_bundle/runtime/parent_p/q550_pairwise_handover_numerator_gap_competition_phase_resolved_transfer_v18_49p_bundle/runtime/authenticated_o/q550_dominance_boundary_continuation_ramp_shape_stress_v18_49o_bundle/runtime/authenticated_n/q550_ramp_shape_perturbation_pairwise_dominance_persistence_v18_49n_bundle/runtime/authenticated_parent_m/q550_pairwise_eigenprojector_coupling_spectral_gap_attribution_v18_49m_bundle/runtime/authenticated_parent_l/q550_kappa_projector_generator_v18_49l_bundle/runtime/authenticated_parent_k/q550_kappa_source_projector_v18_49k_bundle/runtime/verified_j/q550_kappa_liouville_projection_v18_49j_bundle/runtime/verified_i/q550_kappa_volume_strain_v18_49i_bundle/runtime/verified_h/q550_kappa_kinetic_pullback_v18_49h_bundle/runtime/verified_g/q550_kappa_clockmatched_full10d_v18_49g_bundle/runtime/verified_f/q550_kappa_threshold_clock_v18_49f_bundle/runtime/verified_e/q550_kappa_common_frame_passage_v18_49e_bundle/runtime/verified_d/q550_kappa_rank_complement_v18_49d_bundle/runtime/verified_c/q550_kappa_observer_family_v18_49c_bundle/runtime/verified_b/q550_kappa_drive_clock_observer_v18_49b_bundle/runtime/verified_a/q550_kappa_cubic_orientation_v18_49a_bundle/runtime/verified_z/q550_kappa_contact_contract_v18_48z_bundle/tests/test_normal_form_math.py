import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from scipy.optimize import brentq
from normal_form_math import fit_jet,polynomial_gap,asymptotic_gaps,contract_ratio,affine_check
class TestNormalForm(unittest.TestCase):
 def test_pure_quadratic(self):
  q=np.linspace(.40,.60,401);qb=.5;B=.015;C=-5.
  d=B+C*(q-qb)**2/2
  fit=fit_jet(q,d,qb,B,.03,4)
  self.assertAlmostEqual(fit['derivatives'][2],C,7)
  self.assertAlmostEqual(fit['derivatives'][3],0,6)
  self.assertAlmostEqual(fit['derivatives'][4],0,4)
  for delta in (1e-6,1e-4,4e-4):
   G=polynomial_gap(B,fit['derivatives'],4,delta)
   self.assertAlmostEqual(contract_ratio(G,delta,C),1,9)
 def test_quartic_correction_sign_and_order(self):
  B=.015;C=-5.2;D3=13.;D4=50.
  d={1:0.,2:C,3:D3,4:D4}
  for delta in (2e-6,1e-5,1e-4):
   actual=polynomial_gap(B,d,4,delta)
   quadratic,corrected,_=asymptotic_gaps(delta,C,D3,D4)
   self.assertLess(abs(corrected-actual),abs(quadratic-actual))
 def test_affine_phase_gauge(self):
  for val in (.002,.005,.01):
   a=contract_ratio(val,.0002,-5.42)
   b=affine_check(val,.0002,-5.42,2.3)
   self.assertAlmostEqual(a,b,13)
 def test_bad_curvature(self):
  with self.assertRaises(ValueError):asymptotic_gaps(.0001,5.)
 def test_constrained_phase_fit_noise(self):
  q=np.linspace(.46,.50,81);qb=.48;B=.013
  d=B-2.6*(q-qb)**2+.15*(q-qb)**3-.5*(q-qb)**4
  f=fit_jet(q,d,qb,B,.019,4)
  self.assertAlmostEqual(f['derivatives'][2],-5.2,6)
  self.assertAlmostEqual(f['derivatives'][3],.9,5)
if __name__=='__main__':unittest.main()
