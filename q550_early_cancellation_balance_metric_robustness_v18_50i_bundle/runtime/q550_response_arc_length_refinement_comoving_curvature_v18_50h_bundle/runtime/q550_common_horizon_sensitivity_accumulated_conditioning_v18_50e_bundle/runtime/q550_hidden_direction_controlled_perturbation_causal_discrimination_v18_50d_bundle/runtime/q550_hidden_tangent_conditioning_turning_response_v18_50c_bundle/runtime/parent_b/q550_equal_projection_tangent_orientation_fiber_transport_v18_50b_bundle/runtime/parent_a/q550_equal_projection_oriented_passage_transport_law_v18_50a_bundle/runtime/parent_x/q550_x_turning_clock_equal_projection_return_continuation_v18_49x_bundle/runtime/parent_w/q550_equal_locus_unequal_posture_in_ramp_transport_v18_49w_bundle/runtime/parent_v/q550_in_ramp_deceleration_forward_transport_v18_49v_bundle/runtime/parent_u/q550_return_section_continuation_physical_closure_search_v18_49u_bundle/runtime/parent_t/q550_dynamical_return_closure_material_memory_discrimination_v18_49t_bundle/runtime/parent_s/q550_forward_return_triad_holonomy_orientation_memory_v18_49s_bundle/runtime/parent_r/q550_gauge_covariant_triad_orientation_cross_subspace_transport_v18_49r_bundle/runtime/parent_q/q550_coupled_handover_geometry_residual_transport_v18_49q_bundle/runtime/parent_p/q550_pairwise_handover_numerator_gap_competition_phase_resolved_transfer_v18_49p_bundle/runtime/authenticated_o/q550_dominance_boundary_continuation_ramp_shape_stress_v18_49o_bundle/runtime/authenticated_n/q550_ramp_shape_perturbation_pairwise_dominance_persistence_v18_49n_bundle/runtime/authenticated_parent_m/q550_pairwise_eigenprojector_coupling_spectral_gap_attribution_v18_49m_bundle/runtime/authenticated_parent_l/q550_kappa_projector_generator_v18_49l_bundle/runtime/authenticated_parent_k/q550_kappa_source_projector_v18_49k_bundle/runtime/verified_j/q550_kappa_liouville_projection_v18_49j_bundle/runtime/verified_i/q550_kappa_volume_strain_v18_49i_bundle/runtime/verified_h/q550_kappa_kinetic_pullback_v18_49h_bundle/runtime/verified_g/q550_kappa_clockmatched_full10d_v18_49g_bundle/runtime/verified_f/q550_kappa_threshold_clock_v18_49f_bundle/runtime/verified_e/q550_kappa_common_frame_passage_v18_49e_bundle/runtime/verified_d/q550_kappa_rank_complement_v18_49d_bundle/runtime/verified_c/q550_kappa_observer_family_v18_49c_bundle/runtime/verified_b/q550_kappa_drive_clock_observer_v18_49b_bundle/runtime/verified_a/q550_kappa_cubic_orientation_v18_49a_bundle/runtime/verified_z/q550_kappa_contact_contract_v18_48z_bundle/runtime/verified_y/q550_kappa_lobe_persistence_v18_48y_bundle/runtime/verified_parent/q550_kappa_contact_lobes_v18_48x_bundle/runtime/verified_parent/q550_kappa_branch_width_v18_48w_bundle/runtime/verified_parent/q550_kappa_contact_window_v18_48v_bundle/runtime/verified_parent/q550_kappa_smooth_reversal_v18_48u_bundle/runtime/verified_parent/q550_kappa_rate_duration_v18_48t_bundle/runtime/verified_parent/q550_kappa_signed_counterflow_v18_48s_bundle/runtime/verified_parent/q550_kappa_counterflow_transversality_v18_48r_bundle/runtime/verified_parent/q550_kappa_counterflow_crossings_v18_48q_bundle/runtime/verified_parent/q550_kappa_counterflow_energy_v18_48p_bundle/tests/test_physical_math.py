#!/usr/bin/env python3
"""Exact source power-balance and controlled-drive tests (independent finite differences)."""
import importlib.util,math,sys,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'reference'),str(ROOT/'scripts')]
import physical_math as pm
from structural_jet import structural_jet

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
audit=module(ROOT/'reference/test_support_mobius_monodromy_audit.py','test_audit_ref')
support=module(ROOT/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','test_support_ref')
p=audit.ModelParameters(gamma_rho=.3);slope=.844357915384206/(2*math.pi)
SAMPLES=[np.array([.54,.001,.4,.49,-2.1,.02,-1.7,1.2,.001,.002,.11]),
         np.array([.536,-.002,-.5,.485,-2.9,1.1,-2.2,-1.6,.012,.014,.48]),
         np.array([.542,.003,1.3,.490,-1.85,-.9,.3,.5,-.013,-.01,.8])]
class BalanceTests(unittest.TestCase):
    def test_analytic_rhs_matches_original(self):
        for y in SAMPLES:
            for k in (1/6,35*math.pi/660):
                f=pm.rhs_from_original(y,k,p,slope,1,support,audit)
                ff=structural_jet(y,k,p,slope)[0]
                self.assertLess(np.linalg.norm(f-ff)/np.linalg.norm(f),1e-12)
    def test_energy_differential_identity(self):
        for y in SAMPLES:
            for k in (1/6,35*math.pi/660):
                for c in (-1,0,1):
                    f=pm.rhs_from_original(y,k,p,slope,c,support,audit)
                    h=1e-6/max(1.,np.linalg.norm(f))
                    fd=(pm.energy(y+h*f,k,p)-pm.energy(y-h*f,k,p))/(2*h)
                    analytical=sum(pm.power_terms(y,k,p,slope,c))
                    self.assertLess(abs(fd-analytical)/max(1.,abs(analytical)),2e-7)
    def test_clock_flip_only(self):
        y=SAMPLES[0];k=1/6
        f=pm.rhs_from_original(y,k,p,slope,1,support,audit)
        b=pm.rhs_from_original(y,k,p,slope,-1,support,audit)
        self.assertEqual(float(np.max(abs(f[:10]-b[:10]))),0.)
        self.assertAlmostEqual(f[10],-b[10],13)
    def test_inverse_geometry(self):
        a=SAMPLES[0];b=a.copy();b[2]+=2*math.pi;b[10]-=2*math.pi
        self.assertLess(pm.signed_displacement(a,b),1e-14)
        self.assertLess(pm.physical_shape_distance(a,b),1e-14)
    def test_physical_balance_dissipation(self):
        for y in SAMPLES:
            pw=pm.power_terms(y,1/6,p,slope,1)
            self.assertLessEqual(pw[1],0.)
            self.assertLessEqual(pw[2],0.)
if __name__=='__main__':unittest.main()
