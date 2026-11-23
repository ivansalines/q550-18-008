# Q550 v18.49l — Covariant Projector Generator & Material Strain-Rate Audit

## Question

Can the principal-strain projector rotation be reconstructed **directly** from the derivative of the kinetic Cauchy–Green tensor, with no intermediate source-zero, while discriminating principal stretching from rotation of the eigenspaces? Do the resulting clock-matched diagnostics survive changes in ramp, kappa and a fixed kinetic-frame rotation? Which mathematical statements are identities and which are only numerical associations?

## Genuine lineage and integration

The source `inputs/v18_49k_original_server_sendback.zip` is the **byte-for-byte original uploaded server sendback** from 2026-10-29 (SHA-256 pinned in `inputs/SOURCE_PINS.json`). `scripts/verify_parent.py` checks CRC, SHA-256 of all files in the parent's manifest, exact member list, then calls its recursive verifier back to historical v18.48j. Original physical ODEs, smooth return design, analytic structural material Jacobian and the full 11D histories are loaded from that authenticated hierarchy. This audit performs **14 genuine 11D integrations** and **12 independent 10×10 tangent fundamental-matrix integrations**. No toy dynamics are substituted into the Q550 calculation.

Simulation: phaseblind branch 0, Q550, ramp durations `0.285, 0.292, 0.296333, 0.300, 0.305, 0.309`, `kappa0=1/6` versus the inherited autonomous kappa. Common return clock `q ∈ [0.35,0.65]` at 121 evenly-spaced samples, `t = ramp_xi+q`. The initial kinetic metric comes from the **exact five-coordinate Cartesian kinetic embedding** `H=(Q,tau_ref*V)` with declared `tau_ref=1`. The *source zero* is deliberately absent from the mathematical definition of the primary observables.

## Mathematical construction

At each point, `F(q)` solves the *analytic* material tangent equation `Fdot=J_material F`, `F(0)=I`. The derivative of the kinetic embedding's Jacobian `J_H` is computed by a small symmetric directional stencil along the actual material vector field, not by fitting a smooth numerical trajectory. In the fixed initial kinetic frame,

```
B       = DH(y(q)) F(q) [DH(y(0))]^-1
Bdot    = (D_q DH(y(q)) + DH(y(q)) J_material(q)) F(q) [DH(y(0))]^-1
C       = B.T B
Cdot    = Bdot.T B + B.T Bdot
```

For `C A = A diag(lambda)` with separated positive eigenvalues, the spectral generator is

```
Omega[j,i] = (A.T Cdot A)[j,i] / (lambda[i]-lambda[j])   for j != i
Omega[i,i] = 0
K          = A Omega A.T          (skew symmetric)
P_i        = a_i a_i.T
Pdot_i     = K P_i - P_i K
sigma_i'   = (a_i.T Cdot a_i)/(2 sigma_i)
```

All primes mean differentiation on the **registered clock q**. The instantaneous projector speed is `||Pdot_i||_F/sqrt(2)`, independent of the sign of `a_i`. Aggregate speed is the norm of these ten speeds, numerically equal to `||K||_F`. The unit-interval log-strain-rate vector is `sigma_i'/sigma_i`. The scalar `tr(B^-1 Bdot)` agrees with `sum_i sigma_i'/sigma_i` (Liouville), and is independently checked against the kinetic-volume source in the parent server K results.

Off-diagonal Cdot fraction in the instantaneous C eigenbasis and the normalized commutator `[C,Cdot]` are reported to distinguish axis rotation from principal-stretch rates. Both ratios depend on the declared kinetic metric; neither is a new conserved quantity. A simple spectrum is required for separate rank-one projectors: `min_relative_eigengap` is monitored in every sample. Near degeneracy, only cluster projectors are naturally robust, and the implemented rank-one routine rejects a too-small gap.

## Measured findings from the preflight (not a certificate)

At `q=0.50`, original kappa, the Frobenius generator norm rises from ~5.4949 to ~5.7299 as ramp changes 0.285→0.309; the log-strain-rate norm rises from ~0.9685 to ~1.0343. At ramp 0.300, generator norm ~5.62643, log-strain-rate norm ~1.00745, and off-diagonal fraction of `Cdot` ~0.98419 at the same phase. The agreement of these trends across six ramps does **not** establish a causal relationship or metric-independent invariant. Autonomous-kappa histories are recomputed independently and give nearby, non-identical numbers.

The smallest relative eigengap across the 12 reconstructed histories is ~0.0846 (using **lambda** gaps). Independent finite differences of rank-one projectors confirm the analytic commutator-derived projector rates on the 121-point clock grid within finite-difference truncation. The invariant sum rule relating principal log-strain rates and kinetic-volume source passes. Synthetic tests include a rotating eigenspace with zero principal-strain rate, a pure diagonal stretch with no rotating eigenspace, a fixed orthogonal frame change, and an explicit time-dependent gauge connection correction.

### Limitations that must not be lost

1. `C`, `K`, principal directions and the kinetic-volume source are attached to an explicitly declared kinetic metric and scale `tau_ref=1`. They are not independent of any possible physical metric.
2. Under **time-independent orthogonal** changes of the common initial kinetic frame, `K` and projectors transform by conjugation. Under **time-dependent** changes, an affine `Rdot R.T` term appears; connection-corrected derivatives are needed. Blindly using a moving basis gives spurious rotation.
3. Observed finite differences between separate nonlinear trajectories are not exact nonlinear parallel transports or causal mode energy flows.
4. The commutator relationship and sum rule are algebraic/geometric identities, not newly discovered laws of Q550.
5. The finite-difference comparisons and all historical replays are ordinary double-precision numerical experiments, not interval or topological certificates.

## Server execution

```bash
cd /root/elab1/hysteresis
unzip 49l_full.zip
cd q550_kappa_projector_generator_v18_49l_bundle
bash run_on_server.sh 2>&1 | tee v18_49l_server.log
```

Set `Q550_PYTHON=python3` if Python 3.13 is not the correct interpreter. Dependencies: `numpy scipy matplotlib` (versions captured in `results/environment.json`). Python source comments and documents are entirely in English. The runner checks eight independent unit tests, executes the authenticated physical integration, checks numerical acceptance gates, generates three PNG plots and writes an authenticated `sendback.zip`. The original K ZIP and nested history are conserved unchanged inside the new archive.

## Primary files

- `scripts/run_audit.py` — original-equation 11D/10D replay and tensors.
- `scripts/generator_math.py` — Cauchy–Green derivative, principal eigenspace generator, strain/volume rates.
- `scripts/verify_parent.py` — original K ZIP integrity and recursive ancestry authentication.
- `scripts/check_outputs.py` — quantitative replay gates.
- `tests/test_generator_math.py` — eight algebraic/geometric regression tests.
- `results/covariant_generator_phase_profiles.csv` — all phase-matched generator and strain-rate traces.
- `results/principal_strain_projector_phase_profiles.csv` — four principal-mode details (1,3,8,10).
- `results/ramp_kappa_summary.csv`, `results/report.json`, `results/environment.json`.
- `results/*.png` — three actual numeric diagnostic plots.
- `inputs/v18_49k_original_server_sendback.zip` — unmodified 49k authenticated original and ancestry.
- `SHA256SUMS_OUTPUT.json` — generated manifest, both in the distributed archive and server sendback.
