# Q550 v18.48v — Smooth-Reversal Contact Window & Phase–Energy History Audit

**Status:** completed eight-path original 11D floating-point preflight; a fresh server execution is recommended for the independent sendback. All code comments and documentation are in English.

## Purpose

Follow v18.48u by asking whether the favorable short braking protocol defines a single global contact optimum, or several **branch-dependent favorable windows**. The audit has **two linked views**:

1. **V-1 / Contact-window scan:** refine the cubic smoothstep ramp from 0 to 0.65 xi on 17 declared values, detect geometry-only contact minima on a common return-phase interval and estimate subthreshold phase widths. The contact minimum and its phase are allowed to move with the ramp.
2. **V-2 / Energy-history separation:** at **fixed return phases q = 0.35, 0.50, 0.65**, compare 3D shape, wrapped 11D state, model mechanical energy and decomposed accumulated work. This avoids evaluating different protocol histories only at their individually optimized contact phases.

Both views operate on the **same eight authenticated original 11D Q550 trajectories**, without any synthetic orbit or changed physical constitutive RHS. The user-imposed external command changes; its exact unwrapped phase is evaluated analytically. The ten other dynamical coordinates and four work channels are integrated with DOP853.

## Control protocol

- Original forward physical xi interval: `[3.5, 4.5]`, 41 historical source states for each of eight seeds (`phaseblind`/`phasecov` × 2 physical branches × 2 kappa variants).
- At the turn, material velocities are prescribed as `v_return(0) = (1 - 2 alpha) v_forward(1)`.
- Full ramp grid for **alpha=1**: `0, .04, .07, .09, .11, .125, .14, .15, .16, .175, .19, .21, .24, .28, .35, .50, .65` xi.
- Controls **alpha=0, .75**: ramp grid `0, .15, .35, .65` xi for continuity and parent-v18.48u regression.
- During a ramp of duration `r > 0`, the imposed signed drive speed is `c(t) = 1 - 2[3(t/r)^2 - 2(t/r)^3]`, from `+1` through zero to `-1`. Its signed phase integral across the ramp is zero. After the ramp it is `-1`. The `r=0` control switches instantly to `-1`.
- On the unique post-reversal return branch, the shared phase is `q = t - r`, with `q in [0.312500001, 0.719999999]`. Match the original forward history at `s=1-q`. These are **equal external phase**, not equal elapsed times.
- As ramp length changes, total elapsed time to the same matched phase **also changes**. This is intentional drive-history dependence; it does not independently isolate exposure time or define an intrinsic material response time.
- Physical integration tolerances: `rtol=3e-12`, `atol=3e-13`, `max_step=.025` xi. Continuous solution for the material state, analytic phase for the externally controlled coordinate.

## Authentic server-sendback numerical preflight

- **208** genuine 11D-system integrations: `8 forward replays + 8 × (17 alpha=1 ramps + 4 alpha=.75 controls + 4 alpha=0 controls)`.
- **200** optimized equal-phase near-contact comparisons and **600** independent fixed-phase energy-history comparisons.
- **10/10** independent mathematical unit tests passed. Historical original forward maximum 11D error below `2e-11`; preserved v18.48u control profiles reproduce within `4.47e-15` absolute.
- Largest normalized energy-ledger residual `4.88e-10`, below declared gate `1e-8`; equal-phase work identity also gated to absolute `1e-7`. These are numerical checks, not interval enclosures.
- Smallest observed 3D near-contact across all ramps and seeds: **~0.000216828**. Smallest full wrapped-11D gap anywhere in the 200 contacts: **~1.153218**. These may come from *different* protocol points; do not treat them as the same event.
- Under alpha=1 the **scanned, per-seed best ramp** for the original kappa is:

