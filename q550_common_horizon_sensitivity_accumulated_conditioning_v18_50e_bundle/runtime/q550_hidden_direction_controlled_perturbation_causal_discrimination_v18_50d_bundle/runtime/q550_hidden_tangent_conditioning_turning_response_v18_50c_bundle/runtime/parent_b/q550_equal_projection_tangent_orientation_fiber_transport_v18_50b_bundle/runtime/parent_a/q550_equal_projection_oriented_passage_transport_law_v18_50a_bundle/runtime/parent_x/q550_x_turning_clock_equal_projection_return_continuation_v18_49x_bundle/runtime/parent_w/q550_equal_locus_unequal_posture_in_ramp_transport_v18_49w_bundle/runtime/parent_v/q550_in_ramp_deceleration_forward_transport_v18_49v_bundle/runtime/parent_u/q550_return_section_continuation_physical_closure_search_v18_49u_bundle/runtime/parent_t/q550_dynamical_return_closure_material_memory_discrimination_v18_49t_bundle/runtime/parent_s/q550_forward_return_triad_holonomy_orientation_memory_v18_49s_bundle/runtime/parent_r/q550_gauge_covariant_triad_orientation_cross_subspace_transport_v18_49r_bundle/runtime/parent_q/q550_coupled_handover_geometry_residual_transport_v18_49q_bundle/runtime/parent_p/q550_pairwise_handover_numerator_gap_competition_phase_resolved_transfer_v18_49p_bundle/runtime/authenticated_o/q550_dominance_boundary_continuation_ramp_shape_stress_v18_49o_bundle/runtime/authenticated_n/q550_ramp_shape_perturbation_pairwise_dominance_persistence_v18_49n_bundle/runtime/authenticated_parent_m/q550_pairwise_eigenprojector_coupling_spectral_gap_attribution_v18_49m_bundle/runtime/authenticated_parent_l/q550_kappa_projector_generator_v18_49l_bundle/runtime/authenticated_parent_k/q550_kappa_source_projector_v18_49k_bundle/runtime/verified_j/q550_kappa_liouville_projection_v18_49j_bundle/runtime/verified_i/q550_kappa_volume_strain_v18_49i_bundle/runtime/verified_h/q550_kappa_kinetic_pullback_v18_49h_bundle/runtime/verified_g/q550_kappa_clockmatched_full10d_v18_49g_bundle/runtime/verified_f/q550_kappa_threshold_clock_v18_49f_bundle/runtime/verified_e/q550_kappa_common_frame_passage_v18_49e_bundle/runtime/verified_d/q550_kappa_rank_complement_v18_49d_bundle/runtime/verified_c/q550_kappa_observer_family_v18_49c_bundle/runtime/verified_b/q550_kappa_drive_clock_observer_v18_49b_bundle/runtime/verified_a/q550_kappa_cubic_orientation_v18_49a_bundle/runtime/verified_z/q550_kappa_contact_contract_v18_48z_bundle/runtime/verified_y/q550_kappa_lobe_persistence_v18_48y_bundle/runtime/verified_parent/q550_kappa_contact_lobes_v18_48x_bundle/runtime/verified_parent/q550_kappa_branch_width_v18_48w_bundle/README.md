# Q550 v18.48w — Branch-Resolved Work-Sign & Contact-Width Continuation Audit

**Status:** full eight-path genuine 11D numerical preflight finished, plus unchanged original v18.48v server-sendback authentication. This is a floating-point counterfactual diagnostic, not an interval proof.

## Purpose

The preceding v18.48v audit found branch-dependent favorable braking durations and a misleading ensemble-median sign transition in drive work at matched external phase. **v18.48w** follows each **original physical branch and both kappa parameters separately**, refining the local ramp grid and comparing:

