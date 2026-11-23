# Scientific report — Q550 v18.50q

**Analytic Observer Jacobian & Nullspace Projector Transport Audit**

## Executive finding

The tiny fourth singular mode discovered in v18.50o and examined in v18.50p is explained **structurally** by the normalization of the four-component structural-jet observer. Its analytic Jacobian cannot have rank four. At 34 newly evaluated physical Q550 trajectory sections, independent of the two observed response vectors L and T, it has numerical rank three; the corresponding instantaneous kernel in the 10D state chart is seven dimensional.

A new 10D fundamental-matrix transport of the **entire seven-dimensional subspace** shows that it remains close to, but not exactly aligned with, the kernel recomputed at later sections. These observations do not establish an observer-independent material connection.

## 1. Exact Jacobian identity

Let `F(y;κ₀)∈R¹¹` denote the historic analytic structural jet, with `J=DF`, `H=D²F`. Keeping the drive/clock variable `y[10]` fixed, define

```
h4 = (F[2], F[6], (J F)[2], (J F)[6])
u  = diag(1/common_scale_4d) h4
d  = u / ||u||
```

The raw observer Jacobian with respect to the first ten state coordinates is

```
∂_k h4[0] = J[2,k]
∂_k h4[1] = J[6,k]
∂_k h4[2] = Σ_j H[2,j,k] F[j] + Σ_j J[2,j] J[j,k]
∂_k h4[3] = Σ_j H[6,j,k] F[j] + Σ_j J[6,j] J[j,k].
```

Applying the chain rule to the normalization,

\[
B=\frac{I_4-dd^T}{\|u\|}\operatorname{diag}(1/w)\frac{\partial h_4}{\partial y}\operatorname{diag}(1/s),
\]

where `s` denotes the declared seed chart scales and `w` the four observer scales. Thus

\[
d^T B=0,\quad \operatorname{rank}(B)\le 3
\]

**exactly**, provided `||u||>0`. This is an algebraic fact, not a claim about dynamics or a new conservation law. The numerical fourth singular value is a floating-point remainder.

## 2. Sampled rank of the analytic observer

| Measurement | Original κ₀=1/6 | Autonomous κ₀=7π/132 |
|---|---:|---:|
| Sampled sections | 17 | 17 |
| Sampled rank | 3 throughout | 3 throughout |
| Smallest `s3` | 0.48950273 | 0.48965086 |
| Largest analytic `s4` | bounded by 5.714×10⁻¹⁴ globally | bounded by 5.714×10⁻¹⁴ globally |
| Analytic vs Richardson relative error | at most 2.342×10⁻¹² | at most 2.235×10⁻¹² |

The normalized observer’s exact left-null direction is `d`; it is **not** itself the seven-dimensional right kernel in the 10D state. The latter is obtained from the rank-three row space.

## 3. Kernel-projector transport

Define `P_t=I−V_{3,t}V_{3,t}ᵀ`. The initial nullspace basis `N0∈R^(10×7)` is transported with the original model’s 10D tangent equation `Φ′=J10 Φ`, `Φ(t0)=I`. At each section, orthonormalize `Φ N0`, giving a transported basis `Qt` and projector `Q_t Q_tᵀ`, and compare with `P_t` by principal angles.

| Measurement | Original κ₀ | Autonomous κ₀ |
|---|---:|---:|
| Max principal angle (degrees) | 0.0021514896 | 0.0021505670 |
| Max transported kernel leakage `||B Q||F/||B||F` | 1.53636×10⁻⁵ | 1.53547×10⁻⁵ |
| Max projector Frobenius distance | 5.73538×10⁻⁵ | 5.73281×10⁻⁵ |
| Instantaneous kernel leakage (all sections) | ≤3.127×10⁻¹⁶ | ≤3.127×10⁻¹⁶ |

The compared interval spans approximately 9.7×10⁻⁶ in the evolutionary coordinate. The transported and instantaneous nullspace projectors are **very close**, but the numerical leakage is not zero. This is a diagnostic of projected-model transport, not a certified material memory or a proof of non-invariance at exact arithmetic.

## 4. Interpretation and limitations

- The rank-three observer structure is explained by unit normalization alone. It is not a discovery of a fourth physical constraint.
- Numerical rank three is established at the 34 sampled states. A continuous rank-three theorem would require a lower bound for `s3` across the entire interval.
- A seven-dimensional instantaneous kernel does not identify a unique material direction. It is chart- and metric-dependent as an **orthogonal projector**, even though the rank bound is structural.
- The 10D variational generator is still computed using finite differences of the authentic physical RHS. A self-contained analytic tangent generator or interval bound is a possible later refinement.
- Neither the geometric cancellation in L/T nor the stress overshoot analogy with polymers/glasses should be promoted to a physical identity.

**Classification:** `ANALYTIC_NORMALIZATION_RANK_BOUND_AND_NUMERICAL_10D_PROJECTOR_TRANSPORT_NOT_MATERIAL_CERTIFICATE`.

## 5. Provenance

One input archive is retained: the **authentic v18.50p server sendback**, verified against all 11 immutable source and 7 output hashes. The complete Q550 original solver is reconstructed only in a temporary working directory for the physical replay and omitted from the sendback. Generated outputs carry their own SHA-256 manifest.