| Family | Branch | Best sampled ramp xi | Shape gap (3D) | Full-state gap at that contact |
|---|---:|---:|---:|---:|
| phaseblind | 0 | 0.28 | 0.000357050 | 1.617033 |
| phaseblind | 1 | 0.07 | 0.000216918 | 3.901914 |
| phasecov | 0 | 0.04 | 0.00146376 | 1.920007 |
| phasecov | 1 | 0.35 | 0.000331517 | 1.815985 |

The autonomous-kappa branches select the same four grid durations in this finite sample, with slightly different distances. **This is not a globally optimized or certified unique duration.**

Across eight seeds, the **median** optimized 3D gap at ramp 0.11 xi is `~0.000501`, vs `~0.000743` at 0.15 xi and `~0.014078` for the abrupt reversal. The median full-state gap does **not** minimize at the same ramp. No choice of these near-contacts reaches 11D recurrence.

At fixed phase `q=0.50`, alpha=1, the median signed model-energy gap (return minus forward) is approximately `-0.005011` for the abrupt command, `-0.006157` for ramp .15 and `-0.006830` for ramp .35. The corresponding median cumulative return-drive-work channel changes from `+0.000941` to approximately `+0.000022` and `-0.001215`. These values show **control-path-dependent energy accounting** at the same external phase; model work is not entropy production.

## CLI

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_contact_window_v18_48v_bundle.zip
cd q550_kappa_contact_window_v18_48v_bundle
bash run_on_server.sh 2>&1 | tee v18_48v_server.log
```

The command executes the 10 tests, SHA-256 verifies the unchanged **original v18.48u server sendback**, recursively authenticates its `t → s → r → q → p → o → j` ancestry, integrates and audits all eight paths, verifies numerical gates, draws plots and packs `sendback.zip` with sources, inputs, results and a fresh SHA-256 manifest.

Optional cheap **partial** smoke run, never to be represented as a full audit:

```bash
python3.13 scripts/run_audit.py --limit-groups 1
python3.13 scripts/check_outputs.py
```

Then rerun the full `bash run_on_server.sh` to restore full output counts.

## Files

- `inputs/v18_48u_original_server_sendback.zip`: byte-exact original **user server** artifact, not edited.
- `inputs/SOURCE_PINS.json`: immutable parent archive hash.
- `reference/physical_math.py`, `reference/transversality_math.py`: original inherited source bytes.
- `reference/original_drive_math.py`: original inherited cubic control source bytes for independent comparison.
- `scripts/verify_parent.py`: recursive source authenticity and archive safety; writes only `runtime/` outputs.
- `scripts/ramp_math.py`: independent analytic cubic control and scalar phase-width root bracketing.
- `scripts/run_audit.py`: actual 11D integration and numerical contact/energy audit.
- `scripts/check_outputs.py`, `plot_results.py`, `pack_sendback.py`: acceptance gates, genuine data figures and reproducible sendback archive.
- `results/fine_ramp_contacts.csv`: 200 phase-refined results with individual work channels.
- `results/fixed_phase_energy_history.csv`: 600 matched-q comparisons; `results/per_path_window_optima.csv` and `results/ramp_window_summary.csv`.
- `results/historical_replay.csv`, `results/report.json`, and three PNGs.
- `tests/test_ramp_math.py` (10 tests), `SCIENTIFIC_DECISION_RULES.md`, `SHA256SUMS_OUTPUT.json`.

## Limitations

This is a **numerical counterfactual of an externally imposed drive**, not a proof of a universal anti-flow or intrinsic hysteresis law. All distances depend on the chosen coordinates and normalizations; `3D` means only `(log rho1, log rho2, x)`. In particular, a tiny 3D gap does not entail a small 11D gap.

Each optimum is the minimum on a **finite scanned set of ramp durations**. The equal-phase contact search uses the historical 81-point phase grid with local bounded minimization. Phase widths are refined by root-bracketing at the sampled phase intervals and the identified minimum, but can miss extra sub-grid components; **they are diagnostic**, not rigorous global width certificates. The original energy identity is checked in working double precision; no universal thermodynamic inference is justified.
