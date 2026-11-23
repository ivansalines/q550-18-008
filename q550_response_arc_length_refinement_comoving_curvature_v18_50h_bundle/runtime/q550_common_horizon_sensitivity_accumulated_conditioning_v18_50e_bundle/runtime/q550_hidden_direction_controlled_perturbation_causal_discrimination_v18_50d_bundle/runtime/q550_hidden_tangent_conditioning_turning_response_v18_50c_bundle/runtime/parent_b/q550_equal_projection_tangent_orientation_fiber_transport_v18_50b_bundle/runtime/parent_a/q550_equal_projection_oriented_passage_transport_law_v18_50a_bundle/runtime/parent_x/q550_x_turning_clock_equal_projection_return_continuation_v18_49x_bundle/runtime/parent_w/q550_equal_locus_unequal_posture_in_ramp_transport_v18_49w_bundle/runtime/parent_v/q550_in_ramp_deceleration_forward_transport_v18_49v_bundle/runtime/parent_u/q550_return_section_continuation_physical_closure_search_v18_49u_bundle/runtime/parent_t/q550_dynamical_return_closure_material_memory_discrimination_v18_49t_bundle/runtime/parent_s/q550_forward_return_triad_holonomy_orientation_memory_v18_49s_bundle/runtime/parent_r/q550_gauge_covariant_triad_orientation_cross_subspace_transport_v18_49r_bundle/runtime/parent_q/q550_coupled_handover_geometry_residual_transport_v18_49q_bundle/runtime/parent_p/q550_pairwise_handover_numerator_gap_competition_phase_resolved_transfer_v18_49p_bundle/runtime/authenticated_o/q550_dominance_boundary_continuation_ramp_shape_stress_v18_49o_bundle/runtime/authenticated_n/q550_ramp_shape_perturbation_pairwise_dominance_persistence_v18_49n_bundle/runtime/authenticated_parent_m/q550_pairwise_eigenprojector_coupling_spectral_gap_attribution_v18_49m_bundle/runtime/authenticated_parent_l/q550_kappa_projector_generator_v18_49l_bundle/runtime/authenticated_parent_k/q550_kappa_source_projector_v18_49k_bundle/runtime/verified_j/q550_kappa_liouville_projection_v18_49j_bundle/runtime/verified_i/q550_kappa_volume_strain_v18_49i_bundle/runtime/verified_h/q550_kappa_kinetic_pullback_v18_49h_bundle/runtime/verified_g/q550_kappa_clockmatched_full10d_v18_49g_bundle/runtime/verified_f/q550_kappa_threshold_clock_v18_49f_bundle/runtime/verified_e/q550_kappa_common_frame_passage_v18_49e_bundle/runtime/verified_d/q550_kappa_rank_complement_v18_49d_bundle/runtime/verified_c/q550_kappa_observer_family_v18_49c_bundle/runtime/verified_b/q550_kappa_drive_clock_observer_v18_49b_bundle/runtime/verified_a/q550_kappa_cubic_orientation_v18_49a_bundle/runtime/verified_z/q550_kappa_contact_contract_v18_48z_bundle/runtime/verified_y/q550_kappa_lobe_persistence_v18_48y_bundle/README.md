# Q550 v18.48y — Contact-Lobe Threshold Persistence & Barrier-Curvature Audit

**Status:** authentic 11D floating-point numerical audit, not an interval proof of topology, dynamical merger, constitutive hysteresis law, material torsion, or energy/entropy theorem.

## Purpose

Following the authenticated v18.48x user-server audit, study the **family of strict sublevel sets**

`L(r,epsilon) = { q in [0.10,0.90] : d3(q;r) < epsilon }`,

where `d3` is the equal-external-phase distance of the original 11D forward and smooth-reversed return trajectory projected to `(logrho1,logrho2,x)`. The chosen smoothstep drive and fully inverted material velocities at the turning point are **unchanged** from v18.48x. The `q=0` imposed turning contact is not included.

The central barrier `B(r)` is the *interior local maximum* of `d3` between the two observed contact minima. This allows us to describe a **threshold-dependent merger curve** `epsilon=B(r)`. It is an observable of the particular chosen projection, q-window, and protocol, not a universal critical curve of matter.

## Genuine input provenance and source genealogy

- `inputs/v18_48x_original_server_sendback.zip` is the **exact** v18.48x user-server upload. The input is SHA-256 pinned (in `inputs/SOURCE_PINS.json`). It is never modified.
- `scripts/verify_parent.py` authenticates every entry of the historical X archive and recursively invokes the X verifier to authenticate the full chain of exact original server packages **x → w → v → u → t → s → r → q → p → o → j**.
- `reference/physical_math.py`, `reference/parent_ramp_math.py`, `reference/original_drive_math.py`, `reference/transversality_math.py` and `reference/parent_lobe_math.py` are byte-exact copies of authenticated historical mathematics; the original physical RHS, parameter definitions and mechanical balance are NOT refitted or changed.
- The original 328 11D history states and both kappa values are recovered through the verified genealogy. No manufactured material seed is used.

## Numerical protocol

Only the two physically integrated **phaseblind branch 0** histories (original κ₀=1/6 and independently proposed autonomous κ₀) are freshly integrated, because this is the family in which the interior two-lobe bridge was identified. All eight original history paths and 328 states are authenticated, but the six nonfocus paths are not rerun in v18.48y. Do not infer an identical merger in those paths.

23 ramp durations (ξ units) per kappa:

