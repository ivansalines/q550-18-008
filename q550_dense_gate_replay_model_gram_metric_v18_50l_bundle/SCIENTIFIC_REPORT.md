# v18.50l — Dense-Gate Physical Replay & Model-Jet Gram Metric Audit

## Executive scientific statement

New Q550 model-RHS integrations on `Δξ ∈ [0.00104,0.00109]`, at 513 time observations in each branch, reproduce a **norm-parity-then-cancellation-maximum** sequence for the two κ₀ families under the inherited common observer normalization. This is a genuinely new short integration of the original *driven-clock 10D physical RHS* from authenticated 11D natural turning states. It is not just a spline recalculation of v18.50k.

The sequence is **not metric invariant**: neither raw coordinate normalization nor two frozen, regularized Jacobian-Gram observer metrics displays the pair of events *inside this narrow time window*. These controls have negative local–transport scalar products but strongly different norm ratios and cancellation magnitudes. No kinetic metric of the physical model has been independently derived.

## Main measurements

Natural-state replay: `ramp=0.24`, `shape=beta:2:2`, separate turning seed per κ₀; `epsilon=1e-4`, reference chart from v18.50c. Root positions are spline estimates *within dense-sample brackets*:

| Observation | Original κ₀=1/6 | Autonomous κ₀=7π/132 |
|---|---:|---:|
| Norm-parity estimated Δξ | 0.001059115922906 | 0.001058706819693 |
| Stationary-cancellation estimated Δξ | 0.001068839383366 | 0.001068417450905 |
| Separation Δξ | 9.72346046e-6 | 9.71063121e-6 |
| Relative angle at parity | 130.25038447° | 130.24122951° |
| Relative angle at stationary | 130.25541947° | 130.24625942° |
| Rate of resultant norm at stationary | +131.76721 | +131.86169 |
| Peak sampled cancellation | 57.93828766% | 57.93103981% |

The maximum difference of the new numerical stationary estimates from the original v18.50k spline values is `6.30265e-9` in model Δξ. This agreement is strong evidence for consistency of the *numerical protocol*, not a unique-root or material-law certificate.

### Metric counterfactuals

Reference original κ₀, epsilon 1e-4, narrow window:

| Observer metric | Highest sampled C in window | Parity/stationary events inside window? |
|---|---:|---|
| Inherited common v18.50c normalization | 57.9383% | Both, in that order |
| Raw coordinate normalization | 0.723% | Neither |
| Frozen model-jet inverse Gram (α=0.1) | 17.923% | Neither |
| Frozen model-jet inverse Gram (α=1.0) | 38.809% | Neither |

The candidate inverse-Gram metrics are **observer constructions**, not measured kinetic energy or a covariant physical metric. Their dependence on the chosen state chart and regularization is declared. The local/transport scalar product remained negative for the sampled data in the four metrics; its sign persistence alone does not imply an invariant physical cancellation magnitude.

### Solver and convergence checks

- 2 κ₀ families × (1 unperturbed plus 2 symmetric pairs at 2 epsilons) = **10** new short physical RHS IVPs, plus 2 natural-state setup trajectories.
- 2 κ₀ × 2 epsilons × 513 time points × 4 observer metrics = **8,208** vector measurements.
- The maximum relative mismatch between centered IVP response and local+transport linearized split is `2.49861e-9`.
- The sample spacing is `(0.00109−0.00104)/(513−1)=9.765625e-8`. Recorded event brackets are a single sample interval. The 129,257,513 sample checks reuse the **same integrations** and therefore are not independent ODE convergence tests. In particular stationary spline roots vary by several `e-9` across sample grids and epsilon values; a guaranteed continuous-root enclosure was not produced.
- Parent v18.50k immutable source (14 files) and execution output (7 files), nested v18.50j SHA pin, and v18.50i input members (18 files) are checked before the physical replay.

## Mathematical observer definition

Let `H(y)` denote the original four-component hidden structural jet and

`D(y) = unit(H(y) / common_scale_4d)`.

At each independently authenticated natural turning seed, form the fixed `B` matrix of finite differences `∂D/∂y_j` scaled by the declared input coordinate scale `max(1,|y_j|)` for `j=0..9`. With `A=B Bᵀ`, define

`W_α = (A + α tr(A) I / 4)^{-1}`, renormalized so `tr(W_α)/4=1`.

This SPD matrix weights two output response vectors by `⟨L,T⟩_W=LᵀWT`. The construction is a regularized model-jet observation geometry. No mechanical Lagrangian kinetic form, invariant pullback metric, or physical polymer constitutive tensor is assumed.

## Scientific classification

**`NEW_SHORT_MODEL_RHS_REPLAYS_DENSE_EVENT_BRACKETS_NOT_KINETIC_METRIC_OR_CERTIFIED_CONTINUOUS_ROOT`**

The observed delay between norm parity and cancellation stationarity **survives numerical reintegration in the inherited observer**. The numerical event sequence **does not survive arbitrary changes of metric within the same narrow window**. Thus what is established is a well-reproduced model-sensitivity sequence in a declared measurement chart, not a universal dynamical threshold. Any comparison with metallic glass, PMMA, polycarbonate, strain-softening or stress overshoot remains conceptual until a physically justified mapping of variables is demonstrated.
