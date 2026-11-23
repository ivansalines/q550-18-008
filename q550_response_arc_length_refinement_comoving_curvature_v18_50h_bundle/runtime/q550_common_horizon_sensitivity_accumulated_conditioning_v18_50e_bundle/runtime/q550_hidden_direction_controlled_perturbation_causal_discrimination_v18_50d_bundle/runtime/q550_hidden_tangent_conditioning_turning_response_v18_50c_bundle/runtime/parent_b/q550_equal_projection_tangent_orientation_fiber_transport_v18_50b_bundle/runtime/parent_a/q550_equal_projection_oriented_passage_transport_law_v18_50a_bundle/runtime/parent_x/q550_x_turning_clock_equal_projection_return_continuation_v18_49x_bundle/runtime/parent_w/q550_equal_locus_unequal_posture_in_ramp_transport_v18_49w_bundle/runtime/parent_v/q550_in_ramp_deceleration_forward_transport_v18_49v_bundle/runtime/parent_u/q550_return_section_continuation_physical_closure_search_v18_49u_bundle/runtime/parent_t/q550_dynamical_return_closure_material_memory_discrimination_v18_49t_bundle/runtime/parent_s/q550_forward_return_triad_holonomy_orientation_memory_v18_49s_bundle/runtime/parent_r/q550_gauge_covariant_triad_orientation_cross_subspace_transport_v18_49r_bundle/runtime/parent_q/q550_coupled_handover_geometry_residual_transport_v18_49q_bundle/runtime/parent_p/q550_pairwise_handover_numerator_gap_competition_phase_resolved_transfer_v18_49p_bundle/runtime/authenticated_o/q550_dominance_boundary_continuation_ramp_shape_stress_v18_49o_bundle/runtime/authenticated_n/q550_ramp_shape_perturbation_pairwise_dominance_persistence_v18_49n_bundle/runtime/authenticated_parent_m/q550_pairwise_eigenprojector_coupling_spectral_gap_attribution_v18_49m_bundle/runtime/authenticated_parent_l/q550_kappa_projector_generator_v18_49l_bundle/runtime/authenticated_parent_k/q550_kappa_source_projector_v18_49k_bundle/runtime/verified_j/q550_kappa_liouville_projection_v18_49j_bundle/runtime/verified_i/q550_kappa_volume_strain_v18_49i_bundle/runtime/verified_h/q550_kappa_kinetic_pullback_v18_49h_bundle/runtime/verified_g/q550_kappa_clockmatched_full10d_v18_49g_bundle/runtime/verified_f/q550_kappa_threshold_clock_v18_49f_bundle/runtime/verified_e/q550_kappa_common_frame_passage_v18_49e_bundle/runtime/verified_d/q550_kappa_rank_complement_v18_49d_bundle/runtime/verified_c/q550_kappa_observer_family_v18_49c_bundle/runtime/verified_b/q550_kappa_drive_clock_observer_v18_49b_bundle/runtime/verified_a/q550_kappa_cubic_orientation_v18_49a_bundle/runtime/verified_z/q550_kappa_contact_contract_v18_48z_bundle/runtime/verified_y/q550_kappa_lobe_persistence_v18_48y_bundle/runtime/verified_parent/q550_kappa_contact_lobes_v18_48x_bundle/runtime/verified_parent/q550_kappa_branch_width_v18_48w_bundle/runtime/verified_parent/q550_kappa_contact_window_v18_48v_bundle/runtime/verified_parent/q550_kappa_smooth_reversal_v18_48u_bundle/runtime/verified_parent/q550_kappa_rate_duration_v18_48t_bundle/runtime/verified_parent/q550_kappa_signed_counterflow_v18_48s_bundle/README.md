# Q550 v18.48s — Signed Counterflow Tangent & Phase-Locked Near-Contact Audit

**Status: authentic numerical preflight completed; original 11D equations; independently authenticated v18.48r server-return provenance.** The v18.48s program is executable from a clean ZIP extraction. All source comments and scientific documentation are in English.

## Scientific question

At points where a forward Q550 IVP and its forward-time, drive-reversed return approach the **same external phase**, are their chronological geometric tangents aligned or opposed, and how do their **signed model-mechanical** energy flows differ *at that meeting*, rather than only at the end of the return?

The three-coordinate chart is **(log rho1, log rho2, x)**; the full material state has 11 coordinates. A 2D projected crossing, a 1-coordinate phase-locked zero, a near-pass in 3D, and an equal 11D state are separate mathematical statements.

## Run on the Linux server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_signed_counterflow_v18_48s_bundle.zip
cd q550_kappa_signed_counterflow_v18_48s_bundle
bash run_on_server.sh 2>&1 | tee v18_48s_server.log
```

Requires **Python 3.13**, NumPy, SciPy, Matplotlib. Set `Q550_PYTHON=python3.13` if necessary. The default numerics match the completed preflight:

```bash
python3.13 scripts/run_audit.py \
  --rtol 3e-12 --atol 3e-13 --max-step 0.025 \
  --phase-root-nodes 151
