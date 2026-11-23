# Q550 v18.48r — Counterflow Crossing Transversality & Phase-Conditioned Recurrence Audit

**Status:** Executed numerical preflight; fully runnable from a clean extracted ZIP.

This audit uses the **original 11-dimensional Q550 support differential equations**, with two κ₀ choices and the true externally driven clock. It builds on the **unaltered original v18.48q server sendback**, preserved inside `inputs/`, and verifies the nested v18.48p, v18.48o, and v18.48j genealogy before every main run. Historical input states, ODE parameters, and the selected mechanical energy formula are not inferred from CSV plots.

## The distinction this audit tests

Three distinct kinds of geometric encounter must not be conflated:

1. **Free asynchronous near-pass in 3D:** separately optimize the two times of the forward and counterflow IVPs in the three-component reduced chart `(log rho1, log rho2, x)`. Source minima are those authenticated in v18.48q; the new calculation reintegrates all 88 11D IVPs and recomputes derivatives and full-state observables at these pairs.
2. **Two-dimensional projected crossing:** solve for two coordinates of the 3D shape to be equal at different times. The third coordinate, the full 11D mismatch, both internal phases, the external phase, velocities, energy, and 3D line-angle all remain explicit. A 2D crossing is not a 3D crossing.
3. **Externally phase-conditioned recurrence:** constrain the drive phase to agree **at the compared instants**, not merely at the end of a phase-closed counterflow protocol. On these source trajectories the unwrapped phase equality is `s = 1 - (rate × duration) × u`, where `u` is return progress and `s` is forward progress. In the phase-closed experiments (`rate × duration = 1`) this becomes `s=1-u`. A fixed-duration return at a different command rate is **not** phase-closed and has its own admissible phase-matched domain.

The tangent diagnostic uses the actual derivative of each 11D IVP, pushed into the three-coordinate shape chart. The **unoriented line angle** is `acos(|cos|)` between the two chronologically oriented curve tangents; a small line angle indicates **near-parallel** passages, not proof of material torsion. The corresponding oriented (chronological) angle and the 3D tangent cross magnitude are saved separately.

## Numerical preflight findings

- **88 genuine 11D integrations** (8 forward + 80 counterflow), on 328 authenticated historical 11D section states.
- The **six interior free-time minima** from the original q sendback remain numerically unchanged (maximum gap regression about `9.44e-16`). All six involve initial material velocity reversal. Their 3D line-angles range from approximately **0.626° to 8.609°**, median **1.083°**: mostly near-tangential, not large-angle crossings.
- The closest free-time 3D near-pass has shape distance `1.06222e-4` but nonzero complete-state mismatch `~3.65` and drive phase mismatch approximately `-0.525 rad` (different forward/return instants).
- The tightest **phase-constrained** shape approach across 80 protocols has 3D distance `9.63121e-4` and still a nonzero 11D separation. The smallest free and constrained values are **not from the same trajectory**, so compare them descriptively, not as a within-case penalty.
- A sampled two-coordinate chord search and dense-IVP refinement yielded **58 numerically resolved crossings in 2D projections**; none of these 58 has equal external drive phase to numerical tolerance. The smallest 3D gap at one of these 2D roots is `1.11939e-4`, so it is not a 3D crossing. The 58 roots include related runs at both κ₀ and two experiment designs; they are *not* 58 independent physical events or an exhaustive intersection count.
- The energy identity residual stays below `2.05e-15` in this preflight; this verifies the selected model's differential energy ledger numerically but does not prove thermodynamic irreversibility.

## Run on the Linux server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_counterflow_transversality_v18_48r_bundle.zip
cd q550_kappa_counterflow_transversality_v18_48r_bundle
bash run_on_server.sh 2>&1 | tee v18_48r_server.log
```

Requires Python 3.13, NumPy, SciPy and Matplotlib. The preflight used DOP853 with `--rtol 3e-12 --atol 3e-13 --max-step 0.0125` and `--projection-nodes 141`. The default run takes longer than v18.48q because it evaluates tangents and refines individual projected roots. Configure parameters using:

```bash
python3.13 scripts/run_audit.py --help
```

Running generates `results/`, `SHA256SUMS_OUTPUT.json`, and **`sendback.zip`**. The runner verifies 10 independent unit tests before the audit and automatically checks the nested source ZIP. It does *not* require historical orbit symlinks.

## Files and scientific genealogy

- `inputs/v18_48q_original_server_sendback.zip`: **unchanged real server sendback**, including the original q scripts, reports, and q→p→o→j genealogy.
- `inputs/SOURCE_PINS.json`: SHA-256 pins for the entire parent archive and inherited source math.
- `reference/physical_math.py`, `reference/crossing_math_q.py`: byte-for-byte copies of verified q source helpers.
- `scripts/verify_parent.py`: authenticates q's manifest and nested p/o/j ancestry; checks source byte identity and original 11D state cache SHA-256.
- `scripts/transversality_math.py`: independent analytic shape tangent and phase constraint, 2D segment intersection screening, dense-IVP projected crossing refinement.
- `scripts/run_audit.py`: original RHS integration, mechanical ledger, 3D line/transversality diagnostics, external phase-matched constrained minima, CSV & JSON reports.
- `scripts/plot_results.py`: regenerates three PNGs **only from actual calculated data**.
- `scripts/pack_sendback.py`: constructs the output manifest and server sendback.
- `tests/test_transversality_math.py`: 10 tests (unoriented vs oriented angles, phase maps, geometric projected roots and non-crossings, logistic derivative, synthetic phase lock).
- `results/crossing_transversality.csv`: all 160 free/phase-conditioned candidate pairs with tangent, phase, shape, full-state and energy observables.
- `results/projection_crossings_2d.csv`: detected crossing plane, refined root, 3D mismatch, tangents, 11D mismatch, phase and energy.
- `results/phase_conditioned_protocols.csv`: per-protocol comparison of unconstrained q and constrained phase-matched near-pass, and verified work/dissipation.
- `results/source_regression.csv`, `results/report.json`, `results/phasecov_selected_trajectories.npz`: validation, summary, and actual 11D plot input.
- `SCIENTIFIC_DECISION_RULES.md`: interpretive gates and explicit nonclaims.
- `SHA256SUMS_OUTPUT.json`: outputs and sources SHA-256 manifest.

## Limits

A local dense-output root with tiny 2D residual is **only a crossing in the named projection**. The 3D geometry is an explicit chart, not an invariant metric. In three dimensions two trajectories generically miss each other. Since the free near-passes and the plane intersection screenings are numerical, no global existence/exclusion theorem is claimed. The setup does not model a complete physical material reversal, nor establish a universal hysteresis law. Reproducing a mechanical energy balance is not an independently conserved-energy theorem.
