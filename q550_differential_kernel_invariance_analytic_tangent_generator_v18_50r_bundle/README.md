# Q550 v18.50r — Differential Kernel Invariance & Analytic Tangent Generator Audit

## Purpose

Test whether the seven-dimensional instantaneous kernel of the normalized structural-jet observer is infinitesimally invariant under the true driven Q550 10D tangent flow, in the inherited fixed Euclidean chart. Do not infer material memory, kinetic energy, physical stress, or a torsional flip from a projector defect.

## Executable genealogy

- `inputs/q550_analytic_observer_jacobian_nullspace_projector_transport_v18_50q_bundle_server_sendback.zip` is the *authentic server sendback* from v18.50q and contains its authenticated v18.50p parent and the preceding solver genealogy.
- `scripts/run_audit.py` verifies every q source/output hash, stages the original model temporarily, computes two new natural replay trajectories, and evaluates the analytic tangent generator. **No historical source is edited.**
- The original structural jet supplies the 11D RHS Jacobian, restricted to the ten driven state coordinates and transformed to the common seed chart. An independent finite-difference RHS Jacobian is calculated at three sections per branch as a regression.
- The normalized observer Jacobian `B` is analytic (v18.50q). The time derivative `Bdot` uses a centered fourth-order stencil along the newly integrated driven trajectory. Two stencils test temporal discretization sensitivity.
- The orthogonal seven-dimensional kernel projector is studied as a *subspace*, not by choosing an arbitrary singular vector.
- A separate output manifest records regenerated artifacts; the immutable source manifest is never rewritten by the runner. Any temporary genealogical workspace is excluded from the sendback.

## Run on the server

```bash
cd /root/elab1/hysteresis
unzip q550_differential_kernel_invariance_analytic_tangent_generator_v18_50r_bundle.zip
cd q550_differential_kernel_invariance_analytic_tangent_generator_v18_50r_bundle
set -o pipefail
PYTHON_BIN=python3.13 bash run_on_server.sh 2>&1 | tee ../v18_50r_server.log
```

Run tests or parent authentication alone:

```bash
python3.13 tests/test_kernel_invariance.py
python3.13 scripts/run_audit.py --preflight-only
```

The full command generates a ZIP in `/root/elab1/hysteresis/q550_differential_kernel_invariance_analytic_tangent_generator_v18_50r_bundle_server_sendback.zip`. Do not edit `run_on_server.sh`; select Python through the `PYTHON_BIN` environment variable. The history is temporarily staged, and this can use considerably more disk space than the ~60 MB ZIP. Only the selected records, sources, exact parent ZIP and manifest enter the sendback.

## Output interpretation

`results/differential_kernel_invariance_ledger.csv` records 17 sections per kappa family at the inherited parity-to-maximum passage. The key fields are `kernel_invariance_defect_norm`, `shape_term_norm`, `tangent_term_norm`, `projector_differential_gap_norm`, `max_lifted_principal_rate_rad_per_xi`, and the numerical-convergence controls. The file `results/parent_q_transport_comparison.csv` compares local rate and the inherited q endpoint principal angle without equating them automatically.

See `SCIENTIFIC_DECISION_RULES.md` for required interpretation. Scientific comments and reports are in English; short user discussion can be in Italian.
