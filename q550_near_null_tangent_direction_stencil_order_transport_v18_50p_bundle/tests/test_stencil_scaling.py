"""Fast mathematical controls, independent of historical solver replay."""
import importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'scripts/run_audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
old,_,_,_=audit.verify_parent()
r=audit.old_scaling(old)
assert len(r)==6
assert all(3.98<d['s4_ratio']<4.02 for d in r)
# A centered difference of a cubic term has exactly quadratic stencil error.
F=lambda x: np.array([x**3,2*x**3])
h=1e-3
d=lambda h:(F(h)-F(-h))/(2*h)
assert np.allclose(d(2*h),4*d(h),rtol=1e-12)
assert np.linalg.norm((4*d(h)-d(2*h))/3)<1e-12
assert abs(audit.sign_free_cos(np.array([0.,-1.]),np.array([0.,1.]))-1)<1e-15
print('v18.50p authenticated parent and stencil-order tests PASS')
