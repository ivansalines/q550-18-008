import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from response_math import unit,central_directional,split_response
class TestMath(unittest.TestCase):
    def test_unit(self):self.assertAlmostEqual(np.linalg.norm(unit([3,4],[1,1])),1)
    def test_zero(self):
        fun=lambda y: y[1:3]**2
        np.testing.assert_array_equal(central_directional(fun,np.ones(3),np.zeros(3)),[0,0])
    def test_chain(self):
        def f(y):return unit([y[0]+y[1],2*y[1]+y[2]],np.ones(2))
        y=np.array([1.,.2,.3]);v=np.array([1.,2.,-1.])
        a,b,c,r=split_response(f,y,v,x_index=0)
        self.assertLess(r,1e-7)
        self.assertLess(np.linalg.norm(c-a-b),1e-7)
    def test_linearization(self):
        f=lambda y: unit([1+y[0],y[1]],[1,1])
        y=np.array([0.,0.]);v=np.array([1.,0.])
        a,b,c,r=split_response(f,y,v,x_index=0)
        self.assertLess(np.linalg.norm(b),1e-10)
if __name__=='__main__':unittest.main()
