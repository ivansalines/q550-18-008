# v18.49v decision rules

**Positive in-ramp motion**: genuine 11D integration with material coordinate path > sampled solver floor and material speed > motion floor while drive zero. No intrinsic monotonic slowing required.

**Partial deceleration**: only if |dstate/dξ| in declared 10D coordinate norm actually decreases across the relevant interval. Clock deceleration alone must be reported separately.

**Triad orientation**: only where 10D Cauchy-Green eigenvalues are nondegenerate; transport angle relative to fixed σ=0.10 spectral frame is a discretized gauge-aligned diagnostic, not a material-body Euler angle. A sample skipped because of near degeneracy cannot be interpolated into an apparent rotation.

**Numerical fidelity**: genuine original model RHS, historical regression, correct clock sign, original mechanical work/damping/source ledger, explicit spectral closure where defined, no substitutions to produce success.

**Physical-memory or physical-volume claim**: expressly OUT OF SCOPE; the phase/quadrant construction is not hardwired into the dynamics.
