# Q550 v18.48x — Contact-Lobe Topology & Phase-Boundary Audit

**Status:** full eight-history-path, genuine 11D floating-point numerical preflight. Not an interval enclosure, topological theorem, constitutive law, entropy proof, or physical torsion proof.

## Purpose

The authenticated **v18.48w** server sendback displayed two disjoint `d3 < 0.01` near-contact intervals in the `phaseblind` branch 0 at ramp `0.295 ξ`, but one interval at `0.300 ξ`. This audit tests whether the two intervals genuinely join as the commanded slowdown changes, or whether the apparent merging arises from finite phase-window truncation or the numerical sampling resolution.

**The observable** is the continuous equal-external-phase shape mismatch

`d3(q;r) = norm( (logrho1,logrho2,x)_return(t=r+q) - (logrho1,logrho2,x)_forward(t=1-q) )`

for a **cubic smoothstep drive reversal of ramp duration `r`**, with the historical material velocities fully inverted (`alpha=1`) at the turn. The remaining original material RHS and the original balance equation are copied *byte-for-byte*. A contact **lobe** is a connected component of the strict sublevel set `{q in [0.10,0.90]: d3(q;r)<threshold}`. It is NOT a separate material orbit or a physical object.

The **old v18.48w observation window** was `[0.312500001, 0.719999999]`. This audit expands it to `[0.10,0.90]`, while **deliberately excluding `q=0`**, where the forward and return paths share the geometric turning position by construction. We do not claim that components absent inside this declared extended window are absent globally.

## Genealogy

- `inputs/v18_48w_original_server_sendback.zip`: original **user server** returned archive, unmodified. SHA-256 pinned in `inputs/SOURCE_PINS.json`.
- `scripts/verify_parent.py`: validates *every* original W archive entry, path, SHA-256 and recursively authenticates `v → u → t → s → r → q → p → o → j`. Original 328 material states are obtained through this ancestry; no invented initial conditions.
- `reference/physical_math.py`, `reference/transversality_math.py`, `reference/original_drive_math.py`, `reference/parent_ramp_math.py`: identical historical bytes.
- `scripts/run_audit.py`: the **actual** DOP853 11D physical replay and lobe detection. `scripts/lobe_math.py` contains the independent sublevel-component and root-bracketing routines.
- `scripts/{check_outputs,plot_results,pack_sendback}.py`, tests, generated results, scientific boundary notes and output manifest complete reproducibility.

## Experimental design

All eight original paths (two families × two seed branches × two κ₀ choices) are replayed over the original forward `ξ ∈ [3.5,4.5]` sections. Two κ₀ values are intentionally kept distinct: original `1/6` versus the **independently proposed** autonomous value. Only one controlled physical RHS parameter changes.

For `phaseblind` branch 0 we integrate **18 ramp values per κ₀**:

`0.275, 0.285, 0.290, 0.292, 0.294, 0.295, 0.296, 0.29625, 0.2965, 0.29675, 0.297, 0.29725, 0.2975, 0.298, 0.299, 0.300, 0.302, 0.305`.

The remaining six paths are independently replayed at the branch-favored original W ramp values: `phaseblind` branch 1 `0.070`, `phasecov` branch 0 `0.040`, `phasecov` branch 1 `0.335` (both κ₀ choices). In total, **eight original forward integrations + 42 return ramp integrations + 22 critical barrier integrations = 72 genuine new original 11D integrations**.

For each ramp, evaluate `d3` at **1,601 uniform q samples** on the extended window. Locate all observed sign changes of `d3-threshold` using `scipy.optimize.brentq` on the *actual dense ODE interpolation*, not on a simulated image. Repeat the connected-component analysis on the old phase window. Four thresholds are tested: `0.0025`, `0.005`, `0.01`, `0.015`. The inter-lobe maximum near `q=0.4815` is independently optimized, then a **9-step bisection** in ramp duration follows the sign of `max(d3)-0.01`, using fresh physical integrations at every step.

