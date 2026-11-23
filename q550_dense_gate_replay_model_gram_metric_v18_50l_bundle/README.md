# Q550 v18.50l — Dense-Gate Physical Replay & Model-Jet Gram Metric Audit

Reproducible audit of a tightly bracketed Q550 sensitivity response near the early norm-parity and cancellation-stationarity events found in v18.50k.

## Purpose

1. Reintegrate the original model RHS on `Δξ = 0.00104 .. 0.00109` from each authenticated natural turning seed (two κ₀ models, a cubic 0.24 ramp).
2. Reproduce the events from **new physical-model ODE samples**, rather than merely refining the v18.50j/v18.50k interpolation.
3. Compare the common v18.50c observer normalization, raw-coordinate observer, and two *frozen model-jet Jacobian Gram candidates*. The Gram candidates are **not** physically derived kinetic energy metrics.
4. Test kick amplitudes `1e-4` and `1e-5`, event-bracket widths, and mesh refinements 129/257/513 sampled points (nested views of the **same** integrations).
5. Keep the authenticated v18.50k server sendback **immutable** while capturing newly executed outputs with a separate hash manifest.

## Execute

```bash
cd /root/elab1/hysteresis
unzip q550_dense_gate_replay_model_gram_metric_v18_50l_bundle.zip
cd q550_dense_gate_replay_model_gram_metric_v18_50l_bundle
bash run_on_server.sh 2>&1 | tee ../v18_50l_server.log
```

Optional overrides:

```bash
bash run_on_server.sh --samples 513 --epsilons 1e-4 1e-5 --rtol 3e-12 --atol 3e-13
```

**Warning:** Initial-seed reconstruction can be computationally expensive because it follows the original Q550 model genealogy, not an invented shortcut. The transient short IVP itself covers a much smaller interval.

## Dependencies

Python 3.9+, NumPy, SciPy, Matplotlib; versions logged in `results/report.json`. The complete executable ancestry is inside the pinned nested ZIP chain. Historical source files are authenticated by their original manifests before use. The derived `runtime/` folder is ignored by the artifact packager, as are `__pycache__/` and execution logs.

## Output files

- `results/dense_gate_vector_ledger.csv`: new model replays, sampled vector components, norm ratio, angle, cancellation, and IVP response discrepancy.
- `results/dense_gate_event_brackets.csv`: sampled brackets and spline event estimates, **not continuous root certificates**.
- `results/turn_replay_checks.csv`: physical turning-seed provenance.
- `results/report.json`: results, source SHA-256, model-jet metric eigenvalues and limits.
- `results/*.png`: new plots.
- `SHA256SUMS_OUTPUT.json`: regenerated output checksums (a different Matplotlib software metadata field cannot corrupt source identity).
- `SOURCE_MANIFEST.json`: exact immutable original source hashes.

## Caveats

The Q550 cancellation is a normalized geometric diagnostic of a chosen coordinate decomposition of sensitivity. It is not stress, energy, a yield law, a polymer constitutive equation, or material-memory evidence. Event locations are chart-dependent. A spline zero in a dense set of newly integrated values is a numerical estimate, not a rigorous proof of a unique continuous zero. Both κ₀ families use their own natural turning state, not a common initial state.
