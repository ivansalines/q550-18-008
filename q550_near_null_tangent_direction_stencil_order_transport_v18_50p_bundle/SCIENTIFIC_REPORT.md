# Scientific report — Q550 v18.50p

**Near-Null 10D Tangent Direction & Stencil-Order Provenance Audit**

## Executive finding

An independent server sendback of v18.50o was authenticated (11 immutable sources and 7 output hashes). Its fourth singular value of the four-dimensional structural-jet observer Jacobian `B∈R^(4×10)` increases by a factor **3.9999128–4.0001545** when the centered-finite-difference step doubles from `1e-6` to `2e-6` across both κ₀ branches and three evolutionary sections per branch. This is a strong `O(h²)` fingerprint of the derivative stencil, not evidence of a physically stable fourth mode.

A new replay of the original Q550 model, independent of response-vector fitting, evaluated **five centered-difference steps** and **four Richardson-corrected combinations** over 17 sections for each of the two κ₀ branches (306 SVD evaluations and 34 10D tangent-direction transport observations).

For the centered stencil at `h=1e-6`, `s4≈3.01e-6`. After fourth-order Richardson extrapolation at the same nominal half-step, it falls to approximately `4.7e-11–2.0e-10` (original) and `5.8e-11–1.7e-10` (autonomous). This is an improvement of roughly **15,000–65,000×** in the original branch at that step. The corrected fourth singular vector is poorly determined: its sign-free cosine with the centered-difference vector varies from **0.0069 to 0.7507** (original) and **0.0178 to 0.5919** (autonomous).

**Decision:** The high-rank pseudoinverse effects of v18.50o, including angles approaching 180°, should be treated as **stencil-sensitive numerical artifacts or unresolved conditioning**, not certified material transport. An analytical/autodifferentiated Jacobian is needed to establish the exact rank of the structural observer map.

## 1. Parent evidence

| Branch | Sections | s4(2e−6)/s4(1e−6) |
|---|---|---|
| Original | parity, midpoint, stationary | approximately 4.000000, 4.000054, 3.999913 |
| Autonomous | parity, midpoint, stationary | approximately 4.000049, 4.000154, 3.999989 |

The weak singular value also satisfies `s4/s1≈9.45e-9` at `h=1e-6`, while the leading singular value is approximately 318.5.

## 2. New 10D replay and stencil-order test

- Original and autonomous κ₀ values: `1/6` and `0.16659961041764054`.
- Natural 10D trajectories independently reconstructed from inherited Q550 natural turning states and nonautonomous physical RHS (one natural seed replay and one 10D driven IVP per branch).
- The Jacobian `B=∂D/∂z` is sampled at 17 positions spanning parity to the stationary cancellation event; the observable is the inherited four-component structural jet.
- Centered 2nd-order stencil `B₂(h)` at five steps `2.5e−7, 5e−7, 1e−6, 2e−6, 4e−6`.
- Corrected 4th-order stencil `B₄(h/2)=[4B₂(h/2)−B₂(h)]/3` at four step-pairs.
- 10D diagnostic variational equation `q′=J₁₀q` is integrated from the local weakest numerical right singular direction at parity, then compared to local weak singular vectors in a **declared seed-normalized chart**.

The centered `s4` spans `~1.88e−7` to `~4.82e−5` as the step varies; corrected `s4` spans `~3.20e−11` to `~7.97e−10` in the complete scan. A tiny rank-four signal from second-order differences should not be used as a physical mode identifier.

## 3. Interpretation of 10D transport

The sign-free overlap of the transported centered-stencil weak vector with the local centered-stencil weak vector remains above `0.999999997`. **This does not rescue a material-mode claim:** these vectors are derived from the same numerical stencil and chart, and the corresponding right singular vector becomes unstable when its `O(h²)` truncation component is removed. Even a small directional mismatch can create appreciable observer motion because `B` has a very large leading singular value.

A rank-three observer Jacobian would leave a **seven-dimensional kernel** in the 10D tangent space; a rank-four observer Jacobian would leave a six-dimensional kernel. Neither possibility selects a unique 10D null direction from the observer alone. The numerical fourth right singular vector should not be confused with a unique physical hidden mode.

## 4. Classification and next scientific gate

`NUMERICAL_WEAK_OBSERVER_MODE_UNDER_STENCIL_AUDIT_NOT_MATERIAL_DIRECTION_CERTIFICATE`

Before deriving a material metric or interpreting the near-180° angle, one needs at least an analytic or automatic-differentiation Jacobian for the structural jet, a rank certificate with controlled numerical/interval errors and, if a true null subspace remains, transport of the **subspace projector** rather than of a single arbitrarily chosen singular vector.

The polymer/metallic-glass discussion remains a conceptual analogy; no material constitutive identity has been demonstrated.

## 5. Reproducibility and provenance

The bundle includes original Python scripts, fast tests, exactly one hash-pinned authentic v18.50o sendback and the derived numerical artifacts. The complete historical solver lineage is reproduced transiently for a full replay and removed afterward. Immutable sources and regenerated outputs use separate manifests. No runtime genealogy is included in the sendback. Python 3.13 is recommended for historical `hashlib.file_digest` calls.