```

The script re-verifies the source ZIP, checks all nested source versions, integrates 88 original 11D IVPs, recomputes orientation and pointwise four-term energy powers, audits source regressions and the energy ledger, generates CSV/NPZ/JSON and real data plots, runs output gates, and writes **`sendback.zip`** and SHA-256 manifest. No symlink to historical orbit files is necessary. The parent source ZIP is preserved **byte-for-byte**.

## The two notions of tangent direction

Let `F(s)` be the forward 11D solution, `R(u)` the *chronologically evolving* return driven with negative external angular speed. If the imposed return angular speed has magnitude `rate` times the original and return duration is `duration`, write `a=rate*duration`.

```
Equal external phase: s(u) = 1 - a*u
Chronological tangents: t_R = d shape(R(u))/du; t_F = d shape(F(s))/ds
Equal-phase tangent correspondence: t_R versus -a * t_F
```

The chronological angle `acos( t_R · t_F / ||t_R|| ||t_F|| )` and the equal-phase angle `acos( -t_R · t_F / ||t_R|| ||t_F|| )` are supplements by construction. This algebraic relationship is **not** an extra physical finding; the measured distribution of chronological angles is. The equal-phase convention applies meaningfully **only** where equal external phase is imposed.

## Signed energy ledger

Use the original support model mechanical observable `E` and its four analytic contributions to `dE/dxi`:

1. imposed external drive power;
2. radial damping;
3. x damping;
4. nonconservative active-x work.

The return clock is prescribed as negative `rate`; the four signed terms are evaluated at the **actual forward and return meeting states**. Compare both local derivatives and cumulative work components. Reconcile the meeting energy gap to `W_F(turn) - W_F(s) + W_R(u)` (material velocity reversal at the turning point does not change its kinetic energy). These energy quantities are **not** claims of universal thermodynamic entropy production.

## Authenticated preflight observations

- 88 genuine original 11D integrations: 8 forward + 80 controlled forward-time returns; historical section regression maximum about **1.47e-11**.
- 160 r-anchored continuous-output contact pairs (80 free asynchronous, 80 equal external phase), plus 58 original r-resolved 2D projection roots re-evaluated on new IVPs.
- **104 bracketed zeros of single geometry coordinates at equal phase**, from a 151-node scan per protocol: **not** 104 intersections in 3D.
- At the 80 equal-phase near-contact minima: median chronological tangent angle about **4.195 degrees**; **56/80** below 10 degrees and **20/80** above 170 degrees.
- Signed drive power at these two states has opposite sign in **60/80** protocols (not statistically independent). The energy difference is negative in **52/80**, positive in **28/80**.
- Minimum equal-phase 3D separation approximately **9.63121e-4**; no complete 11D reunion is inferred.
- The numerical four-term integrated energy identity closes with normalized residual at most **1.471e-14**; the independently recomputed meeting energy gap ledger closes within **4.79e-14** absolute.
- Maximum r-anchor near-pass shape recheck discrepancy **1.97e-12**. Projected 2D roots still have zero matched external-phase events.

**Interpretation:** The signed tangent orientation and the chosen signed mechanical drive-work terms offer a *specific* measure of return-history asymmetry under the prescribed protocols. Neither a 2D crossing nor a near-contact proves a genuine full-state return. The counts have systematic dependence on the chosen 3D chart, initial seed families, and reversal protocols. No constitutive hysteresis, canonical energy flux, or observer-independent torsional transport law is certified.

## Files

- `inputs/v18_48r_original_server_sendback.zip` — exact, unchanged **server** return from v18.48r, containing q→p→o→j genealogy.
- `inputs/SOURCE_PINS.json` — SHA-256 pins of this original archive and byte-for-byte math helper copies.
- `reference/physical_math.py` — unchanged original-support energy/RHS adapter from r.
- `reference/transversality_math.py` — unchanged original 3D shape and tangent math from r.
- `scripts/verify_parent.py` — verify archive manifest, all contents, nested ancestry, original historical NPZ.
- `scripts/signed_math.py` — independent signed tangent, projected chirality, equal-clock phase mapping, energy derivative, bracketed single-coordinate roots.
- `scripts/run_audit.py` — 88 authentic 11D IVPs with 15D state including integrated mechanical work; new contact and power measurements.
- `scripts/check_outputs.py` — output-level scientific regression checks.
- `scripts/plot_results.py` — four genuine numerical figures.
- `scripts/pack_sendback.py` — deterministic member manifest and sendback ZIP.
- `tests/test_signed_math.py` — ten independent synthetic/unit tests.
- `results/signed_contacts.csv` — complete set of free-time and equal-clock-meeting diagnostics.
- `results/signed_projected_crossings.csv` — 58 projection-root signed chiralities with residual full-dimensional mismatches.
- `results/phase_locked_one_coordinate_roots.csv` — real bracketed one-coordinate zeros at equal phase.
- `results/protocol_summary.csv`, `results/source_regression.csv`, `results/report.json` — methodological and outcome summaries.
- `results/phasecov_phase_locked_paths.npz`, `results/*.png` — original new IVP plot data and figures.
- `SCIENTIFIC_DECISION_RULES.md` — explicit scientific interpretation gates and nonclaims.
- `SHA256SUMS_OUTPUT.json`, `sendback.zip` — generated output authenticity and transport.

## Caution on figures

The equal-phase trajectory figure includes `u=0`, where return and forward shape coincide **trivially by the reversal setup**. This prescribed turning point is excluded from the nontrivial near-contact search, which uses `u>=0.25` (and compatible `s` bounds). Its zero shape gap must not be counted as a discovered return.
