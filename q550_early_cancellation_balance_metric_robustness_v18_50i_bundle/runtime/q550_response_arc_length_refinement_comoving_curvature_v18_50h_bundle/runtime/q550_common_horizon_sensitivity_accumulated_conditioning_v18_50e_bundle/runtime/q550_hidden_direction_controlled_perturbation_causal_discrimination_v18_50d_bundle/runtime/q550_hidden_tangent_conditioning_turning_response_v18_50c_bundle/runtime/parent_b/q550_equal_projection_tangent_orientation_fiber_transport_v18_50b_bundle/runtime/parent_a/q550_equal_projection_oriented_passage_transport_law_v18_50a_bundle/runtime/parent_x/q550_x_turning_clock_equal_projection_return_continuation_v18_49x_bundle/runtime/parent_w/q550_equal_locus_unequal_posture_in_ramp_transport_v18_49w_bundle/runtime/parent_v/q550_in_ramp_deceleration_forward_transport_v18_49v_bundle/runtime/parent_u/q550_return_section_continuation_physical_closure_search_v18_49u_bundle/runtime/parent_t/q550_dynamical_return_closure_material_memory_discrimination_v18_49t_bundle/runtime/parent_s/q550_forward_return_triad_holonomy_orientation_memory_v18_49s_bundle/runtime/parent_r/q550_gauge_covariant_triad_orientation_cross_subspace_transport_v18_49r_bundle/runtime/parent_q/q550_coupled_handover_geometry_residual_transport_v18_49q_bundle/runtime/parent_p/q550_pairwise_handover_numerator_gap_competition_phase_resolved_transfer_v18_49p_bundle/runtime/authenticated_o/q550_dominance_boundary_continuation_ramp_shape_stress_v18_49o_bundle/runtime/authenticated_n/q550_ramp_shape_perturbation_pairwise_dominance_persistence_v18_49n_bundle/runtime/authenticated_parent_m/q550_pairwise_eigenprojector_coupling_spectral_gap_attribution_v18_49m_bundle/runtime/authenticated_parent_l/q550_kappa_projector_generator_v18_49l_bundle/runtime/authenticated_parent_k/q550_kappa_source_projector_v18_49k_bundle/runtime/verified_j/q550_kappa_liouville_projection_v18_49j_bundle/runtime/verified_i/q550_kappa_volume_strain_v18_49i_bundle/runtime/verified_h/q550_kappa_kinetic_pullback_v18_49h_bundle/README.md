# Q550 v18.49h — Kinetic-Metric Pullback & Covariant Material Curvature Audit

This bundle is an **authentic executable research audit**, not a physical theorem. It extends the SHA-authenticated **v18.49g server sendback** and the recursively verified original Q550 11D lineage back to v18.48j.

## Scientific purpose

The previous v18.49g compared full-10D direction paths in a declared **Euclidean historical observer-complement chart**. That curve cannot be given a metric-independent interpretation. This audit builds a kinetic metric from the exact historical mechanical energy, and follows **the entire material 10D state**, without projecting away any historical observer family.

Physical solver coordinates are:

`(log(rho1), v1, theta1, omega1, log(rho2), v2, theta2, omega2, logit(x), vz)`.

The original model's tau-time kinetic energy is

`T = 0.5*(rho1**2*(v1**2+omega1**2) + rho2**2*(v2**2+omega2**2) + m_x*(x*(1-x)*vz)**2)`.

Introduce the physical configuration in Cartesian form:

`Q=(rho1*cos(theta1),rho1*sin(theta1),rho2*cos(theta2),rho2*sin(theta2),sqrt(m_x)*x)`.

Its tau-time velocity is `V=dQ/dtau`. **Precisely** `T=V.T@V/2`. The full material state embedding is `H=(Q,tau_ref*V)`; its chart pullback metric is `G=DH.T@DH`. This is the ordinary Sasaki construction for the **flat kinetic base** of this specific model, with `tau_ref` an explicitly declared choice of position/velocity relative weight. The original physical dynamics need not be geodesic.

For the return flow's 10D material tangent operator `F`, the generalized Cauchy–Green tensor is

`C=F.T@G_end@F`, eigenvalues of `C v = lambda G_start v`, material stretch factors `sqrt(lambda)`.

