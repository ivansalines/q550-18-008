# Q550 v18.49t — Dynamical Return Closure & Material-Memory Discrimination Audit

**Validated local full execution: `DYNAMIC_RETURN_NOT_CLOSED_AT_TESTED_SECTIONS` (5 cases, 15 nearest-geometry sections, 0 strict closures). This is not a material-memory certificate.**

This audit corrects the scope limitation of v18.49s. v18.49s had two distinct physically simulated return histories but mathematically reverse-traversed one of them and applied canonical endpoint connectors. In v18.49t the full 11D **forward** trajectory is reintegrated under the original drive, the five velocities are explicitly reversed at the turning point (an externally imposed intervention), and the full 11D **return** trajectory is integrated with the original signed and ramped drive. No geometric inverse path is substituted for that return, and no connector is used to force a physical loop closure.

For three forward anchor sections, find the closest configuration on the *physically integrated return leg*. Configurations use (log rho1, theta1, log rho2, theta2, logit x, Theta) with wrapped angles. The return state is not declared identical simply because its configuration is closest. Report geometric distance, reversed-velocity gap, actual elapsed time, mechanical-energy difference, and explicit integrated drive/damping/source terms.

To compare the triad in the same initial kinetic material reference, compose the authentic 10D tangent propagators `F_return(t) · R_flip · F_forward(1)` and evaluate projectors using the same initial embedding `J_initial`. This is a *different observable* from v18.49s two-path Kato SO(3) holonomy. It is **not** an absolute oriented triad after an exactly closed physical orbit.

Strict closure requires all four predefined tolerances to pass simultaneously: configuration, reverse velocity, energy and common-frame spectral projector. If none close, output `DYNAMIC_RETURN_NOT_CLOSED_AT_TESTED_SECTIONS`, **not** physical-memory evidence. If the spectral gap cannot be resolved, mark the failure and never silently impute a projector.

## Run on server

```bash
cd /root/elab1/hysteresis
unzip q550_dynamical_return_closure_material_memory_discrimination_v18_49t_bundle.zip
cd q550_dynamical_return_closure_material_memory_discrimination_v18_49t_bundle
bash run_on_server.sh --smoke 2>&1 | tee v18_49t_smoke.log
bash run_on_server.sh 2>&1 | tee v18_49t_full.log
```

Optional: `--focus`, `--anchor-times .55 .65 .75`, `--match-samples 151`, `--config-tolerance`, `--velocity-tolerance`, `--energy-tolerance`, `--projector-tolerance`, `--rtol`, `--frame-rtol`. Default includes five duration/κ₀ cases. The scripts, parent pinned v18.49s server sendback, lineage, generated CSVs/plots/report, environment, and checksum manifest are packaged with identical descriptive ZIP and root directory names.

## Scientific decision rules

1. **Same physical state** is NOT implied by a numerical nearest configuration section.
2. A rotation or nonzero projector difference in a nonclosed loop is NOT a material holonomy.
3. External velocity flipping constitutes an imposed protocol, not a spontaneous time reversal.
4. The original mechanical energy is not a conserved total energy; compare its full work/dissipation ledger.
5. Numerical eigenspaces require a declared gap; an unresolved gap blocks that section's orientation diagnostic.
6. Varying the matching metric and initial sections is required before claiming a robust physical closure.