1. minimum equal-external-phase geometry-only separation in `(log rho1, log rho2, x)`;
2. width of the return-phase interval in which that separation remains below each of `0.0025`, `0.005`, and `0.01`;
3. signed **cumulative drive work** at three fixed external return phases `q = 0.35, 0.50, 0.65`, *without* moving the phase to a convenient contact minimum;
4. 11D state separation, five-velocity separation, energy and individual power at the optimized near-contact.

These observables are **not interchangeable**. A near-contact in 3D need not be a full-state recurrence. The cumulative signed work is a term of the model mechanical ledger, not entropy production. An ensemble-median zero is not a sign reversal of a single material path.

## Authenticated input and reproducibility

`inputs/v18_48v_original_server_sendback.zip` is the **unaltered user-server sendback** (from October 27, 2026). `scripts/verify_parent.py` authenticates its exact hierarchy, all SHA-256 manifest entries, original source bytes and recursively pinned `u → t → s → r → q → p → o → j` genealogy. The original 328 history states derive from that chain; they are not synthesized.

**Original dynamic equations:** inherited bytes `reference/physical_math.py`, `reference/transversality_math.py`, and the older verified support RHS from the nested ancestor. We integrate material coordinates and the four energy-work accumulators with **DOP853**, `rtol=3e-12`, `atol=3e-13`, `max_step=0.025`. The externally commanded phase is evaluated analytically; it is not a free new dynamical state. We use the inherited original cubic braking law, `c(t)=1-2[3(t/r)^2-2(t/r)^3]` in a braking segment of duration `r`, followed by `c=-1`. The history is matched to the forward orbit at `s=1-q`, `q in [0.312500001, 0.719999999]`.

**Material velocities are fully inverted at the turn, alpha=1**. Reversing these velocities preserves their initial kinetic energy. Other velocity-preparation fractions tested in the parent are not resimulated here.

### Scan structure

The **original 17-point full ramp grid** from the authenticated v18.48v output is reused *unchanged*, without falsely counting it as new integration. Each historical trajectory gets **8 new local ramp values** near its v-optimum, plus **one independent replay at the original center ramp** to cross-check parent numerical contact depth, contact-width, full-state gap and fixed-phase signed work. There are eight trajectories (two families × two physical branches × two kappa choices).

| Family | Branch | Original best sampled ramp | New sampled ramps |
| --- | ---: | ---: | --- |
| phaseblind | 0 | 0.28 | .260, .265, .270, .275, .285, .290, .295, .300 |
| phaseblind | 1 | 0.07 | .050, .055, .060, .065, .075, .080, .085, .088 |
| phasecov | 0 | 0.04 | .020, .025, .030, .035, .045, .050, .055, .060 |
| phasecov | 1 | 0.35 | .330, .335, .340, .345, .355, .360, .365, .370 |

Note the upper phaseblind-1 refinement is `.088`, not `.090`, because `.090` is already on the authenticated original grid; this preserves exactly eight **new** samples per path. Original selected-center runs are counted as genuine independent regression runs, not new ramp values.

The 80 newly executed 11D integrations are **8 forward physical replays + 8 × (8 additional ramps + 1 repeated center)**. They add 64 new optimized contact rows to 136 inherited original-alpha=1 rows, giving 200 combined ramp/contact rows and 600 matched-phase work/energy rows (25 ramps × 3 phases × 8 paths).

## Original-kappa numerical preflight, q = 0.50

| Family | Branch | Best sampled ramp xi | Best 3D shape gap | Ramp with widest `d3<0.01` phase interval | Width in phase q | Cumulative drive-work sign across 25 ramps |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| phaseblind | 0 | .275 | .000356164 | .300 | .165175 | negative |
| phaseblind | 1 | .070 | .000216918 | .070 | .032014 | positive |
| phasecov | 0 | .040 | .001463764 | .035 | .022953 | positive |
| phasecov | 1 | .335 | .000320192 | .370 | .054362 | negative |

