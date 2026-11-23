# Q550 v18.49m — Pairwise Eigenprojector Coupling & Spectral-Gap Attribution Audit

## Scientific question

The authenticated v18.49l server run showed rapid growth of the material Cauchy–Green projector generator toward q=0.65. Which of the **45 independent rank pairs** drive that increase? Is it attributable primarily to growth of off-diagonal tensor rates, inverse eigenvalue gaps, or both? Do the same findings recur across six ramp **durations** and both kappa choices?

## Genuine source and experiment

The embedded, unchanged server archive `inputs/v18_49l_original_server_sendback.zip` is pinned by SHA-256 in `inputs/SOURCE_PINS.json`. On replay, the runner checks CRC, every original manifest hash, exact archive membership and recursively authenticates the source lineage through the older v18.48j. The original 11D physical return solver and analytic 10×10 tangent Jacobian, loaded from that authenticated lineage, are used to perform **14 physical integrations and 12 tangent-frame integrations**. The historical phaseblind branch-0 trajectory is used as the physical starting state.

Cases: smoothstep command with ramp durations 0.285, 0.292, 0.296333, 0.300, 0.305, 0.309, each for original and autonomous kappa0. For each case, 121 samples at common return phases q=0.35 to 0.65. The metric is the declared kinetic embedding at tau_ref=1; no source-zero is used. **Alternative ramp shapes were not integrated in this audit**, so shape robustness has not been established.

## Mathematical operation

In the initial kinetic frame, let C=B.T B and Cdot be the analytic rate from the 10D tangent flow. Let C a_i=lambda_i a_i with a rank-ordered simple spectrum. For 1-based i<j define:

    N_ij = |a_j.T Cdot a_i|
    d_ij = lambda_i - lambda_j > 0
    w_ij = N_ij/d_ij = |Omega_{ji}|
    contribution to ||K||_F^2 = 2*w_ij^2

Since K is skew-symmetric with ten-dimensional simple spectrum, there are 45 independent pairs and ||K||_F^2 equals the sum of their squared contributions. The squared amplitudes do not depend on eigenvector sign; the ordered pairs are stable only while the eigenspectrum remains simple and correctly tracked.

To analyze the change between q0=0.50 and q1=0.65, construct F(n,d)=2*n^2/d^2 for each pair and compute the exactly closed symmetric (two-order) factor decomposition:

    Numerator := 0.5*((F(n1,d0)-F(n0,d0)) + (F(n1,d1)-F(n0,d1)))
    Gap       := 0.5*((F(n0,d1)-F(n0,d0)) + (F(n1,d1)-F(n1,d0)))
    Delta F   = Numerator + Gap

The decomposition is an **algebraic endpoint diagnostic**, not a causal separation of dynamical mechanisms. In particular the counterfactual pairs do not represent integrated physical trajectories, and this is not a claim of energy transfer between modes. Other decompositions could assign a different share to the interaction term; the symmetric prescription is disclosed to make the attribution reproducible.

## Actual preflight findings

For original kappa0 and ramp 0.300, ||K||_F grows from 5.626433 at q0 to 15.085692 at q1. The growth in squared norm decomposes into 111.99369 from numerator changes and 83.92767 from inverse-gap changes: 57.16% and 42.84%, respectively. The five strongest final couplings account for 89.30% of ||K(q1)||_F^2. The dominant pair is **6-7**: its |N| increases 0.147769 -> 0.500388, while its absolute eigenvalue gap contracts 0.130378 -> 0.057284; its signed contribution to delta ||K||^2 is 150.03961.

Across the twelve Q550 cases the leading final pair remains 6-7. The share of the final squared generator norm in the top five ranges 87.117% to 89.370%. This is robust across the tested ramp *durations*, but not a claim about other command shapes or different metrics.

## Validations and limits

- 14 algebraic/unit tests (eight inherited and six new) pass.
- Independent 10D generator Frobenius identity, sign-gauge independence and constant orthogonal coordinate changes are tested.
- Endpoint Shapley decomposition closes numerically for all 45 pairs in all twelve cases.
- Genuine original physical 11D and analytic tangent-frame 10D replay is compared with the authenticated L parent outputs.
- No exact interval certification, rank crossing/degenerate projector continuation, metric-independent physical angular momentum, mode energy flow, nonlinear curvature invariant or causal coupling is asserted.
- Time-dependent basis changes require the gauge connection; pair rankings in a different physical metric may change.

## Server execution

```bash
cd /root/elab1/hysteresis
unzip q550_pairwise_eigenprojector_coupling_spectral_gap_attribution_v18_49m_bundle.zip
cd q550_pairwise_eigenprojector_coupling_spectral_gap_attribution_v18_49m_bundle
bash run_on_server.sh 2>&1 | tee v18_49m_server.log
```

Requires Python >=3.10 with numpy, scipy, matplotlib; by default uses `python3.13` if available. Override with `Q550_PYTHON=python3`. The runner generates `sendback.zip` and an identical descriptively named `q550_pairwise_eigenprojector_coupling_spectral_gap_attribution_v18_49m_bundle_sendback.zip`, including this source, original parent ZIP, CSV files, figures, reports, manifest, and an authenticated source hierarchy on execution; the runtime extraction is intentionally omitted from the ZIP because the full historical chain is already stored inside the original parent archive.

## Output files

- `scripts/run_audit.py` actual 11D/10D replay script.
- `scripts/pairwise_math.py` exact 45-pair and symmetric attribution calculations.
- `scripts/verify_parent.py` original v18.49l authentication and recursive genealogy.
- `tests/test_generator_math.py`, `tests/test_pairwise_math.py` 14 unit tests.
- `results/pairwise_generator_phase_profiles.csv` 65,340 timestamped pair samples.
- `results/pairwise_shapley_comparison.csv` 540 pairwise comparisons q0.5 vs q0.65.
- `results/pairwise_case_summary.csv` all 12 case summaries.
- `results/covariant_generator_phase_profiles.csv`, `results/principal_strain_projector_phase_profiles.csv`, `results/ramp_kappa_summary.csv` inherited L-compatible controls.
- `results/*.png`, `results/report.json`, `results/environment.json`, `SHA256SUMS_OUTPUT.json`.
- `inputs/v18_49l_original_server_sendback.zip` unchanged original and nested executable ancestors.
