# Q550 v18.50k — Log-Balance / Orientation Gate & Advancing Response Audit

## What this audit answers

Does the norm-parity event `||L||=||T||` terminate the geometric cancellation, or can
relative orientation continue to advance until a later stationary event?
We measure this with the fully specified geometric gate
`H = sin(theta/2)/cosh(u/2)` where `u=ln(||T||/||L||)` and
`theta=acos(<L,T>/(||L|| ||T||))`, using the v18.50j server sendback.

**This is algebraic/numerical postprocessing, not an additional Q550 physical integration.**
The complete authenticated server sendback v18.50j is in `inputs/`, including
its earlier executable genealogy through v18.50i and the original solver.

## Run on the Q550 server

```bash
cd /root/elab1/hysteresis
unzip q550_log_balance_orientation_gate_transport_v18_50k_bundle.zip
cd q550_log_balance_orientation_gate_transport_v18_50k_bundle
bash run_on_server.sh 2>&1 | tee ../v18_50k_server.log
```

Requires Python 3.9+ and the packages in `requirements.txt`.
The original source/parent ZIP is never rewritten. Each execution regenerates
`results/` and updates its own `SHA256SUMS_OUTPUT.json`.
Matplotlib metadata, PNG byte hashes, floating output hashes and console logs
are execution-specific, not falsely assumed to be source-integrity failures.

For a sendback:

```bash
cd /root/elab1/hysteresis
zip -qr q550_log_balance_orientation_gate_transport_v18_50k_server_sendback.zip \
  q550_log_balance_orientation_gate_transport_v18_50k_bundle v18_50k_server.log
```

## Files

- `scripts/verify_parent.py`: strict verification of j numerical sources using 17
  original manifest entries, with four explicitly pinned PNG `Software` metadata
  exceptions (remaining PNG chunks must be byte-identical).
- `scripts/gate_math.py`: exact geometric identity and differential.
- `scripts/run_audit.py`: independent ledger, event scan, visualizations, output report.
- `tests/test_gate_math.py`: algebraic, label-swap and finite-difference checks.
- `tests/test_decision_rules.py`: scientific event/metric decision rules.
- `scripts/verify_source_manifest.py` and `SOURCE_MANIFEST.json`: immutable inputs,
  scripts and reports are always SHA-256 checked.
- `scripts/write_output_manifest.py`: fresh per-run hashes of generated outputs.
- `results/geometric_gate_ledger.csv`: 4,800 analyzed numerical rows.
- `results/geometric_gate_events.csv`: 30 configuration/event summaries.
- `results/report.json` and four PNG figures.

See `SCIENTIFIC_REPORT.md` and `SCIENTIFIC_DECISION_RULES.md`.

## Identification and limitations

`kappa0_original = 1/6` and `kappa0_autonomous = 7*pi/132` at `n=10,Q=550`.
The autonomous rule is an input to this study, not independently physically validated.
All norms, angles and derivatives are from the explicitly chosen *sensitivity charts*.
The event locations remain cubic-spline interpolations of sampled traces, not
validated continuous-root enclosures. No inference of material memory, stress,
strain, yielding, or causal origin from this identity alone is permitted.
