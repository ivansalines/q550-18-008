# Q550 v18.50m — Resultant Advance Intensity & Orientation-Rate Ledger

This audit measures how rapidly the **four-dimensional Q550 response vector** changes between norm parity and maximum cancellation, using the **authenticated v18.50l server sendback**. It requires no extracted ancestral runtime and performs **zero new ODE integrations**.

## Reproduce on the server

```bash
cd /root/elab1/hysteresis
unzip q550_resultant_advance_intensity_orientation_rate_v18_50m_bundle.zip
cd q550_resultant_advance_intensity_orientation_rate_v18_50m_bundle
PYTHON_BIN=python3.13 bash run_on_server.sh 2>&1 | tee ../v18_50m_server.log
```

The runner authenticates all 11 immutable source and seven output hashes **inside** the enclosed v18.50l sendback, checks the mathematical decomposition, regenerates the result ledgers and plots, checks its own immutable sources, writes a separate per-run output manifest, and produces a light self-contained `..._server_sendback.zip` in the parent directory. It never expands the 49 ancestral ZIPs into `runtime/`.

## Where to look

- `results/intensity_gate_summary.csv`: 4 precise event-to-event speed and turning measurements (two κ₀ families × two intervention amplitudes).
- `results/intensity_phase_ledger.csv`: 2052 timestamped observer-response rate samples in the inherited common reference normalization.
- `results/metric_same_anchor_rates.csv`: 16 comparisons of the derivative of the response **norm** at exactly the same event times in four declared metrics. Events in alternative metrics are not redefined.
- `results/report.json`: classification, checks, complete primary cases, parent digest.
- Three plots in `results/`: total/radial/transverse speeds, turning and metric sensitivity.
- `SCIENTIFIC_REPORT.md` and `SCIENTIFIC_DECISION_RULES.md`: interpretation and evidence thresholds.

## Provenance and packaging

A single ZIP under `inputs/` contains the *exact* authenticated v18.50l server result. The SHA-256 source manifest fixes the genealogy without unpacking the nested ancestors. The per-execution output manifest is independent so that Matplotlib metadata cannot falsely imply source drift. The command log is outside the immutable bundle and is not counted in any source hash.

## Definition

In the fixed inherited *common_parent_c* Euclidean chart, write `R(ξ)=L(ξ)+T(ξ)`, `rhat=R/||R||`, `V=dR/dξ`. We report `speed=||V||`, `radial=V·rhat=d||R||/dξ`, `transverse=||V−radial*rhat||`. The squared-rate identity holds pointwise. Curve derivatives are cubic-spline estimates from densely sampled v18.50l **integrated response vectors**. The transverse fraction is a fraction of speed *magnitudes*, not of energy.

The term *advance intensity* here means numerical sensitivity-response speed per unit model evolution coordinate `ξ`: **not energy, mechanical stress, plastic flow rate, laboratory time or physical velocity**.
