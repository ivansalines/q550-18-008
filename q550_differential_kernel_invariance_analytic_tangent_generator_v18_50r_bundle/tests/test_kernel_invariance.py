#!/usr/bin/env python3
"""Deterministic algebraic and finite-difference controls independent of Q550 replay."""
from pathlib import Path
import importlib.util
import sys
import numpy as np

mod_path=Path(__file__).resolve().parents[1]/'scripts/run_audit.py'
spec=importlib.util.spec_from_file_location('q550_v18_50r_test',mod_path)
a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
rng=np.random.default_rng(182350)
# 4x10 normalized observer Jacobian: rank exactly three, left-null direction fixed.
d=rng.normal(size=4);d/=np.linalg.norm(d)
B0=(np.eye(4)-np.outer(d,d))@rng.normal(size=(4,10))
Bdot=(np.eye(4)-np.outer(d,d))@rng.normal(size=(4,10))*.3
J=rng.normal(size=(10,10))*.2
z=a.kernel_defect(B0,Bdot,J)
assert np.linalg.matrix_rank(B0,tol=1e-9)==3
assert np.linalg.norm(d@B0)<1e-13
assert np.linalg.norm(B0@z['P'])<1e-11
assert np.linalg.norm(z['P']@z['P']-z['P'])<1e-12
assert z['identity_residual']<2e-11
assert z['B_defect_identity_residual']<2e-11
assert np.linalg.norm(z['discrepancy'],'fro')/np.linalg.norm(z['lifted'],'fro') - np.sqrt(2) <1e-10
# Finite-difference check of the projector derivative at constant rank.
h=1e-5
Pplus=a.null_projector(B0+h*Bdot)[0]
Pminus=a.null_projector(B0-h*Bdot)[0]
assert np.linalg.norm((Pplus-Pminus)/(2*h)-z['Pdot'])<1e-6
# If Bdot=-B J on the kernel, the kernel is infinitesimally invariant.
Bdot_cancellation=-B0@J
z2=a.kernel_defect(B0,Bdot_cancellation,J)
assert np.linalg.norm(z2['D'])<1e-12
assert np.linalg.norm(z2['discrepancy'])<1e-11
# Analytic chart transformation has the same action as a similarity mapping.
j=np.zeros((11,11));j[:10,:10]=rng.normal(size=(10,10))
s=np.exp(rng.normal(size=10))
x=rng.normal(size=10)
Jc=a.chart_analytic_generator(j,s)
assert np.allclose(Jc@x,s*(j[:10,:10]@(x/s)),rtol=1e-13,atol=1e-13)
# Fourth-order derivative and dt-refinement of a smooth polynomial field.
h=1e-3
fun=lambda t: np.array([[1+2*t+3*t*t+t**3+t**4]])
diff=a.fivepoint_derivative([fun(v) for v in [-2*h,-h,h,2*h]],h)
assert abs(float(diff[0,0])-2)<1e-10
print('v18.50r algebraic kernel, analytic chart, stencil and projector tests PASS')