`0.280, 0.285, 0.290, 0.292, 0.294, 0.295, 0.296, 0.29625, 0.296333, 0.2965, 0.29653, 0.297, 0.298, 0.299, 0.300, 0.301, 0.302, 0.303, 0.304, 0.305, 0.307, 0.309, 0.312`

Two original forward DOP853 integrations + 46 fresh counterflow return integrations = **48 genuine 11D integrations**. Relative tolerance `3e-12`, absolute `3e-13`, max solver step `0.025`. All 46 equal-phase profiles are sampled at 1601 q points in `[0.10,0.90]`. Threshold roots are refined by `brentq` against continuous dense-IVP evaluations, not by drawing curves. The selected strict contact levels are `0.005,0.008,0.010,0.012,0.015`.

The barrier phase is optimized against dense-IVP `d3(q;r)` over `q ∈ [.465,.505]`. Curvatures `d²(d3)/dq²` use symmetric differences at steps `[.002,.001,.0005,.00025]` and a Richardson check. These are **finite-difference diagnostics**, not rigorous differentiability/roundoff bounds.

For seven critical thresholds `epsilon∈{.004,.006,.008,.010,.012,.014,.016}`, the barrier is bracketed between **two genuinely integrated ramp durations** and a **linear secant estimate** of the crossing is provided. The secant is not a newly integrated critical orbit and the brackets are *numerical sampling brackets, not interval enclosures*. All q-domain boundary clipping flags remain explicit.

Each barrier evaluation also records full wrapped 11D separation and model mechanical-energy difference. The latter is not drive work alone; balance is verified with dissipative and active terms in the original physical audit.

## Main numerical findings (original κ₀; secant estimates)

| ε | Critical ramp ξ (interpolated) |
|---|---|
| 0.016 | 0.283384 |
| 0.014 | 0.287758 |
| 0.012 | 0.292080 |
| 0.010 | 0.296333 |
| 0.008 | 0.300530 |
| 0.006 | 0.304679 |
| 0.004 | 0.308793 |

The autonomous κ₀ critical curve is systematically shifted approximately `+0.00019…+0.00020 ξ` over the tested threshold levels; the source-based X transition at ε=0.010 is independently reproduced. Throughout this 23-ramp region, central barrier curvature is negative (approximately `−5.49 ... −5.34`), not flat, and the full wrapped 11D state separation remains above `1.88`. This supports an observed **smoothly changing level-set merger** for the chosen projection, without full-state recurrence.

**Numerical gates:** 48 true IVPs; parent X profile regression ≤`3.6e-15`; maximum 11D original-state replay error and original mechanical-ledger residual in `results/report.json`; all five contact thresholds yield interior components without clipping; 9 mathematical tests and generated-output checks.

## Run on server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_lobe_persistence_v18_48y_bundle.zip
cd q550_kappa_lobe_persistence_v18_48y_bundle
bash run_on_server.sh 2>&1 | tee v18_48y_server.log
```

Python 3.13 is default. Override with `Q550_PYTHON` if necessary. No symlinks, orbit caches or hand-selected runtime files are necessary. The extraction root is exactly `q550_kappa_lobe_persistence_v18_48y_bundle/`.

The command authenticates historical files, executes tests, generates the complete 11D replay, verifies scientific gates, creates four plots and packages `sendback.zip` with exact script sources, source pins, historical original ZIP, CSVs, figures and a complete SHA-256 manifest.

## Files generated

- `results/barrier_height_curvature.csv`: true dense-IVP barrier phase, height and curvature at four steps, two contact minima, wrapped full-11D and energy separation.
- `results/critical_threshold_curve.csv`: seven sampled ramp brackets per kappa and secant interpolated critical ramp.
- `results/threshold_persistence_components.csv`: connected components of `{d3<epsilon}` at five levels; explicit boundary clipping flags.
- `results/dense_contact_profiles.csv`: all 46 × 1601 true equal-phase physical shape gaps.
- `results/barrier_ramp_sensitivity.csv`: finite-secant barrier slope `ΔB/Δr`.
- `results/original_x_profile_regression.csv`, `results/report.json`, `results/runtime_environment.json`, four real numerical PNGs.
- `sendback.zip` and `SHA256SUMS_OUTPUT.json` for executable provenance.

## Scientific boundary

The experiment samples one ramp interval and one branch, with finite q resolution. We have not excluded all possible tiny subgrid components, demonstrated structural stability under arbitrary model perturbations, certified a persistence diagram in interval arithmetic, nor proved exact topology of the original dynamics. A smooth threshold-level bridge should never be promoted to material fusion, full-state recurrence, dissipative work law, or an intrinsic time constant.

## Independent local barrier-to-gap consistency check

At a local maximum with barrier height `B` and negative phase curvature `C`, Taylor expansion gives

`d3(q) ≈ B - |C|*(q-q_barrier)^2/2`.

For `epsilon < B` sufficiently near the barrier, the two actual sublevel contact intervals are separated by the predicted excluded gap

`G_pred = 2 * sqrt(2*(B-epsilon)/|C|)`.

The independently measured gap uses dense-IVP threshold roots, not curve pixels. On 12 data pairs within `0 < B-epsilon < 0.0004`, the maximum relative discrepancy is **0.0344%** (the exact value is in `quadratic_gap_scaling_report.json`). This is a local geometric Taylor check, not a universal critical exponent proof or a dynamical fusion. `scripts/check_quadratic_gap.py` regenerates the check CSV and report; `scripts/plot_results.py` draws `quadratic_barrier_gap_prediction.png`.
