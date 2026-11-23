# v18.49x — X-Turning Clock & Equal-Projection Return Continuation Audit

## Status
`NUMERICAL_TURNING_CLOCK_AND_EQUAL_X_PROJECTION_NOT_PHYSICAL_CLOCK_OR_CLOSED_3D_LOCUS_CERTIFICATE`

## Authentic execution
- Reintegrated cases: **12**; failures: **0**.
- Sign-bracketed turning roots: **12**; exact equal-x projection pair roots: **34**.
- The same source physical Q550 11D model and 10D tangent kinetic-frame embedding are used, with upstream SHA-256 ancestry checked.
- Event times are *measured* for each trajectory rather than fixed to a common ξ or σ.

## Physical and projected observables

`x = logistic(y[8])` and `dx/dξ = x(1−x) * f[8]` for the original structural RHS. Zeros of the latter are bracketed and refined with Brent’s method.
The prescribed drive zero is a separate control event at σ=1/2 (for the symmetric profiles).
In an equal-projection pair, the later intersection is found by a second scalar root solve on the actual dense 11D solution; radial coordinates, angular posture, energy and spectral projectors are evaluated independently.

## Case events

| κ₀ | ramp r | shape | ξ turn | σ turn | ξturn − ξdrive | matches |
|---|---:|---|---:|---:|---:|---:|
| original | 0.120000 | `beta:2:2` | 0.089769725 | 0.748081041 | 0.029769725 | 0 |
| original | 0.180000 | `beta:2:2` | 0.090659349 | 0.503663048 | 0.000659349 | 3 |
| original | 0.240000 | `beta:2:2` | 0.091047626 | 0.379365109 | -0.028952374 | 4 |
| original | 0.327375 | `beta:2:2` | 0.091306709 | 0.278905563 | -0.072380791 | 4 |
| original | 0.500000 | `beta:2:2` | 0.091494724 | 0.182989448 | -0.158505276 | 2 |
| original | 0.240000 | `beta:3:3` | 0.091289273 | 0.380371970 | -0.028710727 | 4 |
| autonomous | 0.120000 | `beta:2:2` | 0.089746325 | 0.747886040 | 0.029746325 | 0 |
| autonomous | 0.180000 | `beta:2:2` | 0.090634930 | 0.503527387 | 0.000634930 | 3 |
| autonomous | 0.240000 | `beta:2:2` | 0.091022719 | 0.379261331 | -0.028977281 | 4 |
| autonomous | 0.327375 | `beta:2:2` | 0.091281461 | 0.278828442 | -0.072406039 | 4 |
| autonomous | 0.500000 | `beta:2:2` | 0.091469221 | 0.182938442 | -0.158530779 | 2 |
| autonomous | 0.240000 | `beta:3:3` | 0.091264115 | 0.380267147 | -0.028735885 | 4 |

## Nearness of turning and prescribed drive zero
The smallest absolute difference among sampled cases occurs at κ₀=autonomous, ramp=0.18, shape=beta:2:2: `Δξ=0.000634930`. This is neither a certified zero nor a universal clock.

## A genuine equal-projection pair (selected from solved roots)
- κ₀=original, r=0.18, shape=beta:2:2
- ξin=0.0180000000; ξout=0.1694015235; |Δx|=0.000e+00.
- Angular posture gap 0.2422771 rad; 3D span-normalized locus gap 1.1797451.
- Triad projector Frobenius gap 0.3376843; maximum principal angle 9.5167793 degrees.

## Numerical controls
- Original forward-history regression: `3.425e-13`.
- Max mechanical ledger error: `4.389e-12`.
- Max w endpoint regression: `0.000e+00`.
- Max event shift after doubling scan grid: `1.052e-13`.

## Interpretation constraints
- Time coordinates are model xi and ramp fraction sigma, not universal or empirically calibrated physical time.
- No universal turning clock is imposed; roots are recomputed for each genuine Q550 trajectory and ramp.
- An equal logistic-x projection is not equal spatial locus, state, energy, or material memory.
- Projector comparisons are spectral and gauge invariant in the declared common initial kinetic frame; they do not establish spatial body rotations.
- Finite sign-bracketed roots are not a global uniqueness or interval certificate; double the scanning grid to search for hidden roots.
- No assumption that the cubical phase-quadrant construction is realized physically by Q550.

The scope is a **numerical event-clock diagnostic**, not a physical time law, spatial-volume certificate, material-memory certificate, or proof of Q550 realizing the autonomous cube/quadrant construction.