**Threshold crossing is not certified against arbitrary sub-grid oscillations**; q-grid count and Brent roots do not constitute validated interval arithmetic. The 9-step final ramp brackets are algorithmic/numerical **not rigorous error enclosures**.

## Main numerical results

| κ₀ | Last grid interval with two/one lobes | Refined critical ramp bracket ξ | Inter-lobe phase near critical |
|---|---|---|---|
| Original 1/6 | 0.29625 / 0.29650 | **[0.2963325195, 0.2963330078]** | ~0.48159 |
| Autonomous | 0.29650 / 0.29675 | **[0.2965288086, 0.2965292969]** | ~0.48148 |

Both original and autonomous local changes occur **inside** both old and extended phase windows: the two components do not disappear at the phase boundary. The interface `d3 ≈ 0.01` is a *threshold-level* merger; it is not a crossing of complete 11D material trajectories. At the inter-lobe barrier the full-state gap stays approximately **1.899**, while the signed model mechanical-energy gap is approximately **−0.00594**.

**Important window-control result:** `phasecov` branch 0 at ramp `0.040` and κ₀ original has **one** observed contact interval in the historical W window, but **two** in `[0.10,0.90]`; the first newly resolved interval is near `q∈[0.22580,0.25508]`. This is *window truncation*, not the lobe merger seen in `phaseblind` 0. Do not mix the two mechanisms.

Original W width regressions (16 comparisons) agree to maximum absolute error **4.68×10⁻¹⁴**. Maximum physical-11D replay error is **1.65×10⁻¹¹**, and the model ledger normalized maximum is **2.88×10⁻¹⁰** (the declared acceptance gate is `1e-8`). Five unit tests plus generated-output acceptance gates pass.

## Execute on server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_contact_lobes_v18_48x_bundle.zip
cd q550_kappa_contact_lobes_v18_48x_bundle
bash run_on_server.sh 2>&1 | tee v18_48x_server.log
```

The default is `python3.13`; override with `Q550_PYTHON`. The runner **tests**, authenticates the entire original genealogy, performs all physical integrations, writes the numerical and root-bracket CSVs, validates scientific acceptance gates, generates plots and creates `sendback.zip`. The ZIP extraction root is exactly `q550_kappa_contact_lobes_v18_48x_bundle/`.

### Outputs

- `results/phase_lobe_summary.csv`: full-state separation, energy difference and connected-component counts for 42 return histories.
- `results/extended_lobe_intervals.csv`: all `42×4` original-vs-extended sublevel-component intervals and clipping flags.
- `results/focus_lobe_profiles.csv`: original actually evaluated distance profiles, `2×18×1601=57636` points for image reconstruction and independent analysis.
- `results/candidate_two_to_one_brackets.csv`: coarse topology-transition brackets without pretending they are exact roots.
- `results/critical_barrier_refinement.csv`: actual high-resolution physics reintegrations and sign-bracketing of the inter-lobe barrier.
- `results/original_w_width_regression.csv`, `results/report.json`, four PNG plots, and `SHA256SUMS_OUTPUT.json`.
- `sendback.zip`: full exact root archive including Python generators and unchanged nested original W sendback.

## Limits and decision boundaries

1. A merged strict sublevel set in a **3-coordinate projection** is not a recurrence in all 11 dynamical variables.
2. The change of sublevel topology depends explicitly on `threshold=0.01` and the chosen `q` window. Other thresholds have separate rows; no global persistence theorem is asserted.
3. The values `0.296332...` and `0.296529...` are *numerical* critical candidates for **this ramp family and this path**, not intrinsic relaxation times.
4. `q=0` is artificially coincident in geometric position; the study excludes this turn to avoid a trivial lobe. Conversely, the analysis cannot rule out additional lobes for `q<0.10` or `q>0.90`.
5. The energy difference is computed from the declared mechanical model and balanced against actual work/damping. It is **not** thermodynamic entropy, free energy, or a universal hysteresis identity.
6. Do not infer exact intersection, torsional flip, change of material topology, or phase-independent non-reciprocity from this audit alone.