The **same signed-work pattern persists for each of the three fixed phases (`.35`, `.50`, `.65`) and both kappa choices** in all 25 sampled ramps, with a sign floor of `1e-12` work units. No within-branch sign reversal is resolved on this finite grid.

**Important:** the phase width is not a physical time, not an invariant and not a certified exhaustive measure of all sub-grid components. Its definition is a *thresholded portion of the chosen q-window*. Optimizing depth and optimizing width select different ramps on three of four original-kappa branches, but this is a finite-grid observation, not a continuous extremum theorem.

## Numerical gates and scientific boundaries

- **9/9 math unit tests passed.** Full eight-path audit accepted by `scripts/check_outputs.py`.
- Maximum original-v center-ramp cross-check error: `3.04e-13` (far below declared `2e-7`).
- Maximum normalized original mechanical ledger error in new integrations: `4.08e-10` (gate `1e-8`). Parent v itself uses floating-point verification, not interval arithmetic.
- Every full state keeps an independent 11D distance and five-velocity distance beside 3D geometry.
- The contact minimum is optimized only on the inherited 81-point q-scan using local bounded minimization, not a global proof. The root-bracketed threshold widths can miss sub-grid disconnected components.
- The same final external phase can be reached at different elapsed times with different command histories. This protocol dependence is **not** alone a causal constitutive time constant, a thermodynamic entropy statement, or a universal law of counterflow.

## Server execution

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_branch_width_v18_48w_bundle.zip
cd q550_kappa_branch_width_v18_48w_bundle
bash run_on_server.sh 2>&1 | tee v18_48w_server.log
```

The default launcher uses Python 3.13 and invokes tests, genealogy/source verification, genuine integrations, numerical acceptance gates, plotting, and the sendback packer. Override Python with `Q550_PYTHON=/path/to/python` if necessary. The output is `sendback.zip`. Do not place the archive under a different inner root; the ZIP actually includes exactly one root named `q550_kappa_branch_width_v18_48w_bundle/`.

A cheap smoke of a **single physical trajectory** (not a full scientific run):

```bash
python3.13 scripts/run_audit.py --limit-groups 1
python3.13 scripts/check_outputs.py
```

Then rerun `bash run_on_server.sh` to restore all eight paths and regenerate the full sendback.

## Files and provenance

- `inputs/v18_48v_original_server_sendback.zip`: full byte-original user v sendback, *including the authentic parent history chain*.
- `inputs/SOURCE_PINS.json`: SHA-256 pin of the server original and each inherited exact reference file.
- `reference/*.py`: original mathematical source bytes, including `parent_ramp_math.py`.
- `scripts/{verify_parent,continuation_math,run_audit,check_outputs,plot_results,pack_sendback}.py`: actual executable source.
- `results/new_refined_contacts.csv`, `new_refined_fixed_phase_energy.csv`: only newly integrated ramps / independent center checks; contains the original center too in fixed phase for explicit regression.
- `results/combined_branch_contacts.csv`, `combined_branch_fixed_phase_energy.csv`: verified historical v entries plus genuine new refinements, with no duplicate center.
- `results/branch_resolved_work_signs.csv`: numerical signs for each family, branch, kappa, phase, plus any **brackets** where a sign changes (not invented roots).
- `results/branch_resolved_window_summary.csv`: independent depth-optimum and width-optimum ramp for each threshold, separately by original branch.
- `results/original_center_regression.csv`, `historical_replay.csv`, `report.json` and four generated PNGs.
- `tests/test_continuation.py`, `SCIENTIFIC_DECISION_RULES.md`, requirements, manifest `SHA256SUMS_OUTPUT.json` and executable `run_on_server.sh`.

**Genealogical rule:** the script creating figures is always included; input, output, generated file hashes and original ancestors are part of the archive. Different code paths can be acceptable if they have the same mathematical purpose and independently verified functional outcomes; we do not alter historical artifacts to retrofit new directory names.
