# Q550 — v18.50b — Equal-Projection Tangent Orientation & Fiber-Transport Audit

This reproducible continuation takes the **authenticated server sendback from v18.50a** as immutable ancestry. It numerically re-integrates the authentic Q550 physical 11D system and compares tangent directions at genuinely equal-x passages. It does not assign quadrant labels or make spatial/material claims.

## Run on server

```bash
cd /root/elab1/hysteresis
unzip q550_equal_projection_tangent_orientation_fiber_transport_v18_50b_bundle.zip
cd q550_equal_projection_tangent_orientation_fiber_transport_v18_50b_bundle
bash run_on_server.sh 2>&1 | tee v18_50b_server.log
```

Requires Python 3.13 (or compatible Python 3), NumPy, SciPy, Matplotlib. `Q550_PYTHON` overrides the interpreter. For a quick single ramp: `bash run_on_server.sh --smoke`. Other CLI parameters: `--kind`, `--ramps`, `--path-samples`, `--scale-samples`, `--trace-all-cases`, and tolerances shown in `python scripts/run_audit.py --help`.

## What is measured

- Endpoint tangents for x; (x,theta1); (x,theta2); five-dimensional chart (x,theta1,theta2,theta1_rate,theta2_rate); and ten-dimensional complete dynamical chart where latent x is replaced by the logistic physical x.
- Original model RHS and Jacobian provide exact local derivatives of the 5D reduced chart.
- Both native Euclidean and trajectory-span-scaled coordinate metrics are reported. This metric choice is explicit; no intrinsic angle is claimed.
- Hidden-coordinate tangent fraction, orientation evolution along each passage, and inherited common-frame triad projector gap.
- All original 34 parent equal-x pairs are targeted; `--smoke` examines the four original r=.24 cases.

The parent server archive, scripts, and recursive authenticated genealogy are embedded. After execution, `sendback.zip` includes all audit outputs, generators and hash manifest. The parent ZIP is **not** modified. See SCIENTIFIC_DECISION_RULES.md and SCIENTIFIC_REPORT.md.
