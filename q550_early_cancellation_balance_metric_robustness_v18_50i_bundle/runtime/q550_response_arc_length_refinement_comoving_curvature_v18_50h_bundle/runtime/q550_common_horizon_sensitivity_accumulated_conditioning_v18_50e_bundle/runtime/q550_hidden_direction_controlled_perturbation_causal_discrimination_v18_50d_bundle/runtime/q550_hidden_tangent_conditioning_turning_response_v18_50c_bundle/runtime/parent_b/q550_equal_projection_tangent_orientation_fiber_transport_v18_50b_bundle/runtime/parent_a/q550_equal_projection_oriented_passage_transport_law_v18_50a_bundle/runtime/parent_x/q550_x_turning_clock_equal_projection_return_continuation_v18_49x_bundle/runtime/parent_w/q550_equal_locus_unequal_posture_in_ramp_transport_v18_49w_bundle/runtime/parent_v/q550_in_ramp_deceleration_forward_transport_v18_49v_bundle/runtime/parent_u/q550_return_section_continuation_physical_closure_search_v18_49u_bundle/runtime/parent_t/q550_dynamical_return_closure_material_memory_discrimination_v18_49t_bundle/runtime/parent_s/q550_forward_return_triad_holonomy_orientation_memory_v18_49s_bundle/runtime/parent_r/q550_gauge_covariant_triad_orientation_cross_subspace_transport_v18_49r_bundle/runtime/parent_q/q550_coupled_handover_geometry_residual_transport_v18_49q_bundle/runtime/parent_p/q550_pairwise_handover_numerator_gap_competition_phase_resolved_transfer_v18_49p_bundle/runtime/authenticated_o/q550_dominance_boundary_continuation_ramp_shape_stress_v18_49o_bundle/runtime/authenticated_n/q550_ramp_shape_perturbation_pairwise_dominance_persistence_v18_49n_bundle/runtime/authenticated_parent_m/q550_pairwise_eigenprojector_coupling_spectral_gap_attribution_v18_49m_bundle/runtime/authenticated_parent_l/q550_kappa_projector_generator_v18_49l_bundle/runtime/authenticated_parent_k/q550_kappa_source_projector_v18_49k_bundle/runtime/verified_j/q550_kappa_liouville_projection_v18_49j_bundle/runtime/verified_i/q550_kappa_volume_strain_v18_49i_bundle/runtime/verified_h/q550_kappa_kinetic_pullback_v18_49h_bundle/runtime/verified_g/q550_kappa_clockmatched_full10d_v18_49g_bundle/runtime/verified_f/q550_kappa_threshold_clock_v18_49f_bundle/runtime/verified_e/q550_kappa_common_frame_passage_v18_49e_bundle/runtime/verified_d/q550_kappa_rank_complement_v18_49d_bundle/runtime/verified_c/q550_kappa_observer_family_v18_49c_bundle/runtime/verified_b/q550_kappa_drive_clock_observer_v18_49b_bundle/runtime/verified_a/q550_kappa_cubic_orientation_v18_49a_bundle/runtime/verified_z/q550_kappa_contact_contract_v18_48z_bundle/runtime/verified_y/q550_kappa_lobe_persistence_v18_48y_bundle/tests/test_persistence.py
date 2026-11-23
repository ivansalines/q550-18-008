"""Unit tests are algebraic/numerical controls, not the Q550 physical replay."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from persistence_math import barrier,minimum,root_intervals,sample_curvature,critical_bracket
class TestPersistenceMath(unittest.TestCase):
    def test_known_quadratic_barrier_curvature(self):
        f=lambda q:.01-3*(q-.4815)**2
        b=barrier(f)
        self.assertAlmostEqual(b['q'],.4815,places=6)
        self.assertAlmostEqual(b['curvature_richardson'],-6.,places=6)
    def test_two_components_when_below_barrier(self):
        q=np.linspace(.1,.9,1601)
        f=lambda t: ((t-.40)*(t-.56))**2+.001
        z=np.array([f(t) for t in q])
        spans=root_intervals(q,z,.00102,f)
        self.assertEqual(len(spans),2)
    def test_one_component_when_above_barrier(self):
        q=np.linspace(.1,.9,1601)
        f=lambda t: ((t-.40)*(t-.56))**2+.001
        spans=root_intervals(q,np.array([f(t) for t in q]),.002,f)
        self.assertEqual(len(spans),1)
    def test_no_components_below_minima(self):
        q=np.linspace(.1,.9,801)
        f=lambda t: ((t-.40)*(t-.56))**2+.001
        self.assertEqual(root_intervals(q,np.array([f(t) for t in q]),.0001,f),[])
    def test_known_curvature(self):
        f=lambda q:2-5*q*q
        self.assertAlmostEqual(sample_curvature(f,0,.001),-10.,places=8)
    def test_threshold_crossing_bracket(self):
        rows=[{'ramp_duration_xi':r,'barrier_distance_3D':.03-r} for r in (.01,.02,.03)]
        b=critical_bracket(rows,.015)
        self.assertEqual((b['left_ramp'],b['right_ramp']),(.01,.02))
    def test_missing_crossing(self):
        a=[{'ramp_duration_xi':r,'barrier_distance_3D':v} for r,v in [(.1,.007),(.2,.005)]]
        self.assertIsNone(critical_bracket(a,.01))
    def test_minima(self):
        f=lambda q:(q-.42)**2+.003
        a=minimum(f,(.355,.466))
        self.assertAlmostEqual(a['q'],.42,places=7)
        self.assertAlmostEqual(a['distance'],.003,places=7)
    def test_curvature_refinement_stability(self):
        f=lambda q:np.cos(5*(q-.4815))+.01
        b=barrier(f)
        self.assertLess(b['curvature_step_variation'],1e-5)
        self.assertLess(abs(b['curvature_richardson']+25),1e-5)
if __name__=='__main__':unittest.main()
