# Q550 v18.49k — Source-Zero & Principal-Projector Clock-Transport Audit

## Scope and experimental question

Does the local zero of the clock-matched *difference* between kinetic-volume sources (autonomous minus original kappa) have a stable temporal relationship to the transport of the material principal strain projectors? Is that relationship independent of the volume form or could it arise because both clocks respond to the same ramp control?

This is an **authentic Q550 numerical diagnostic**, not an interval certificate, proof of causal coupling, physical energy transfer, topological closure, or observer-free holonomy.

## Authentication and original computation

`inputs/v18_49j_original_server_sendback.zip` is the *unaltered uploaded original* Q550 v18.49j server archive. SHA-256 is pinned in `inputs/SOURCE_PINS.json`. `scripts/verify_parent.py` checks archive CRC, every SHA-256 file in its manifest, and recursively executes the v18.49j→v18.49i→historical ancestry verification, authenticating the physical 11D reference implementation up to the historical v18.48j. All reference Python files are extracted under `runtime/` during replay; none are hand-waved or replaced by a surrogate.

The script reintegrates **14 original physical 11D histories** (2 forward, 12 return) and **12 material 10×10 variational fundamental matrices**. The Q550 return histories follow `phaseblind` branch 0, ramps `[0.285,0.292,0.296333,0.300,0.305,0.309]`, and `kappa` variants `original` and `autonomous`. The source sampling grid is 121 points on the common return coordinate `q∈[0.35,0.65]`; the return integration coordinate is `t=ramp_xi+q`. All fits and markers use the same registered `q` clock. The historical 61-point source and 10-axis occupation records are independently checked at shared sample points.

## Observable definitions

- Material state `y=(l1,v1,theta1,w1,l2,v2,theta2,w2,z,vz)`; physical configuration and velocity embedding `H(y)=(Q,tau_ref*V)` with `tau_ref=1` gives the kinetic Riemannian metric `G=DH^T DH` (see `scripts/kinetic_metric.py`).
- Tangent fundamental matrix `F(t)` follows the analytic material Jacobian from the authenticated structural jet. The physical fixed-frame deformation matrix is `B(t)=DH(y(t))*F(t)*inv(DH(y(0)))`. Eigenvectors of `B^T B` give ordered principal strain axes, with principal spectral gaps tracked.
- `P_i(q)=a_i(q) a_i(q)^T` is a **sign-independent rank-one eigenprojector**. It is analyzed in the *declared Euclidean initial kinetic embedding*, not under arbitrary changes of kinetic scale. Its angular speed is `omega_i(q)=||dP_i/dq||_F/sqrt(2)`. A combined spectral diagnostic uses `sqrt(sum_i omega_i^2)`.
- For each speed, the **half-turn marker** is the time `q_1/2` where the accumulated integral of this **nonnegative angular speed** reaches half its integral over `[0.35,0.65]`. It is not an instantaneous turning point or a closed loop.
- The physical-volume source in solver coordinates is `s_0(y)=tr(J_material)+grad(log|det DH|)·f`, with the kinetic density exactly defined in `scripts/source_math.py`.
- For the counterfactual form `dV_alpha=exp(alpha*(l1-l2))*dV_kinetic`, the local source is `s_alpha=s_0+alpha*(f_l1-f_l2)`. The root is obtained from the **difference** `Delta s_alpha=s_alpha,autonomous-s_alpha,original`. Roots are accepted only if the discrete samples bracket a sign change, refined by shape-preserving PCHIP + Brent; missing/extra roots are reported rather than fabricated.
- Clock lag is `q_1/2 - q_root`. Correlation and its exhaustive 6! ramp-permutation control are **descriptive only**; both markers have an external common control parameter (ramp), and there are only six ramps.

## Result highlights from the local preflight replay

For the **ramp=0.300**, the kinetic-volume (`alpha=0`) source root is `q≈0.388745`. The original-κ half-turn clocks are `q≈0.472652` (axis 10), `q≈0.505929` (axis 1), `q≈0.540947` (axis 8), and `q≈0.543249` (combined principal projectors). There is **no coincident fixed-phase event**.

As ramp grows from 0.285 to 0.309 the source root moves from ≈0.402169 to ≈0.380774 while the combined projector half-turn moves from ≈0.532892 to ≈0.549135 (original κ). The raw Pearson correlation for these two clocks is ≈−0.99992, but this is **confounded by their common ramp dependence** and does not certify causal coupling.

Counterfactual volume-form sensitivity is decisive: at `ramp=0.300`, `alpha=-0.001` moves the source root to `q≈0.474299`; `alpha=+0.001` removes all roots in the measured window. The projectors do not change in this counterfactual because the kinetic metric and the trajectories are held fixed. Therefore a coincidence between these markers would **not** be an invariant of arbitrary volume-form choice.

The source of kappa in the analytic material Jacobian has zero explicit trace. Kappa can still change the source indirectly via the physical trajectory and the kinetic density.

Max errors in the full local replay: historical forward regression ≈3.43e-13; original v18.49j source ≈4.27e-14; projector occupation vs parent ≈6.00e-15; projector-occupation derivative balance ≈1.60e-4 per q (finite-difference); 121 vs 61 grid half-turn difference ≈5.94e-5 q; minimum sampled relative principal spectral gap ≈0.0432. These are numerical checks, not interval certificates.

## Run on the server

```bash
cd /root/elab1/hysteresis
unzip Q550_v18_49k_COMPLETO.zip
cd q550_kappa_source_projector_v18_49k_bundle
bash run_on_server.sh 2>&1 | tee v18_49k_server.log
```

Python 3.13 is selected by default. `Q550_PYTHON=/path/to/python` overrides it. Required imports: numpy, scipy, matplotlib (exact runtime versions are recorded in `results/environment.json`). Script/document comments and contents use English.

The runner checks 8 independent unit tests, verifies all upstream hashes, runs the authentic dynamical integration, checks scientific numerical gates, plots the original numeric data, then packs `sendback.zip` with script sources, inputs, outputs, manifests and SHA-256 hashes. No runtime extraction cache is included in the ZIP; it regenerates from immutable inputs.

## Outputs

- `results/report.json`: scientific gates, source roots, settings, lineage.
- `results/physical_sources_clockmatched.csv`: physical clock and individual solver/metric volume source terms.
- `results/principal_projector_transport.csv`: 10D projector speeds and derivative decomposition for axes 1,3,8,10.
- `results/source_zero_counterfactual_roots.csv`: all alpha/ramp root states.
- `results/principal_projector_halfturn_markers.csv`: individual and aggregate half-turn markers.
- `results/clock_lag_and_volume_form_controls.csv`: experimental event lags.
- `results/ramp_permutation_controls.csv`: raw correlation plus exact descriptive permutation score (not causal).
- Four PNG figures generated directly by `scripts/plot_results.py`.
- `scripts/run_audit.py`, `scripts/clock_math.py`, and the original inherited reconstructed/exact source modules.
- `inputs/` pins the original J sendback; ancestry authenticates earlier original Python scripts and arrays.

## Scientific interpretation

The local source-zero and principal-projector clocks drift systematically but **are not synchronized**. The source root is demonstrably sensitive to the chosen volume form. A very strong raw correlation across six ramps can be induced by opposing monotonic responses to the ramp. Any stronger physical statement needs independent protocols and a genuinely coordinate-covariant comparison with a declared material connection and volume form. No additional conserved quantity is certified here.
