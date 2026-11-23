# Q550 v18.48u — Smooth Drive Reversal & Phase–Energy Path Dependence Audit

**Status:** full original-support numerical preflight completed for eight authenticated physical Q550 11D paths. Documentation and Python comments in English. The original server-generated **v18.48t** sendback is included **byte-for-byte** and its authentic ancestry **s/r/q/p/o/j** is recursively SHA-256 verified before any calculation.

## Scientific question

Does a prescribed **smooth transition of the external rotating drive** (brake → zero angular velocity → reverse) change the phase-matched return geometry, state and signed model mechanical energy, compared with the abrupt constant-rate reversal at the same final external phase?

This is a **drive-history counterfactual** on the historically authenticated Q550 equations, not a proof of autonomous mechanical delay, entropy production, a universal hysteresis law or physical reversibility violation.

## Physical computation

- State: 11 physical variables, unchanged original-support RHS; mechanical energy and the four signed mechanical power channels are copied byte-identically from v18.48t.
- Eight historical seed trajectories (two historical observer families × two physical seed branches × original/autonomous kappa), 41 sections on xi ∈ [3.5,4.5]. Regenerated with genuine DOP853 integration (rtol=3e-12, atol=3e-13, max_step=.025).
- The **external clock coordinate** `Theta` is integrated *analytically* from the imposed clock-sign function. Its ten material coordinates and four work channels are integrated numerically from the original RHS. Analytic clock evaluation avoids numerical drift in the prescribed phase; it is **not** a separate approximate physical model.
- Six drive histories × three velocity preparation levels (`alpha=[0,.75,1]`) × 8 seeds = 144 new reversed material IVPs, plus 8 original-forward trajectory integrations: **152 genuine 11D-system solutions**.
- No artificial coordinates or synthetic orbital trajectories; all controls are declared user-imposed protocols.

## The six controlled drive histories

The instantaneous reference is `clock_sign = -1` for all xi after turn. Every smooth profile starts at the historical `+1` and reaches `-1` via zero; its **signed integral over the prelude is zero**. Hence all protocols return to `q=0` at the end of their prelude and subsequently traverse the same net negative phase excursion `q>0` at identical final drive speed `-1`.

| name | clock-sign history | prelude xi | zero-drive dwell xi | total simulated return xi |
|---|---|---:|---:|---:|
| instant | immediate switch +1 to -1 | 0 | 0 | 1.00 |
| smooth_short | cubic smoothstep +1→-1 | 0.15 | 0 | 1.15 |
| smooth_medium | cubic smoothstep +1→-1 | 0.35 | 0 | 1.35 |
| smooth_long | cubic smoothstep +1→-1 | 0.65 | 0 | 1.65 |
| smoother_medium | quintic smootherstep +1→-1 | 0.35 | 0 | 1.35 |
| stop_dwell | cubic +1→0, hold 0, cubic 0→-1 | 0.50 | 0.15 | 1.50 |

The external angular velocity in the support xi clock is `omega * clock_sign(xi)` with `omega = 2*pi*slope ≈ 0.84436`. In the cubic and quintic profiles, the switch crosses exactly through zero at half of the prelude. For the stop/dwell experiment, each ramp half-width is `0.175 xi` and the drive stops for `0.15 xi`.

The shared **unwrapped positive return phase excursion** is `q=-∫clock_sign dt`. During an initial smooth ramp, q can become temporarily *negative*, as the drive initially keeps moving forward; the contact search deliberately uses only the unique **post-reversal** branch `q>0`. All comparisons use the exact historical 81-point shared phase window q ∈ [0.312500001, 0.719999999] from v18.48t:

```
return_elapsed_time = prelude_duration + q
forward_elapsed_time = 1 - q
Theta_return = Theta_forward = Theta_turn - omega*q
```

Thus return elapsed times differ by the prelude length. Matching q explicitly prevents treating these as equal elapsed-time measurements or confusing a longer programmed duration with altered earlier dynamics.

## Material preparation and energy identity

At turn, the five material velocity coordinates are scaled by `1 - 2*alpha`, leaving all positions, internal phases and external `Theta` unchanged:

