"""Human-readable report from numerical artifacts."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
main=r['results']['reference_original_cubic_024_same_seed']
text=f"""# Q550 v18.50f — Scientific Report

**Classification:** `{r['classification']}`

## Source and audit scope

Immutable authenticated v18.50e server sendback: {r['ancestry']['verified_entries']}/{r['ancestry']['verified_entries']} hash checks, ZIP SHA-256 `{r['ancestry']['zip_sha256']}`. Reused {r['source']['parent_csv_rows']} measurement rows, {r['source']['case_count']} cases, 5 horizons each. **No new physical ODE integrations were performed** in v18.50f.

## Structural observation

The response is represented in the fixed metric-whitened 4D chart by **R=L+T**. The local L and transported T terms can be counter-aligned; their norms must not be added as scalars. The cancellation fraction is `(||L||+||T||-||L+T||)/(||L||+||T||)` and is a conditional metric-dependent scalar, not physical dissipated energy.

At the original κ₀, cubic r=0.24, same-seed horizon 0.05:

- `||L||` = {main['endpoint_local']:.8f}
- `||T||` = {main['endpoint_transported']:.8f}
- `||L+T||` = {main['endpoint_gain']:.8f}
- `cos(L,T)` = {main['alignment_cos']:.8f}
- `angle(L,T)` = {main['alignment_angle_deg']:.5f}°
- cancellation fraction = {main['cancellation_fraction']:.6%}
- transport share of the sum of norms = {main['transport_share']:.6%}

## Robustness and controls

- Nonzero-transport rows with negative scalar product: {r['results']['negative_local_transport_inner_products']}/{r['results']['eligible_nonzero_transport_rows']}.
- Maximum IVP-vs-vector-split relative discrepancy: {r['results']['max_IVP_vs_vector_split_relative_residual']:.3e} (parent finite perturbation and numerical derivative).
- Compare natural-turn and same-seed endpoint protocols in `results/endpoint_protocol_contrasts.csv`.
- Compare angle and cancellation *separately*: a more negative cosine need not mean a larger fraction of the response is cancelled, because L and T have very different magnitudes.

## Interpretation boundary

A structured, non-additive vector composition is numerically resolved. It is **not** yet a new independent physical law, nor a demonstration of a constraint transition, volume, physical causality, or material memory. This audit is deliberately an algebraic analysis of authenticated prior integrations.
"""
(ROOT/'SCIENTIFIC_REPORT.md').write_text(text)
