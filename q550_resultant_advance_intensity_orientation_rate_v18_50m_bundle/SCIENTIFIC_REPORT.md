# v18.50m — Resultant Advance Intensity & Orientation-Rate Ledger

## Research question

The v18.50l physical replay found that equality of the local and transported response magnitudes precedes the maximum of their normalized cancellation. The result did not stop advancing at either event. **How much of the response's change is increase of magnitude, and how much is rotation of its four-dimensional direction?**

## New result in the inherited common observer

The numbers below are **per unit of the model evolution coordinate `Δξ`**, and are numerical response-sensitivity rates, not physical power or laboratory-time speeds. They are derived from the authentic server's 513-point dense response trajectory and its estimated event anchors.

| Quantity at cancellation stationary point | Original κ₀=1/6 | Autonomous κ₀=7π/132 |
|---|---:|---:|
| Vector speed `||dR/dξ||` | 303.995806 | 304.155244 |
| Rate of resultant magnitude `d||R||/dξ` | +131.770155 | +131.860931 |
| Transverse speed | 273.952690 | 274.085948 |
| Transverse fraction of speed | 90.1173% | 90.1138% |
| Speed of local contribution `||dL/dξ||` | 5.269810 | 5.271403 |
| Speed of transported contribution `||dT/dξ||` | 308.935562 | 309.096841 |
| Resultant four-vector angular turn parity→stationary | 0.556437° | 0.556242° |
| Relative L-to-T angular change parity→stationary | +0.005031° | +0.005030° |
| Resultant magnitude increase parity→stationary | 0.00126725 | 0.00126749 |
| Fractional increase of resultant magnitude | +0.4624% | +0.4623% |

These are **two distinct angles**. The larger is the change of the direction of the entire response four-vector. The smaller is the change in mutual orientation of the two components. The latter being tiny does **not** imply the full response direction barely moves. The transported contribution changes much faster than the local component in the inherited chart.

The same qualitative decomposition is present for `ε=10^-5`: original total-vector speed 304.003256, transverse 273.959507; autonomous 304.154324, transverse 274.085105. The postprocessing compares two perturbation amplitudes, not independent trajectories beyond the input v18.50l integration set.

### Rates and meaningful distinction

Writing `rhat=R/||R||`, the exact identity in a fixed Euclidean observer chart is:

`||dR/dξ||² = [d||R||/dξ]² + ||(I−rhat rhatᵀ)dR/dξ||²`.

At the primary original stationary point, `273.953/303.996≈0.901` is a fraction of the velocity magnitude. The corresponding squared transverse share is about `81.2%`; do **not** call the 90.1% an energy partition. The underlying response is a sensitivity vector and `ξ` is not calibrated laboratory time.

### Dependence on the observer metric

Holding the two **common-chart event times** fixed and changing the measurement metric, the original κ₀ rate of the *norm* at the same stationary time becomes:

| Metric | `d||R||/dξ` per model ξ |
|---|---:|
| Inherited common observer | +131.7702 |
| Raw coordinate observer | +0.4569 |
| Frozen regularized model-jet Gram (α=0.1) | +4.9782 |
| Frozen regularized model-jet Gram (α=1) | +32.6329 |

These rates are **not comparable as physical intensities without first deriving a physically privileged covariant metric**. The alternative observers do not generally have their own norm parity or stationary cancellation in this small window; their quoted times are deliberately the common-observer anchors.

## Evidence, method and limitations

- **Parent input:** v18.50l *actual server sendback*, containing new physical RHS integrations; all 11 source hashes and seven output hashes verified before processing. It is read in-place with `zipfile`; nested `runtime` is never generated.
- **New integration count:** zero. This audit is independent source-checked analysis of v18.50l's tabulated responses, not fresh dynamic confirmation.
- **Root source:** the same original Q550 10D driven-clock RHS as v18.50l, inherited but not reintegrated here.
- **Numerical method:** four independent cubic splines for `L` and `T` component histories, event anchors from parent brackets, Euclidean projection of the resulting derivative, endpoint angle and displacement, finite-difference derivative cross-check.
- **Sampling:** 513 samples per κ₀/ε trajectory, 2052 phase rows; no certified continuous enclosures.
- **Metric status:** inherited common observer is a declared normalized chart, not a physical kinetic metric; Gram candidates are frozen observer constructions, not physical metrics.
- **Interpretation:** the response advances with a strong *direction-changing component* in the declared four-dimensional observer. This does not establish a physical flip, hidden polymer analogue, geometric holonomy, or material memory law.

**Classification:** `AUTHENTICATED_PARENT_POSTPROCESSING_4D_OBSERVER_SPEED_NOT_PHYSICAL_KINETIC_INTENSITY`.
