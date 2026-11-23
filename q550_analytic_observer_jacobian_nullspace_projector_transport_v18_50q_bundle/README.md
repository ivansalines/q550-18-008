# Q550 v18.50q — Analytic Observer Jacobian & Nullspace Projector Transport Audit

This audit takes **one authentic v18.50p server sendback** as its immutable parent. Its recorded parent ZIP is verified at all 11 source and 7 output SHA-256 hashes. The nested original Q550 10D model is staged in a temporary directory for replay, then discarded. No extracted 1.4 GB genealogy enters the generated sendback.

## Main question

Is the tiny fourth singular value of the 4D structural-jet observer physical, and does its hidden 10D kernel remain invariant under true 10D linearized transport?

## Key results (local verified run)

- The observer is `d = (h4 / common_scale) / ||h4 / common_scale||`, hence the **exact** identity `d.T @ B = 0` and **rank(B) <= 3** anywhere it is defined.
- The analytic Jacobian is evaluated by the chain rule using the exact `F,J,H` tensors of the historical Q550 structural jet, not by numerical differences of the 4D observer.
- The 34 sampled sections (17 per κ₀) have numerical rank **3**. The fourth singular value from analytic evaluation is at most `5.714e-14`; the third stays at least `0.48950`.
- The pointwise 10D observer kernel has **dimension 7** in these sections. It is represented by a complete orthogonal projector, not a sign-unstable, selected singular vector.
- Transporting its initial seven-dimensional basis with the 10D model variational flow gives a maximum principal angle from the instantaneous kernel of about `0.00215149°`, with maximum projected leakage `1.5364e-5` (in the declared normalization).
- The short-window projector discrepancy is numerical evidence about observer non-closure, **not** a certificate of material memory, a physical metric, or a unique hidden mode.

## Server execution

```bash
cd /root/elab1/hysteresis
unzip q550_analytic_observer_jacobian_nullspace_projector_transport_v18_50q_bundle.zip
cd q550_analytic_observer_jacobian_nullspace_projector_transport_v18_50q_bundle
set -o pipefail
PYTHON_BIN=python3.13 bash run_on_server.sh 2>&1 | tee ../v18_50q_server.log
```

This command checks the immutable source manifest, runs analytic tests, authenticates the parent, reconstructs the genuine physical trajectory, computes the analytic observer Jacobian and transports the full 10D variational operator, then creates a fresh output manifest and a small server sendback outside the bundle directory.

To run the fast algebra-only tests:

```bash
python3.13 tests/test_analytic_observer.py
```

The full audit is deliberately more expensive because it stages the authentic historical solver; its temporary genealogy is removed automatically. Use `PYTHON_BIN` rather than editing `run_on_server.sh` to avoid source hash drift.

## Contents

- `scripts/run_audit.py`: the complete mathematical/computational audit (both κ₀ branches).
- `tests/test_analytic_observer.py`: independent chain-rule finite difference and projector/rank tests.
- `inputs/q550_near_null_tangent_direction_stencil_order_transport_v18_50p_bundle_server_sendback.zip`: authenticated parent.
- `results/analytic_observer_rank_ledger.csv`: 34 exact-chain-rule / numerical comparison rows.
- `results/nullspace_projector_transport_ledger.csv`: 34 transport rows, principal angles and leakage.
- `results/*.png`: three independent diagnostic figures.
- `results/report.json`: structured report and limits.
- `SOURCE_MANIFEST.json` and `SHA256SUMS_OUTPUT.json`: immutable origin vs regenerated results.
- `scripts/pack_sendback.py`: packs only manifest-listed sources and outputs; no `runtime`.

Scientific comments and supporting documents are in English. The execution history is reproducible but does not constitute a global interval rank or physical-memory certificate.
