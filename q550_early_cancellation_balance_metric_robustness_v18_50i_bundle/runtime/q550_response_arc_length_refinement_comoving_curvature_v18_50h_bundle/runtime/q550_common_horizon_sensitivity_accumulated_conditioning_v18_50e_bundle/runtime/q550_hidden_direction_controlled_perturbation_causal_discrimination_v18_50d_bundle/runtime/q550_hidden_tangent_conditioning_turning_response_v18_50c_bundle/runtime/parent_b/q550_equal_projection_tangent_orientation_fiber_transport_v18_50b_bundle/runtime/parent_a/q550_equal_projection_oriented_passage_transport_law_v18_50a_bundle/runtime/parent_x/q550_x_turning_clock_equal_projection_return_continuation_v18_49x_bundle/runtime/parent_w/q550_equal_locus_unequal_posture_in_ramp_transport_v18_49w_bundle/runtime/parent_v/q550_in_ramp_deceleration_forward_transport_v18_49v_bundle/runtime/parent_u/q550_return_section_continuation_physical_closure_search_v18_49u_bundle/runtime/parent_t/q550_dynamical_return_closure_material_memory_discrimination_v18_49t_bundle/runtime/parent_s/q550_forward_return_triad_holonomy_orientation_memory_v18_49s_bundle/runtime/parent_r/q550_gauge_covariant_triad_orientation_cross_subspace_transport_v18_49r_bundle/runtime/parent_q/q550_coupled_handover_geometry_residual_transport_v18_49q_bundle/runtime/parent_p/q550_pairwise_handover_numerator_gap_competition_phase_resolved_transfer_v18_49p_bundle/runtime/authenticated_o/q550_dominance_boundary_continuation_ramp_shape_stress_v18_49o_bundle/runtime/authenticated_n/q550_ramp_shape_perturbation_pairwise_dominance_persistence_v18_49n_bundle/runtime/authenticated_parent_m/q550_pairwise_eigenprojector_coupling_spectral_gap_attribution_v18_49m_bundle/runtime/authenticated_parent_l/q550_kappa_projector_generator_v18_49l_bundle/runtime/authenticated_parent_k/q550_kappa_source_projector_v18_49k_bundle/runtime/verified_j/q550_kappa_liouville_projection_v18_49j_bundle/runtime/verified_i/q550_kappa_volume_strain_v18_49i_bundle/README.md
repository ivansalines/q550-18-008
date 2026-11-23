# Q550 v18.49i — Volume-Form Invariance & Principal-Strain Transport Audit

**Version:** v18.49i
**Status:** authentic Q550, numerical diagnostic only; NOT an interval proof or a material-invariant claim without a declared metric.

## Scientific objective

Analyze the genuine 10D material linearized flow along six phase-matched Q550 reversals at each of two kappa values. The Q550 state remains 11D; its external command clock is not counted as an independent material variation in the 10D tangent block. There are no new initial orbit seeds; the parent H histories and original solver code are authenticated recursively to the J ancestry.

The physical kinetic embedding was defined and validated in the immutable v18.49h ancestor:

```
H(y) = (Q(y), tau_ref * V(y))
Q = (r1 cos(theta1), r1 sin(theta1), r2 cos(theta2), r2 sin(theta2), sqrt(m_x)*x)
V = dQ/dxi
G(y) = DH(y)^T DH(y)
B(t) = DH(y(t)) * Phi(t) * DH(y(0))^{-1}
C(t) = B(t)^T B(t)
```

Here `tau_ref` defines the declared relative physical scale of positions and velocities and is not uniquely supplied by the dynamics. `Phi` solves the true variational ODE for the material state with the drive clock protocol held fixed.

### Independent volume identity

The physical phase-space metric volume factor is

```
log J_volume = log|det B|
             = log|det Phi| + log|det DH_final| - log|det DH_initial|
             = integral tr(J_material(t)) dt + log|det DH_final/DH_initial|.
```

The integral is calculated independently by adaptive quadrature over the original Jacobian on each genuine 11D solution, rather than by reusing the determinant of `Phi`. The `tau_ref` change is a constant invertible rescaling on the physical embedding and cancels from this volume ratio. A different volume *form* need not yield the same scalar volume factor; absolute coordinate-free volume is NOT claimed.

### Principal strain

Compute eigenvectors and principal stretches of `C` in the common initial kinetic Cartesian frame, ordered from greatest to least. Principal axis signs are arbitrary; compare one-dimensional **lines**, with angle `acos(abs(dot))`. Also compare the leading two-dimensional eigenspace. Report the spectral gap: interpretation of an isolated first eigenvector requires a sufficiently large eigenvalue gap.

Separate the leading strain axis from the direction of the finite return/forward difference, pulled back using `B^-1`; the latter is a **finite-gap diagnostic** and not an exact nonlinear Jacobi vector. A separate comparison with the direction-path tangent and curvature is descriptive, not a proof that strain causes curvature.

## Run on server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_volume_strain_v18_49i_bundle.zip
cd q550_kappa_volume_strain_v18_49i_bundle
bash run_on_server.sh 2>&1 | tee v18_49i_server.log
```

Python 3.13 recommended. Override `Q550_PYTHON` as needed. The parent H sendback is included unchanged in `inputs/v18_49h_original_server_sendback.zip`. The runner first validates 7 standalone unit tests, authenticates the H and all historical ancestors to J, reintegrates genuine trajectories and 10D propagators, checks scientific gates, renders plots and packs a reproducible `sendback.zip` with hashes.

An optional single-case check is available with `python3.13 scripts/run_audit.py --smoke` (this overwrites the numeric results with **smoke-only** data and is not a substitute for the full run).

## New deliverables

- `scripts/run_audit.py` — genuine 11D integration, tangent propagation, metric volume and strain tracking
- `scripts/strain_math.py` — rank/eigen/volume/gauge tools
- `scripts/kinetic_metric.py`, `scripts/frame_math.py`, `scripts/curvature_math.py` — functional copies from authenticated H source, exact historical method preserved
- `scripts/verify_parent.py` — recursive authenticity of H through J
- `scripts/check_outputs.py`, `scripts/plot_results.py`, `scripts/pack_sendback.py`
- `tests/test_strain_math.py` — 7 algebraic unit tests
- `results/report.json`, `results/environment.json`
- `results/liouville_volume_identity.csv` — 12 independent volume checks
- `results/strain_axes_phase_profiles.csv` — 84 complete phase/ramp samples
- `results/all_ten_principal_stretches.csv` — 840 principal stretch values and angular projections
- `results/strain_axis_vs_material_curvature.csv` — 36 direction/path comparisons
- `results/principal_axes_common_frame.npz` — actual full 10D principal vectors and spectra
- 4 figures generated from these CSVs
- `SHA256SUMS_OUTPUT.json`, generated `sendback.zip`

## Interpretation boundaries

1. The volume factor refers to the **tangent material phase-space volume in the chosen kinetic volume form**, not the physical spatial volume nor energy or entropy. Negative log-volume means contraction in that form.
2. The volume factor is independent of constant `tau_ref` scaling in this embedding, not independent of every possible material metric or volume density.
3. Generalized strain eigenvalues and angular comparisons are coordinate-covariant under consistent changes to both tensor and metric; comparing different metrics is a new measurement.
4. The gap between forward and reversed trajectories is finite; its linear inverse pullback is a diagnostic, not a statement of exact nonlinear material invariance.
5. All comparisons are on historical `phaseblind`, branch 0, six reversal ramps and two `kappa_0` choices. Other families and parameter ranges remain unproved.
6. This audit uses no external empirical measurements; it checks the model's own 11D equations and their linearized response.
