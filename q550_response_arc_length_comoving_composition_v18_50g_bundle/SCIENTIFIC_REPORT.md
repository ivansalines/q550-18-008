# Q550 v18.50g — Response Arc-Length & Co-Moving Composition Audit

**Scientific status:** `SAMPLED_RESPONSE_ARC_DIAGNOSTIC_NOT_CONTINUOUS_ARCLENGTH_OR_PHYSICAL_MEMORY_CERTIFICATE`

## Authentic source and reproduction

The exact v18.50f server sendback SHA-256 is `d17d1284fe5ab2db018295307a8e0c283490f3a7c40d5fb2fd87149465760b69`. Its manifest verifies **22** entries, with embedded v18.50e verified over **20** entries. This audit independently re-opens the original v18.50e 4-vectors and crosschecks the v18.50f algebraic output. All **100** source observations are recovered; 20 cases × 5 horizons. No additional physical Q550 ODE/tangent integration is performed.

## What the arc represents

Let the four-component sensitivity vector in the inherited declared metric-whitened coordinates be `R(tau)=L(tau)+T(tau)`; the originally observed perturbed response is checked separately against this identity. With only five available measured horizons, define the **sampled polyline length**

`ell_5 = sum(i=0..3) ||R(tau[i+1])-R(tau[i])||`.

This is a lower bound for the continuous arc length of any rectifiable response curve passing through the samples in their order, **not** a continuous computed integral, a physical distance, or a clock. The normalized sampled progress is `s_i=ell_i/ell_5`. A sparser 3-point length and 2-point chord are controls, not refinement estimates of the actual continuous curve.

## Reference case: same seed, original kappa, cubic ramp r=0.24

- Measured five-point length: **17.99232710**.
- Three-point length (horizons 0, 0.025, 0.05): **17.97686569**.
- Endpoint displacement length: **17.91556460**.
- Ratio endpoint chord / 5-point path: **0.99573360**. The path is nearly straight in this chosen 4D chart; its deviation is measurable but small.
- Maximum discrete turning between neighboring segment chords: **5.061858 degrees**.
- The 3-point polyline underestimates the five-point measurement by **0.08593%**. This is an observed sampling effect, not a bound on the *remaining* error relative to a continuous curve.

### Endpoint cancellation versus sampled progress

| Evolution horizon Δξ | Sampled progress s | Response gain | Cancellation fraction |
|---:|---:|---:|---:|
| 0.0000 | 0.00000 | 0.32118 | 0.000% |
| 0.0125 | 0.21998 | 3.76101 | 14.508% |
| 0.0250 | 0.46077 | 8.08042 | 8.717% |
| 0.0375 | 0.72121 | 12.74149 | 6.649% |
| 0.0500 | 1.00000 | 17.71237 | 5.579% |

The cancellation fraction rises from zero when `T=0` to a maximum among these sampled points at `tau=0.0125`, then falls toward the endpoint, while `||R||` continues to increase. Neither the time nor arc position of a genuine continuous maximum can be certified from this sparse grid.

### Co-moving chord-frame composition

At each segment, define `u_i = ΔR_i/||ΔR_i||`. The signed advances satisfy the exact identity `⟨ΔL_i,u_i⟩+⟨ΔT_i,u_i⟩=||ΔR_i||`. In the reference case:

| Horizon interval | Local signed advance | Transported signed advance | Resultant chord | Segment-cancellation fraction |
|---|---:|---:|---:|---:|
| 0.0000–0.0125 | -0.06319 | 4.02117 | 3.95798 | 3.196% |
| 0.0125–0.0250 | -0.06647 | 4.39888 | 4.33241 | 3.072% |
| 0.0250–0.0375 | -0.06914 | 4.75503 | 4.68589 | 2.957% |
| 0.0375–0.0500 | -0.07128 | 5.08733 | 5.01605 | 2.852% |

Here the signed local advance is negative in every **sampled segment** whereas the transported advance is positive and larger. This is an incremental vector ledger. It does **not** imply a local force, a universal monotonic sign between measured points, or an independently causal decomposition.

## Cross-case findings and metric sensitivity

Across all 20 cases in the inherited metric, sampled arc lengths range from **16.719095 to 19.657203**. Three-point underestimation of five-point length ranges from **0.0442% to 0.1958%**; endpoint-chord straightness ranges from **0.990452 to 0.997835**.

An intentionally different diagonal metric changes the reference sampled arc from **17.992327** to **24.816500**. This is *sensitivity to the measuring metric*, not a physical increase in travelled distance.

The maximum source-vector Gram mismatch is **3.553e-15**; the maximum disagreement between the parent independently observed sensitivity vector and the reconstructed `L+T` is **3.593e-05** in the parent metric chart. These match the expected finite-difference tolerance scale.

## What this audit cannot resolve

- Five observed horizons **do not** determine continuous turning rates, path curvature or total response arc length. They provide a polygonal lower bound and sample-level turning angles only.
- Response path almost straightness and cancellation are properties of the inherited metric-whitened chart. They are not spatial geometry of a body.
- Relative monotonicity in the sampled intervals is not proof of monotonicity between samples.
- No additional Q550 IVPs, perturbations, material memory, phase/volume realization, or independent physical causal certificate arise from this postprocessing.

**Most appropriate next test:** replay the authenticated RHS with densified *physically integrated horizon points*, compare `ell_N` as N increases (e.g., 5, 9, 17, 33), and only then search for a robust local change of tangent direction; retain the common chart and a separate metric stress test.