- alpha=0: velocities retained;
- alpha=.75: velocities multiplied by -0.5 (externally imposed preparation kinetic-energy jump);
- alpha=1: full velocity inversion, kinetic energy unchanged instantaneously.

The initial energy change is recorded **separately**. The phase-matched energy gap is checked against original forward work, preparation jump and return work, each broken into external-drive power, radial damping, x damping and active x forcing.

## Full numerical preflight (8 historical paths)

- **152** physical-system solutions, **144** phase-matched optimized contact comparisons, **11,664** shared-phase profile rows.
- **11/11** independent math regression tests passed.
- Original-forward replay maximum 11D historical error: ~1.65×10^-11.
- Max discrepancy of abrupt control against original v18.48t historical common-phase profiles: ~1.54×10^-12.
- Max mechanical balance residual, normalized: ~1.75×10^-10; max equal-phase absolute balance-gap residual ~1.75×10^-10. This is **floating-point residual**, not an interval-bound proof. External clock phase equality is analytic to working floating-point precision.
- At alpha=1, the median of optimized 3-coordinate gaps (eight seeds each): instant ~0.014078, smooth_short ~0.000743, smooth_medium ~0.011765, smoother_medium ~0.012489, smooth_long ~0.142174 and stop_dwell ~0.129661.
- Across all 144 contacts the minimum optimized 3D gap is ~0.000323784 (phasecov branch1, autonomous kappa, smoother_medium, alpha=1); the minimum full wrapped-11D gap in the sample is still ~1.161. A near-contact in `(log rho1, log rho2, x)` is not a full 11D reunion.
- In 120/144 best contacts the instantaneous forward and return **drive powers** have opposite sign. There is no claim of entropy production: this is only a **signed term in a declared model-mechanical energy balance**. For alpha=0, 4/8 by protocol have opposite power signs; for alpha=.75 and 1, 8/8 by protocol.
- alpha=.75 carries a median **preparation** energy jump of approximately -0.272739, kept separate from the subsequent drive work.

**Decision:** Changing *how the rotating command is reversed* changes the material path even at matched external phase and final command speed. The dependence is not monotonic in ramp duration. This is a measured protocol-dependent physical-model response, not a unique intrinsic delay constant.

## Reproduce on Linux

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_smooth_reversal_v18_48u_bundle.zip
cd q550_kappa_smooth_reversal_v18_48u_bundle
bash run_on_server.sh 2>&1 | tee v18_48u_server.log
```

Override interpreter with `Q550_PYTHON=python3.13` if needed. The runner verifies authentic parent source SHA recursively, executes unit tests, recalculates all original-material trajectories, enforces output assertions, plots authentic measurements and produces `SHA256SUMS_OUTPUT.json` plus `sendback.zip`.

For a cheap, *explicitly partial* local test: `python3.13 scripts/run_audit.py --limit-groups 1`. Never cite a partial run as the completed eight-path audit.

## Contents and genealogy

- `inputs/v18_48t_original_server_sendback.zip` and `inputs/SOURCE_PINS.json`: immutable authentic provenance.
- `reference/physical_math.py`, `reference/transversality_math.py`: unchanged original-protocol material diagnostics, byte-compared with the authenticated parent.
- `scripts/drive_math.py`: analytic brake/stop/reverse control functions with exact phase primitives.
- `scripts/verify_parent.py`, `scripts/run_audit.py`, `scripts/check_outputs.py`, `scripts/plot_results.py`, `scripts/pack_sendback.py`: runnable genealogy and decision gates.
- `tests/test_drive_math.py`: 11 independent mathematical control tests.
- `results/phase_locked_contacts.csv`, `results/common_phase_profiles.csv`, `results/historical_regression.csv`, `results/report.json` and genuinely regenerated figures.
- `SCIENTIFIC_DECISION_RULES.md`: interpretative and failure boundaries.

No historical source ZIP is modified or repackaged internally; `runtime/verified_parent` is generated on demand, keeping packaged hierarchy predictable.
