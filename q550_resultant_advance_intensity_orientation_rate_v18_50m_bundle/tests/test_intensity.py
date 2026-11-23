"""Tests of the geometric decomposition, independent of the parent data."""
import numpy as np
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
# Radial/transverse decomposition is an identity in fixed Euclidean coordinates.
r=np.array([3.,4.,0.,0.]); v=np.array([1.,2.,3.,0.]); n=r/np.linalg.norm(r)
rad=v@n;trans=np.linalg.norm(v-rad*n)
assert abs(np.linalg.norm(v)**2-rad**2-trans**2)<1e-12
assert abs(rad-2.2)<1e-12
# A temporal perturbation which scales the entire response rotates nothing.
r1=1.1*r
turn=np.degrees(np.arccos(np.clip((r@r1)/(np.linalg.norm(r)*np.linalg.norm(r1)),-1,1)))
assert abs(turn)<1e-5
p=root/'results'/'report.json'
if p.exists():
 d=json.loads(p.read_text()); a=d['original_primary']; b=d['autonomous_primary']
 for case in (a,b):
  assert case['vector_speed_at_stationary']>case['transverse_speed_at_stationary']>case['rate_norm_R_at_stationary']>0
  assert case['resultant_direction_turn_deg']>0.4
 assert d['checks']['all_four_common_cases_positive_radial_growth']
 assert d['checks']['all_four_common_cases_transverse_dominates_radial']
print('v18.50m projection and intensity tests PASS')
