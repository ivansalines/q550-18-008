# Q550 v18.49b — Drive-Clock Covariant Skew & Observer-Transport Audit

## What is genuinely new

This bundle integrates the exact historical 11D material equations from the authenticated original server genealogy, plus a **new 10D material variational and cotangent adjoint** along twelve freshly driven counterflow returns. Two historical v18.48j observer covectors are used only as seeds at the genuine velocity-reversal turning point; the newly driven cotangent histories are NOT claimed to be present in v18.48j.

For a prescribed drive clock Θ(t), write the material state y_m=y[:10] and F_m(y_m,Θ(t)). The linearization of the material state with fixed external control has

`v' = J_m(t) v`, `g' = -J_m(t)^T g`, `J_m = ∂F_m/∂y_m|Θ(t)`.

Consequently `d(g.T @ v)/dt=0` exactly in real arithmetic for the **linearized** equations. This is not energy conservation or a finite-offset invariant. The analytic J is copied byte-for-byte from the authenticated historical v18.48j source. Independently checked Jacobian columns derive from fresh RHS finite differences.

We evaluate two differently seeded transported covectors against finite 10D return-minus-forward state differences at each of the 48 *physical* continuous-IVP root pairs established by v18.48z and reauthenticated by v18.49a; we also include their barrier centers (288 total observer/root records, 96 barrier records but **only 12 distinct barrier physical points**, repeated for 4 threshold levels and two observer channels). Clock angle, root locations, geometry and energy remain the same when the observer changes; signed projection is a reading, not a material observable invariant by itself.

The 11D state retains prescribed Θ as the eleventh coordinate. The tangent/adjoint IVP transports only **10 material variables**; do not promote this result to an 11D joint drive-control cotangent theorem.

## To run on the server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_drive_clock_observer_v18_49b_bundle.zip
cd q550_kappa_drive_clock_observer_v18_49b_bundle
bash run_on_server.sh 2>&1 | tee v18_49b_server.log
```

To preview one kappa and one ramp, `python3.13 scripts/run_audit.py --smoke` (smoke results will overwrite full results in the current directory; rerun full command afterwards).

The runner verifies the nested A→Z→Y→X→W→V→U→...→J ancestry, runs the 5 independent unit tests, replays all 14 physical 11D integrations (two physical forward paths and twelve smooth counterflows), integrates 12 material cotangent histories, regenerates CSV/PNG results and `sendback.zip`. The complete parent A original server ZIP is carried unchanged in `inputs/`.

## Files

- `scripts/run_audit.py`: actual calculation, explicit CLI tolerances.
- `scripts/observer_math.py`: transported observer/tangent equations and shape gradient.
- `scripts/verify_parent.py`: strict nested archive member and SHA validation.
- `reference/`: byte-exact historical math sources, original 11D integrator and J analytic derivatives.
- `results/*.csv`, `results/report.json`, `results/*.png`: computed outcomes.
- `SCIENTIFIC_DECISION_RULES.md`: interpretation gates.
- `inputs/SOURCE_PINS.json` and `SHA256SUMS_OUTPUT.json`: genealogy checksums.

## Limits

Floating-point experiment, not interval verified. Results establish consistency of transported-observer projections for these twelve return trajectories, not a universal chiral material law or intrinsic material delay. The historical observer covectors and chart normalization depend on the selected observation convention.
