# v18.50e — Common-Horizon Sensitivity & Accumulated Conditioning Audit

**Classification:** `COMMON_HORIZON_IN_MODEL_RESPONSE_DECOMPOSITION_NOT_PHYSICAL_CAUSAL_OR_REGIME_CERTIFICATE`

## Why this control is needed

The v18.50d gain grows along ramps but each natural turning state is different. This audit (A) keeps identical elapsed evolution horizons for each authentic natural turning, and (B) imposes identical initial 11D state, event time, initial clock phase, pooled 4D metric and elapsed horizon while changing the future commanded ramp. These are two different counterfactual comparisons.

## Measured result at Δξ = 0.05

| κ₀ | r | natural turning gain | common-seed gain |
|---|---:|---:|---:|
| original | 0.180000 | 16.494037 | 16.987768 |
| original | 0.240000 | 17.712350 | 17.712350 |
| original | 0.327375 | 18.599115 | 18.282900 |
| original | 0.500000 | 19.250341 | 18.730930 |
| autonomous | 0.180000 | 16.500356 | 16.993184 |
| autonomous | 0.240000 | 17.716725 | 17.716725 |
| autonomous | 0.327375 | 18.601704 | 18.286262 |
| autonomous | 0.500000 | 19.251408 | 18.733384 |

Cubic vs quintic, r=0.24:

| κ₀ | Protocol | Cubic gain | Quintic gain |
|---|---|---:|---:|
| original | natural_turn | 17.712350 | 17.961903 |
| original | same_seed | 17.712350 | 17.732029 |
| autonomous | natural_turn | 17.716725 | 17.965935 |
| autonomous | same_seed | 17.716725 | 17.736486 |

## Local-versus-transported linear response ledger

For each endpoint state y(t), let g(y) be the *normalized 4D hidden structural jet*. Under a symmetric perturbation of the x-logit state at the source event, δy(t) is the transported state tangent. The endpoint derivative is decomposed, in the stated coordinate chart, as

`Dg[y(t)] δy(t) = Dg[y(t)] e_x + Dg[y(t)] (δy(t) − e_x)`.

This is a **linearized endpoint-coordinate identity**, not proof that a physical direct cause and an independent memory mechanism can be separately intervened upon. Vector magnitudes do not add and partial cancellations are possible.

Example, original κ₀, cubic r=0.24, common seed:

| Δξ | total gain | frozen endpoint-x gain | accumulated component magnitude | cosine of components |
|---:|---:|---:|---:|---:|
| 0.0000 | 0.321184 | 0.321184 | 0.000000 | +0.00000 |
| 0.0125 | 3.761012 | 0.378045 | 4.021236 | -0.71307 |
| 0.0250 | 8.080423 | 0.440035 | 8.412006 | -0.76484 |
| 0.0375 | 12.741485 | 0.505738 | 13.143261 | -0.80152 |
| 0.0500 | 17.712350 | 0.574069 | 18.184804 | -0.82805 |

At the source event, the local direction response has gain 0.321184; by Δξ=0.05, the final response is 17.712350. The larger endpoint response involves state tangent transport, but its decomposition is chart-dependent.

## Verification

- Original 11D Q550 RHS and structural hidden jet reused from the byte-pinned v18.50d recursive lineage.
- Every short-run test uses a single fixed initial state and identical elapsed horizons for the same-seed comparison.
- No failures among 60 short IVPs; cases 10 natural + 10 same seed.
- Maximum relative difference between the IVP-centered directional response and the transported-tangent chain rule: 1.8664e-06.
- Maximum absolute linear split residual: 1.8111e-09.

## Scope / nonclaims

- The scalar gain depends on the chosen pooled metric and on normalization of the hidden four-jet.
- Source-kick amplitude is a mathematical perturbation in the logit chart, not an independently accessible physical actuator.
- The same-seed protocol holds the 11D initial state and initial clock phase fixed; different future ramp signs and phase excursions are deliberate counterfactual inputs.
- No discontinuity, bifurcation, physical memory, geometric 8-octant realization or spatial volume is established.
- Growth with duration may be smooth and depends on the specified horizon, metric, and source protocol.

## Files

`results/common_horizon_direction_responses.csv`, `results/report.json`, the four PNG figures, executable scripts and inherited pinned sendback with original Python solver.
