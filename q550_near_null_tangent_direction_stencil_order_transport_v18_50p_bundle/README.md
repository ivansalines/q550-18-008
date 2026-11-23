# Q550 v18.50p — Near-Null 10D Tangent Direction & Stencil-Order Provenance Audit

## Purpose

Investigate the **weakest singular direction of the 4×10 structural observer Jacobian** seen in v18.50o. This is first a numerical-rank question, not yet a certified hidden physical mode. The authenticated v18.50o server sendback is the only included parent; its full historical Q550 solver ancestry is intact inside that ZIP, but is unpacked only into a temporary directory for the optional full run.

The observed fourth singular value in v18.50o scales almost exactly by four when the centered-difference step doubles. v18.50p tests whether the weak singular value persists under a finer stencil grid and Richardson fourth-order extrapolation, and only then studies how the corresponding right singular vector is transported under the authentic Q550 10D variational generator.

## Server execution (Python 3.13)

```bash
cd /root/elab1/hysteresis
unzip q550_near_null_tangent_direction_stencil_order_transport_v18_50p_bundle.zip
cd q550_near_null_tangent_direction_stencil_order_transport_v18_50p_bundle

PYTHON_BIN=python3.13 bash run_on_server.sh \
  2>&1 | tee ../v18_50p_server.log
```

The original ZIP is immutable. A separate **output manifest** permits legitimate Matplotlib metadata changes, and the generated server sendback excludes all temporary historical expansions. The temporary solver expansion may require ~1.4 GB of disk while active but is automatically removed when the audit finishes.

For a **fast authenticated numerical preflight without integration**:

```bash
python3.13 scripts/verify_source_manifest.py
python3.13 tests/test_stencil_scaling.py
python3.13 scripts/run_audit.py --preflight-only
```

Do **not** run the preflight through `run_on_server.sh` if you want to preserve a previously completed full-run result manifest; that launcher always regenerates output manifests and sendback archives.

## Mathematical protocol

- In the inherited normalized 10D state chart, let `B=∂D/∂z` where the 4D observable is the same structural-jet observer as v18.50o.
- At 17 positions between the inherited parity and stationary sections, for both κ₀ families, estimate `B` using centered differences with `h∈{2.5e−7,5e−7,1e−6,2e−6,4e−6}`.
- Construct Richardson differences `B₄(h/2)=[4B₂(h/2)−B₂(h)]/3`; compare `s₄(B₂)` and `s₄(B₄)` and their right singular directions.
- Evolve one *diagnostic* unit vector from the initial weak right singular vector under `q′=J₁₀(t)q` along the independently reconstructed natural 10D trajectory; compare its **sign-free** orientation against local weakest singular vectors and the strong rank-three projector.
- All angles and norms are chart-dependent. If the weak singular value collapses as `O(h²)`, the appropriate interpretation may be numerical rank three; do not infer a material near-null mode.

## Contents

`inputs/` contains the hash-pinned authentic v18.50o server sendback (~55 MB).

`scripts/run_audit.py` is the executable analysis and physical replayer. `tests/test_stencil_scaling.py` checks source authentication and stencil algebra. `results/historical_stencil_scaling.csv` records six directly verified historical comparisons, `results/ten_d_stencil_singular_spectrum.csv` records the new 10D Jacobian results, and `results/weak_direction_tangent_transport.csv` records the transported direction. `results/report.json` declares limitations and the exact software environment. PNGs are diagnostic visualizations, not independent evidence.

`SOURCE_MANIFEST.json` describes immutable inputs/source SHA-256. `SHA256SUMS_OUTPUT.json` describes the outputs actually generated on each machine; their PNG bytes may differ without changing the underlying numerical data.

## Interpretive restriction

Neither a small singular value nor the right singular vector of a finite-difference Jacobian certifies a kinetic/material mode, a physical nullspace, a unique connection, a polymer constitutive mechanism or a material-memory law. In particular, singular vectors corresponding to a rank-deficient operator are generally nonunique and can vary with chart, numerical stencil and gauge choice.
