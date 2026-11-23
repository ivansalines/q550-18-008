# Q550 v18.50a — Equal-Projection Oriented Passage & Transport-Law Audit

The v18.49x sendback identifies 34 dynamically solved pairs with equal projected x across a turning point. This v18.50a replays the **authentic 11D physical Q550 equations** and integrates two signed phase-plane passage areas `(x,θ1)` and `(x,θ2)` across the event-defined interval. It checks (i) opposite branch velocities; (ii) rate-integral consistency; (iii) quadrature refinement; and (iv) the gauge-invariant triad 6–7–8 projector gap from a common kinetic frame against v18.49x.

The apparent closure of the x-projection is **not** a full spatial/state closure. The sign of a 2D area depends on coordinate orientation; it is not an intrinsic chirality or a material memory certificate. No identification of the optional 4/8 quadrant lens is made.

## Use on server

From `/root/elab1/hysteresis`, extract this ZIP into the single named root and run:

```bash
unzip q550_equal_projection_oriented_passage_transport_law_v18_50a_bundle.zip
cd q550_equal_projection_oriented_passage_transport_law_v18_50a_bundle
bash run_on_server.sh 2>&1 | tee v18_50a_server.log
```

Optional fast validation: `bash run_on_server.sh --smoke`. Parameter examples:

```bash
bash run_on_server.sh --kind original --ramps 0.24 0.327375
bash run_on_server.sh --quad-points 257 --max-area-refinement-error 5e-9
```

The `inputs/` directory contains the exact authenticated **v18.49x server ZIP** (all executable lineage retained) and hash pins. Scripts and outputs stay together, and `sendback.zip` is generated with full descriptive root and internal SHA-256 manifest. `scripts/verify_parent_x.py` verifies all upstream member hashes before running the solver. Source code/docs are in English; diagnostics are in the model evolution coordinate ξ, not calibrated physical time.

## Main outputs

- `results/oriented_equal_projection_passages.csv` — signed areas, angular transport, real x crossing signs, spectral projector comparisons, numerical checks.
- `results/case_summary.csv` — per-ramp success and sign trends.
- `results/selected_passage_trace.csv` — sampled geometry of selected actual passages.
- `results/report.json`, `SCIENTIFIC_REPORT.md`, plots and `results/environment.json`.
- `SHA256SUMS_OUTPUT.json` and complete `sendback.zip`.
