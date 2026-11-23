# Q550 v18.50f — Scientific Report

**Classification:** `VERIFIED_V18_50E_VECTOR_LEDGER_POSTPROCESSING_NOT_INDEPENDENT_CAUSAL_OR_MATERIAL_CERTIFICATE`

## Source and audit scope

Immutable authenticated v18.50e server sendback: 20/20 hash checks, ZIP SHA-256 `21d9f910c14148746853bd211c873a77ae965ec8cf386baff2ec2b8f0cdb8a2f`. Reused 100 measurement rows, 20 cases, 5 horizons each. **No new physical ODE integrations were performed** in v18.50f.

## Structural observation

The response is represented in the fixed metric-whitened 4D chart by **R=L+T**. The local L and transported T terms can be counter-aligned; their norms must not be added as scalars. The cancellation fraction is `(||L||+||T||-||L+T||)/(||L||+||T||)` and is a conditional metric-dependent scalar, not physical dissipated energy.

At the original κ₀, cubic r=0.24, same-seed horizon 0.05:

- `||L||` = 0.57406923
- `||T||` = 18.18480360
- `||L+T||` = 17.71237211
- `cos(L,T)` = -0.82804652
- `angle(L,T)` = 145.89859°
- cancellation fraction = 5.578697%
- transport share of the sum of norms = 96.939746%

## Robustness and controls

- Nonzero-transport rows with negative scalar product: 80/80.
- Maximum IVP-vs-vector-split relative discrepancy: 1.866e-06 (parent finite perturbation and numerical derivative).
- Compare natural-turn and same-seed endpoint protocols in `results/endpoint_protocol_contrasts.csv`.
- Compare angle and cancellation *separately*: a more negative cosine need not mean a larger fraction of the response is cancelled, because L and T have very different magnitudes.

## Interpretation boundary

A structured, non-additive vector composition is numerically resolved. It is **not** yet a new independent physical law, nor a demonstration of a constraint transition, volume, physical causality, or material memory. This audit is deliberately an algebraic analysis of authenticated prior integrations.
