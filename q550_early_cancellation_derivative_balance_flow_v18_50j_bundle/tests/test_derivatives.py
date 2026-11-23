#!/usr/bin/env python3
"""Pure analytical checks for the cancellation derivative ledger."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_audit import curve_C,derivative_terms

def test():
  for b,c in [(0.1,-.95),(.99,-.65),(1.01,-.646),(3.7,-.67),(.9,.1)]:
    for db,dc in [(10.,-2.),(-1.,3.),(0.,-1.)]:
      eps=1e-7
      der=(curve_C(b+eps*db,c+eps*dc)-curve_C(b-eps*db,c-eps*dc))/(2*eps)
      p,q=derivative_terms(b,c,db,dc)
      assert abs(der-p-q)<2e-8,(b,c,db,dc,der,p+q)
  for b in [0.,.1,1.,2.]:
    assert abs(curve_C(b,1.))<1e-12
    assert curve_C(b,-.5)>=-1e-12
  print('v18.50j analytical derivative tests PASS')
if __name__=='__main__':test()
