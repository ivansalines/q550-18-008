# v18.50b — Equal-Projection Tangent Orientation & Fiber-Transport Audit

**Classification:** `NUMERICAL_EQUAL_PROJECTION_TANGENT_AND_FIBER_DIAGNOSTIC_NOT_PHYSICAL_FIBER_BUNDLE_OR_MATERIAL_MEMORY_CERTIFICATE`

## Execution and provenance

- Genuine Q550 11D replay using the full authenticated v18.50a input archive and its v18.49x ancestry.
- Cases succeeded: **10**. Failed: **0**.
- Matched equal-x passages evaluated: **34** / 34.
- Maximum authenticated parent projection difference: 2.220446e-16.
- Opposing x crossing rate in all measured pairs: True.

## Direct result

The two passes through the same projected x have opposing **x-direction** tangents. Their full tangent vectors remain distinct in a five-coordinate state and in the ten-coordinate dynamical chart; the angle depends strongly on the chosen chart metric. Across tested pairs, the 5D span-scaled angle ranges **25.857571°–113.46009°**; its arithmetic mean is **72.128925°**. The same 5D directions using native coordinate scales range **4.6240354°–14.851001°**.

These are **not invariant physical rotation angles**. The contrast is itself a metric-sensitivity finding.

## Example authentic passage

- κ0 choice: **original**; ramp r=0.24; shape `beta:2:2`.
- First and second crossings ξ = 0.012, 0.17841186.
- Equal-x residual: 0.
- x tangent dot-sign: cosine -1, opposed by construction of two crossing branches.
- 5D tangent angle: **13.944062°** native / **94.836555°** span-scaled.
- 10D tangent angle: **28.589451°** native / **93.153217°** span-scaled.
- Span-scaled hidden-tangent shares: **0.78141044** incoming and **0.67355517** outgoing.
- Triad projector distance inherited from parent v18.50a: **0.37116186** (not newly integrated).

## A useful comparison with v18.50a

At the selected example the instantaneous θ2′/θ1′ ratio changes from **1.4406556** at entry to **1.8930747** at exit; the corresponding signed-area ratio reported by the authenticated parent is **1.6747795**. The near-uniform area ratio in v18.50a is therefore **not simply a fixed instantaneous angular-rate ratio**. It may still follow from the model's local equations and from the weighting used in the integral; no independent transport law is claimed.

Across all pairs, the instantaneous entry ratio ranges 1.4406552–1.598691, and the exit ratio ranges 1.742479–1.8932872.

## Geometry measured

For z=(x,θ1,θ2,θ1′,θ2′), the five-dimensional tangent is obtained from the 11D physical RHS and the directional Jacobian derivative JF. The derivatives are with respect to the model's evolution coordinate ξ, not physical laboratory time. The 10D chart substitutes the logistic x for its latent coordinate, applying its chain rule to the tangent.

Native Euclidean and per-case span-scaled Euclidean chart metrics are explicitly compared. The 'fiber' share means the length fraction of the four coordinates hidden when only x is projected; it is not a canonical Ehresmann connection, a global material fiber, or an intrinsic measure.

The path-turn sum is a finite-resolution sum of successive tangent-direction angles along the section; compare values after increasing `--path-samples` before treating it as numerically converged.

## Non-conclusions

1. Matching x is not matching the full radial locus or the full physical state.
2. A chart-dependent angle is not a laboratory-space body rotation or physically certified flip.
3. No discrete four/eight quadrants were assigned to Q550; the autonomous quadrant rule remains independent.
4. No closed physical return, physical holonomy, material memory, spatial volume or topology has been certified.
5. All pairs within an orbit share a dynamic history; there are not 34 independent experimental replicates.

## Files

`results/equal_projection_tangent_pairs.csv`, `results/case_summary.csv`, `results/tangent_trace_selected.csv`, `results/report.json`, `results/environment.json`, visualization PNGs, original Python scripts, unit tests, recursive authenticated parent ZIP, and SHA-256 manifests.
