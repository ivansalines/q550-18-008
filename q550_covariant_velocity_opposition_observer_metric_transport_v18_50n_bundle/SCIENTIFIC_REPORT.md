# Q550 v18.50n — Covariant Velocity Opposition & Observer-Metric Transport Audit

## Question

Does the ~159.785° opposition of the local and transported response *velocities* persist when the observer or metric changes? Can a co-moving observer distinguish directional advance from its own rotation?

The four-vector data here are sensitivity observables derived from an authentic v18.50l short Q550 physical RHS replay, authenticated via the v18.50m server sendback. In this audit **zero** new RHS integrations were run. All rates are derivatives with respect to model evolution offset Δξ, not a laboratory-time speed or kinetic energy.

## Direct results at the inherited cancellation stationary event

Original κ₀=1/6; perturbation ε=10⁻⁴:

| Declared measurement | Angle between local and transported derivatives |
|---|---:|
| Inherited common normalized observer, fixed Euclidean metric | 159.78518° |
| Distinct raw nonlinear observable, fixed Euclidean metric | 124.14398° |
| Common observer with frozen model-jet Gram metric, regularization α=0.1 | 114.94748° |
| Common observer with frozen model-jet Gram metric, regularization α=1 | 140.80394° |
| Deliberately response-targeted positive-definite negative-control metric | 69.66084° |

The measured velocity opposition is obtuse in the four *predeclared* observers, but it is not invariant across them. The last row explicitly demonstrates that there is **no universal sign theorem for arbitrary SPD metrics**. It is not a physical candidate metric.

The Gram metrics were *frozen at the model's natural turning seed* in v18.50l. Their matrices were not saved, so this audit reconstructs them from redundant vector norms/dots with a linear inverse problem, validates eigenvalues against the v18.50l report and evaluates on an independent ε=10⁻⁵ holdout. The reconstruction design is very ill-conditioned, and nothing here identifies a mechanically privileged kinetic metric.

## Passive moving chart versus actual change in observer weighting

Let `x` denote the whitened four-vector in a fixed SPD metric, and let a known moving chart be `q(ξ)=O(ξ)x(ξ)` with orthogonal O. Its ordinary derivative includes chart rotation: `q′=O x′+O′ x`. A correctly transported derivative removes the known gauge term: `Dq=q′−O′ Oᵀ q = O x′`.

A test using a prescribed 300 rad/model-ξ chart rotation in the whitened (0,2) plane gives, at the original stationary event:

- Angle between *ordinary chart derivatives*: **77.48914°** (apparently acute).
- Angle between *connection-corrected derivatives*: **159.78518°**, exactly the inherited fixed-chart value to floating-point precision.

A nonorthogonal shear chart was tested with the simultaneously pulled-back metric `G_q=S⁻ᵀG S⁻¹` and its exact chart connection. The analytic inner-product identity was checked numerically. This **establishes algebraic covariance under a specified coordinate change**, not a discovered connection of the Q550 physical state space.

## Response-locked co-moving frame

For unit resultant direction `r=R/||R||` in whitened coordinates, choose the skew connection `Ω=r′rᵀ−rr′ᵀ`. It satisfies `Ωr=r′`. The moving-frame-relative derivative `v−Ωx` of each contribution therefore removes the resultant transverse velocity exactly by construction.

- Fixed-chart derivative angle: **159.78518°**.
- Response-locked, locally co-moving *uncorrected-relative* derivative angle: **172.86852°**.
- The geometrically covariant derivative in the moving chart (including the connection) restores the fixed-chart value **159.78518°**.

Both numbers have a specified meaning, but **they are different comparisons**. A frame rigidly following R is not uniquely specified without fixing its rotation in the orthogonal complement; our choice is locally rotation-minimizing. Calling 172.87° a universal material torsional angle would be incorrect.

## The scientific distinction

**Passive gauge change** with correctly carried metric and connection: the original velocity-angle information is preserved by mathematical construction.

**Change of metric** or of observable: numerical angle and even its acute/obtuse classification can change. A privileged physical connection or kinetic metric has not been derived.

Accordingly, the v18.50n result is an **authenticated observer-transport diagnostic**, not independent physical proof of hidden torsion, material memory, or constitutive equivalence with polymers or metallic glasses.

## Provenance and numerical limitations

- 8,208 parent v18.50l vector/metric rows; 2,052 common-chart horizon rows; 2 κ₀ families × 2 perturbation amplitudes.
- Both parent v18.50m and nested v18.50l server archives verified against their independent immutable source and regenerated output SHA-256 manifests.
- Velocity values are obtained by cubic spline derivatives from 513 actual RHS-generated response samples per κ₀/ε. There are no certified continuous derivative enclosures.
- Gram matrices reconstructed by scalar-pair constraints are numerically delicate; diagnostic holdout and eigen checks are included.
- Angles are in *four-dimensional sensitivity space* and per model Δξ, not spatial torsion, kinetic strain, stress or energy.

**Classification:** `AUTHENTICATED_POSTPROCESSING_PASSIVE_GAUGE_COVARIANCE_NOT_PHYSICAL_CONNECTION_OR_KINETIC_METRIC`.
