import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import numpy as np
from pairwise_math import PAIRS,shapley_pair_attribution
from run_audit import pair_ratio_ledger,P67,P78
class TestHandover(unittest.TestCase):
    def test_pair_indexing(self):
        self.assertEqual(PAIRS[P67],(5,6));self.assertEqual(PAIRS[P78],(6,7))
    def test_shapley_closure(self):
        b={'numerator':np.ones(45),'gap':np.ones(45)*2}
        a={'numerator':np.ones(45)*3,'gap':np.ones(45)*4}
        z=shapley_pair_attribution(b,a)
        self.assertLess(z['closure_error'],1e-12)
        self.assertLess(max(abs(z['numerator_attribution']+z['gap_attribution']-z['delta_pair_norm_sq'])),1e-12)
    def test_ratio_ledger(self):
        n=np.ones(45);g=np.ones(45)*2
        n[P67]=2;n[P78]=4;g[P67]=3;g[P78]=1
        s={'numerator':n,'gap':g,'pair_K_frob_sq':2*(n/g)**2}
        l=pair_ratio_ledger(s)
        self.assertAlmostEqual(l['log_power_ratio_78_over_67'],l['log_numerator_ratio_term']+l['log_inverse_gap_ratio_term'],places=12)
    def test_shapley_signed(self):
        b={'numerator':np.ones(45)*2,'gap':np.ones(45)}
        a={'numerator':np.ones(45),'gap':np.ones(45)*2}
        z=shapley_pair_attribution(b,a)
        self.assertLess(z['numerator_attribution'][0],0)
        self.assertLess(z['gap_attribution'][0],0)
if __name__=='__main__':unittest.main()
