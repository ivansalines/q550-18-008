# Q550 v18.49q — Coupled Handover Geometry & Residual Transport Audit

**Question:** What remains geometrically coherent while the rank-ordered pairwise coupling 6–7 yields the lead to 7–8, and what fraction of instantaneous and finite transport is NOT captured by the two leading pairs?

This v18.49q experiment re-integrates the authentic Q550 11D return and 10D variational transport, in the **same historical kinetic metric and fixed initial kinetic observer reference**. It authenticates the original server-produced v18.49p sendback ZIP (and its complete v18.49o…v18.48j nested ancestry) with exact SHA-256 manifest verification.

The 45 instantaneous pair channels are constructed from `K = A Ω Aᵀ`, where the ordered eigendirections form the matrix `A`. `Kij` is the skew operator for the given rank pair. The two selected couplings share eigendirection 7, so their Lie bracket is *algebraically* in the 6–8 plane. Independently measure the genuine 6–8 channel and all remaining 43. Check the projector equation `Pdot=[K,P]` by analytic expression and by **direct central difference of source-sampled projectors**, not only by algebra. Compare full finite orthogonal transport with pair-only and pair-plus-6–8 truncations. Use midpoint matrix exponentials and a factor-2 step-refinement check.

## Server commands

From `/root/elab1/hysteresis`:

```bash
unzip q550_coupled_handover_geometry_residual_transport_v18_49q_bundle.zip
cd q550_coupled_handover_geometry_residual_transport_v18_49q_bundle
bash run_on_server.sh 2>&1 | tee v18_49q_server.log
```

Full run: 5 cases (original r=0.32671875, 0.327375, 0.33; autonomous r=0.327375, 0.33), 151 phase samples on q=[.60,.65], finite transport over q=[.63,.65] with 200 midpoint steps and 100-step refinement. Four expected events. Minimal smoke: `bash run_on_server.sh --smoke --phase-samples 51 --transport-steps 40`; focused: `bash run_on_server.sh --focus` (two cases). Optional `Q550_PYTHON=python3.13` selects interpreter; Python >=3.10 with NumPy, SciPy and Matplotlib required. Runtime extraction goes to `runtime/`, not to the ZIP, to avoid ancestor duplication.

## Files

- `scripts/`: run, authentication, geometry, plots, report, manifest packaging. All comments and document citations are English.
- `tests/`: pure mathematical identities, rank-pair indexing, finite transport baseline.
- `inputs/`: original authenticated v18.49p server sendback and SHA pin, including every ancestor via nested ZIP.
- `results/phase_resolved_geometric_ledger.csv`: pair shares, remainder, Lie bracket, observed K68, leakage and closure at each q.
- `results/numerical_handover_geometry_events.csv`: root phases and phase-specific geometric observables.
- `results/report.json`: all five case metrics, numerical verification and scientific limitations.
- `SCIENTIFIC_REPORT.md`: interpreted numerical findings; `SCIENTIFIC_DECISION_RULES.md`: what would and would not count as an independent material explanation.
- `SHA256SUMS_OUTPUT.json`: manifest for the entire ZIP, not just figures.

## Interpretation boundary

The pair split is a rank-ordered-eigenspace decomposition, **not** independent particle identities. Lie bracket 6–8 is a kinematic fact; measured K68 is a distinct physical-model rate and not identified with the bracket. The 43-pair `Kother` is not a numerical defect: the algebraic reconstruction error is measured separately and should be near machine precision. The finite transport discrepancy depends on interval, time ordering, splitting and inherited metric. This audit does not certify an observer-independent torsional flip, or interval-certified root uniqueness.