With a finite forward/return material separation, take the **exact Cartesian secant** `delta_H=H(return)-H(forward)` and pull it back along the **linearized** return flow in the initial Cartesian tangent frame. Its unit vector forms a direction curve on S9. Compute its full-sphere arclength, endpoint angle and geodesic curvature, with numerical grid-refinement checks. **Linearized pullback of a finite gap is NOT an exact nonlinear flow inverse**, and no claim of exact finite-distance isometry is made.

## Scope / original data

- Families: `phaseblind`, branch 0 only; both original and autonomous kappa0.
- Six actual smooth reversal times: 0.285, 0.292, 0.296333, 0.300, 0.305, 0.309 xi.
- 14 original 11D integrations (2 forward, 12 return) and 12 full tangent propagators.
- Position/velocity weight `tau_ref` scanned at 0.5, 1 and 2; this **is a metric sensitivity study**, not changing the original IVP.
- Three clock-matched comparison phases q=0.35, 0.50, 0.65; 36 high-resolution curves on q=0.30..0.70.
- 8 independent mathematical unit tests, Jacobian finite difference, exact original kinetic-energy comparison, nonlinear coordinate covariance and spherical-geodesic controls.

## Validated numerical results (tau_ref=1)

At q=0.50 over 12 original return trajectories:

- Smallest material stretch across all runs: `0.409463308147228`.
- Largest material stretch across all runs: `2.3184204841293985`.
- Largest/smallest stretch ratio per run: `5.63854...5.66210`.
- S9 curvature at q=0.50: `1.38941...1.40199`, **with the new metric/observable only**.
- Max historical 11D regression error: `3.43e-13`.
- Kinetic-energy reconstruction error: `1.11e-16`.
- Nonlinear-coordinate generalized-eigenvalue covariance residual: `1.78e-15`.
- Sphere path arclength refinement (121 to 241 samples): maximum `3.73e-05` degrees.

At ramp 0.300 xi and original kappa, excess path angle **between the two extrema** is ~1.19643 deg in the historical G observer-complement chart but ~0.013962 deg when following the entire kinetic-metric material secant. The two curves and metrics are **NOT the same mathematical observable**; this is a counterexample to interpreting the former number as universal intrinsic material strain.

As the ramp increases, geodesic curvature **at q=0.50** slightly increases, whereas excess total angular path **between the extrema** decreases. This is not contradictory: local curvature and global excess are distinct measurements over different parts of the same direction curve.

## How to run (Python 3.13)

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_kinetic_pullback_v18_49h_bundle.zip
cd q550_kappa_kinetic_pullback_v18_49h_bundle
bash run_on_server.sh 2>&1 | tee v18_49h_server.log
```

The runner checks all source SHA-256 pins **recursively**, runs tests, reproduces 11D integrations and tangent maps, writes figures and CSV, validates scientific gates, and builds `sendback.zip` with its own output manifest. `inputs/v18_49g_original_server_sendback.zip` is retained **byte-for-byte**. Original C/B/A/.../J scripts are extracted and verified from its nested history; they are not replaced by hypothetical stand-ins.

For a quick exploratory pilot, run **only**:

```bash
python3.13 scripts/run_audit.py --smoke --curvature-samples 41
```

The smoke run overwrites output with one test trajectory. To return to complete results, run `bash run_on_server.sh` with no extra flags.

## Files

- `scripts/kinetic_metric.py`: exact physical kinetic embedding, metric, generalized Cauchy–Green and nonlinear-coordinate test.
- `scripts/curvature_math.py`: full S9 local geodesic curvature and path-vs-endpoint excess.
- `scripts/run_audit.py`: authenticated 11D experiments.
- `scripts/frame_math.py`, `scripts/full10d_math.py`: exact retained G helper sources.
- `scripts/verify_parent.py`: SHA-256-gated nested historical verification.
- `scripts/check_outputs.py`, `scripts/plot_results.py`, `scripts/pack_sendback.py`: scientific gates, real figures and manifest.
- `tests/test_kinetic_metric.py`: eight mathematical tests.
- `results/report.json`: measured summary, precision checks and boundaries.
- `results/kinetic_deformation_eigenvalues.csv`, `kinetic_sphere_curvature.csv`, `kinetic_orientation_profiles.csv`, `metric_comparison_with_G.csv`: quantitative outputs.
- `results/*.png`: four real diagnostics; no synthetic illustrations.

## Limitations

This audit establishes covariance of the **declared** metric under consistent chart changes, not invariance to replacing the metric. It does not establish an observer-independent material torsion invariant, intrinsic kappa0 period, physical hysteresis theorem or interval-certified global convergence.
