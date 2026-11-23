# Q550 — v18.50i — Early Cancellation Balance & Metric-Robustness Audit

**Scope:** follow the sharp early cancellation found in v18.50h under both physical κ₀ inputs, multiple declared metric charts, and three finite intervention amplitudes. All outputs are obtained from fresh integrations with the original Q550 11D model and read-only authenticated genealogy. The measured 4-vector is the hidden structural jet `(f[2], f[6], (Jf)[2], (Jf)[6])`.

**Original κ₀:** 1/6. **Autonomous κ₀:** 7π/132 for n=10, Q=550. Both values are passed to the solver as prescribed model inputs, not inferred from these data.

## Execute

```bash
cd /root/elab1/hysteresis
unzip q550_early_cancellation_balance_metric_robustness_v18_50i_bundle.zip
cd q550_early_cancellation_balance_metric_robustness_v18_50i_bundle
bash run_on_server.sh 2>&1 | tee v18_50i_server.log
```

Use `Q550_PYTHON` for an alternative Python binary. Requires numpy, scipy, matplotlib. Source scripts in `scripts/`, tests in `tests/`, verified ancestor archive in `inputs/`. The run regenerates all results and packs `sendback.zip`.

## Audit geometry

`R = L + T` is the **declared coordinate split** of a linearized normalized hidden-direction response at common model phase Δξ. `L` differentiates the endpoint x-logit while holding other endpoint coordinates fixed; `T` differentiates the transported tangent less that coordinate basis. The cancellation scalar is `(||L||+||T||-||L+T||)/(||L||+||T||)` in a declared 4D normalization chart. This scalar is not a metric invariant, energy quantity or certified physical instability.

`peak_metric_amplitude_summary.csv` identifies sample extrema, not continuous roots. `early_metric_amplitude_trace.csv` keeps complete vector ledgers and error checks. All data terms, code comments, README and reports are English.
