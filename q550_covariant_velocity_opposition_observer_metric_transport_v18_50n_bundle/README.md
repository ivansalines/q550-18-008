# Q550 v18.50n — Covariant Velocity Opposition & Observer-Metric Transport Audit

A fully executable **authenticated postprocessing** audit of the Q550 v18.50m server sendback and its embedded v18.50l dense RHS replay. No new physical integration is performed.

## Run on the server

```bash
cd /root/elab1/hysteresis
unzip q550_covariant_velocity_opposition_observer_metric_transport_v18_50n_bundle.zip
cd q550_covariant_velocity_opposition_observer_metric_transport_v18_50n_bundle
PYTHON_BIN=python3.13 bash run_on_server.sh 2>&1 | tee ../v18_50n_server.log
```

Dependencies: Python >=3.11, NumPy, SciPy, Pandas, Matplotlib. Python 3.13 is recommended. Results are written to `results/`; the self-contained sendback ZIP is written **one directory above** this bundle root. The run does not reconstruct the 1.4 GB temporary historical runtime and does not include transient log files in the source manifest.

## Genealogy

- Embedded original input: `inputs/q550_resultant_advance_intensity_orientation_rate_v18_50m_bundle_server_sendback.zip`.
- The v18.50m input embeds the real v18.50l server sendback, containing 10 earlier short RHS integrations and 8,208 metric-ledger rows.
- Both ancestors' source manifests and output manifests are validated before any scientific analysis. The pinned outer input is SHA-256 checked by the v18.50n source manifest.
- No ancestor files are modified. The v18.50n code reads nested archives in memory, not on the filesystem.

## Scientific operations

1. Reconstruct vector derivatives `L′,T′` from cubic splines of the dense, server-authenticated component vectors at the v18.50l cancellation events, with both κ₀ values and ε=1e-4/1e-5.
2. Compare velocity opposition in common normalized Euclidean observer, the **separate raw nonlinear observable**, and two *frozen* model-jet Gram candidates.
3. Recover the frozen Gram matrices from the recorded norms, dot products and common-coordinate vectors by a checked overdetermined linear inverse problem. Independent ε=1e-5 rows and eigenvalues from the parent report validate the reconstructed matrices. **The inverse system is ill-conditioned; no kinetic metric is inferred.**
4. Introduce a known artificial rotating chart and a non-orthogonal shear chart. A gauge covariant derivative corrects the apparent derivative changes; all inner products are invariant under simultaneous metric pullback and correct connection.
5. Construct a local response-locked co-rotating frame using an antisymmetric connection. It removes the resultant transverse rate **by construction**, not as proof of a physical rotation.
6. Exhibit a deliberately engineered positive-definite *negative-control* metric where the derivative angle becomes acute. This prevents the invalid assertion of universal metric independence.

## Artifacts

- `results/observer_velocity_angle_summary.csv` — stationary-point velocity-angle ledger.
- `results/moving_gauge_controls.csv` — chart gauge sweep and covariant correction.
- `results/co_moving_phase_ledger.csv` — 2,052 time-point local-frame ledger.
- `results/recovered_metric_validation.csv` — holdout residuals and reconstruction conditioning.
- `results/report.json` — counts, criteria, source SHA and limitations.
- Three PNG plots, reporting scientific diagnostics and controls.
- `SOURCE_MANIFEST.json` — pinned immutable source hashes.
- `SHA256SUMS_OUTPUT.json` — hashes of the *current* regenerated result files, separate from source integrity.

See `SCIENTIFIC_REPORT.md` and `SCIENTIFIC_DECISION_RULES.md`.
