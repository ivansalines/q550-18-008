import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from geometry_math import decompose,transports,projector_transport_error,PAIRS,I67,I78,I68
class TestGeometry(unittest.TestCase):
 def test_pairs(self):
  self.assertEqual(len(PAIRS),45)
  self.assertEqual((PAIRS[I67],PAIRS[I78],PAIRS[I68]),((5,6),(6,7),(5,7)))
 def test_lie_bracket(self):
  from geometry_math import pair_generators
  A=np.eye(10);w=np.zeros((10,10));w[6,5]=2;w[5,6]=-2;w[7,6]=3;w[6,7]=-3
  parts=pair_generators({'axes':A,'Omega':w});p,q=parts[I67],parts[I78]
  comm=p@q-q@p
  self.assertAlmostEqual(np.linalg.norm(comm),np.sqrt(2)*6,places=12)
  self.assertAlmostEqual(np.linalg.norm(comm-comm.T*-1),0.,places=12)
 def test_transport_identity(self):
  z=np.zeros((10,10));o={'K':z,'two':z,'other':z,'parts':np.zeros((45,10,10))}
  U,Ut,Uo,U68=transports([o]*5,.01)
  for a in (U,Ut,Uo,U68):self.assertLess(np.linalg.norm(a-np.eye(10)),1e-14)
  p=np.eye(10)[None,...]
  self.assertAlmostEqual(projector_transport_error(U,p,p,indices=(0,)),0.)
if __name__=='__main__': unittest.main()
