# Q550 v18.50o — Dynamical Connection & Material-Metric Attribution Audit

## Scientific question

Can the Q550 model provide a rule of transport derived **before** observing the local/transport response pair `L,T`, rather than a frame fitted to the resultant `R=L+T`?

The audit reconstructs the **original nonautonomous 10D model RHS** and the four-component structural-jet observable from the authenticated `v18.50n → m → l` genealogy. It derives a **candidate** connection from the model RHS Jacobian and the observer Jacobian along unperturbed natural trajectories. It does not assume this candidate is a material kinetic connection.

## Execution (Python 3.13 recommended)

```bash
cd /root/elab1/hysteresis
unzip q550_dynamical_connection_material_metric_attribution_v18_50o_bundle.zip
cd q550_dynamical_connection_material_metric_attribution_v18_50o_bundle

PYTHON_BIN=python3.13 bash run_on_server.sh 2>&1 | tee ../v18_50o_server.log
```

The automatically generated sendback is created alongside the bundle directory:
`q550_dynamical_connection_material_metric_attribution_v18_50o_bundle_server_sendback.zip`.

For a fast, no-integration source/probe check:

```bash
python3.13 scripts/run_audit.py --preflight-only
```

The full execution stages the historical solver temporarily, executes two natural-turning seed replays and two independent short driven-clock 10D IVPs, samples model Jacobians, and then **deletes the temporary historical `runtime`**. The transient expansion may require approximately 1.4 GB of disk, but it is not included in the sendback. Do not modify `run_on_server.sh` merely to select Python: use `PYTHON_BIN=python3.13`.

## What is calculated

Let `z∈R^10`, `dz/dξ=f(z,ξ)` be the authentic Q550 driven-clock dynamics, `J=∂f/∂z` the Jacobian in the declared seed-scaled chart, `D(z,ξ)∈R^4` the inherited structural-jet observer, and `B=∂D/∂z` its Jacobian. The output perturbation is `Y=B u` for a tangent perturbation `u` of the full state. Consequently:

```text
u' = J u
Y' = (B' + B J) u
K = (B' + B J) Bsharp
E = (B' + B J) (I - Bsharp B)
Y' = K Y + E u
```

Here `Bsharp` is a truncated-SVD right inverse. `E` explicitly reveals any hidden complement not determined by `Y` alone. This relation is a **projected diagnostic**, not necessarily a closed 4D dynamics.

For each alpha in {0.1,1}, define the *declared observer* metric

```text
W = normalize_trace_4[ (B B^T + alpha tr(B B^T) I / 4)^(-1) ]
Omega_W = (K - W^(-1) K^T W) / 2
Gamma = W^(-1) W' / 2 - Omega_W
D_xi v = v' + Gamma v
Gamma^T W + W Gamma = W'
```

`Gamma` is computed without using the response vectors. **The output Gram metric is not a kinetic metric derived from a Q550 Lagrangian, and the connection is not unique.** Its dependence on alpha, tangent rank threshold, observable, and chart is explicitly measured.

## Outputs

- `results/identifiability_preflight.csv` — proof that two measured response vectors cannot determine an arbitrary 4D connection.
- `results/dynamical_connection_ledger.csv` — 48 measurements, two κ₀, three event sections, two difference step sizes, two Gram weights, and two SVD thresholds.
- `results/dynamical_event_sections.csv` — original natural-state source events.
- `results/model_source_connection_angles.png` — frozen-metric velocity opposition against source-derived connection-corrected opposition.
- `results/observer_projection_leakage.png` — leakage through unobserved tangent directions.
- `results/report.json` — full method, authentication, environment, limitations, and metrics.
- `SOURCE_MANIFEST.json` — immutable input/code SHA-256.
- `SHA256SUMS_OUTPUT.json` — separate hashes of the actual generated results.

## Numerical cautions

- All angles are in a **four-dimensional sensitivity-observer space**, per evolution offset `Δξ`; no stress, energy, spatial torsion, or physical kinetic metric is identified.
- The SVD spectrum is extremely anisotropic. A rank-truncation choice can radically change the derived connection. Report both retained rank and leakage, not only a selected angle.
- Finite differences and interpolated event positions are numerical diagnostics, not certified intervals or continuous root proofs.
- The polymer/metallic-glass comparison remains an analogy until a constitutive map is established.
- The temporary 1.4 GB runtime is deliberately not packed. Input archives remain hash-pinned.
