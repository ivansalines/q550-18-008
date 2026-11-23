# Q550 v18.50o — Dynamical Connection & Material-Metric Attribution Audit

## Executive scientific statement

**Yes, an observer-space transport *candidate* can be derived from the original Q550 dynamic vector field without fitting it to the response resultant. No, the available measurements do not select a unique, numerically stable material or kinetic connection.** The candidate exhibits strong rank and metric sensitivity, and the observed 4D response does not close well under the projected 10D linearized generator.

The audit authenticates the **v18.50n → v18.50m → v18.50l server genealogy** (source counts 12/11/11 and output counts 8/7/7), reconstructs the original nonautonomous 10D Q550 RHS, and performs **two new independent short driven-clock 10D IVPs plus two authentic natural-turning state replays**. A temporary historical runtime (up to ≈1.5 GB on some systems) is automatically removed after the model calculations; it is never included in the 50o bundle or sendback.

## Why the old response data are insufficient

At the inherited cancellation-stationary sections, the two four-vectors `L,T` have rank **2** in a four-dimensional output space for each κ₀. Knowing the action of a generic 4×4 linear map on those two vectors leaves at least **8** matrix coefficients unconstrained. Selecting the observer-locked connection from `R=L+T` could trivially produce a desired angular behavior; it would not answer the dynamical-source question.

## Derivation from the model, not the response

Let `z∈R¹⁰` follow the authentic driven-clock field `z'=f(z,ξ)`, and `u'=J u` its variational dynamics, where `J=∂f/∂z`. Let `D(z,ξ)∈R⁴` be the pre-existing structural-jet sensitivity observable and `B=∂D/∂z`, both computed on the **unperturbed physical state**. Then for `Y=B u`:

\[
Y'=(B'+BJ)u,
\quad K=(B'+BJ)B^{\sharp},
\quad E=(B'+BJ)(I-B^{\sharp}B),
\quad Y'=KY+Eu.
\]

`Bsharp` is a declared truncated SVD right inverse in the seed-scaled state chart. The residual `E` is **not forced to zero**. Its measured Frobenius fraction stays approximately **0.2747–0.2753**, across the chosen events and thresholds, including the full-row-rank case. This means that around **27.5% of the source operator's Frobenius norm lies outside the retained projected rule** under this normalization. It is *not* a fraction of mechanical energy.

The response closure diagnostic `||R'−KR||/max(||R'||,||KR||)` is approximately **0.904–0.908**, so the 4D source-only `K` is **not** a good autonomous evolution law for this response in the tested chart. This is a negative result against unqualified claims of independent 4D closure, not a failure of the authentic 10D model.

## Time-dependent metric and candidate connection

For observer regularizations `α∈{0.1,1}`, define

\[
W_\alpha(\xi)\propto\bigl(BB^{T}+\alpha\operatorname{tr}(BB^{T})I/4\bigr)^{-1},\qquad
\operatorname{tr}W_\alpha=4.
\]

Compute the source-driven output generator `K` and its metric skew part `Ω_W=(K−W⁻¹KᵀW)/2`. The candidate connection is

\[
\Gamma=\frac12W^{-1}W'-\Omega_W,\qquad D_\xi v=v'+\Gamma v.
\]

It satisfies the expected metric compatibility identity `ΓᵀW+WΓ=W'` to a maximum relative numerical residual of **1.84×10⁻¹⁰**. This consistency identity is necessary for the chosen convention; it is *not* proof of a physically privileged metric.

## The near-null observer direction is decisive

At the reference cancellation-stationary section (κ₀=1/6), the four output-Jacobian singular values are approximately

`[318.54, 1.25, 0.49, 3.01×10⁻⁶]`.

The full-row-rank condition number is about **1.06×10⁸**. Retaining or truncating that weak fourth output direction changes the projected connection drastically.

| Observer candidate | Truncated to rank 3 (SVD rcond 10⁻⁶) | Retaining rank 4 (rcond 10⁻¹⁰) |
|---|---:|---:|
| Gram, α=0.1 | **152.2608°** | **179.9219°** |
| Gram, α=1 | **127.6385°** | **179.9730°** |

These are angles between `DξL` and `DξT` at the **same inherited cancellation-stationary event**, not angles between the underlying 10D physical velocities or stresses. With full rank, the source spin norm reaches the order of **4×10⁶** in the chosen chart, compared with around **4.5×10²** for rank 3. This reveals numerical leverage, not a certified physical torsional flip.

On increasing the finite-difference radii from 10⁻⁶ to 2×10⁻⁶, the rank-3 corrected angles change by less than approximately `6.2×10⁻⁵°` in the original α=0.1 case, while rank-4 angles change by about **0.234°** (α=0.1) or **0.081°** (α=1). The weak mode is therefore noticeably less stable under the tested metrology.

Both κ₀ families show very similar results when treated with their **separately prepared** natural-turning states: agreement across branches is a numerical pattern, not evidence of common-state physical material memory.

## Decision

The independent model-driven construction exists and passes its algebraic compatibility tests. But its observable-space orientation is **not uniquely or robustly determined** by the data, because of (i) unobservable 10D complement coupling, (ii) dependence on the model-jet Gram weights, (iii) nearly singular output direction, and (iv) the absence of a model-derived physical kinetic tensor selecting the metric and the transport.

**Classification:** `MODEL_RHS_DERIVED_CANDIDATE_CONNECTION_NOT_UNIQUE_PHYSICAL_MATERIAL_TRANSPORT`.

### Next discriminating step

Rather than optimizing a 4D angle toward 180°, investigate the **10D tangent transport and the weak observer singular direction together**, then derive or identify an independently justified kinetic/symplectic form if the model supplies one. A meaningful material connection must retain the hidden-complement information or bound its effect, and must pass rechart and finite-step tests without using the response to fit the connection.

## Scientific limitations

- No experimentally identified polymer, metallic-glass, PMMA, or polycarbonate constitutive law follows from this comparison.
- The 4D metric is regularized *model observer* geometry, not proven material kinetic energy.
- The sampled roots from v18.50l are inherited numerical estimates, not interval-certified continuous events.
- Source Jacobians are finite differences in a declared chart; reported angular metrics are observer sensitive.
- Numerical source attribution does not independently demonstrate physical memory or torsion.
