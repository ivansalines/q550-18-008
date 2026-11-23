# Q550 v18.49o — Dominance-Boundary Continuation & Ramp-Shape Stress Audit

**Status:** FOCUSED_BOUNDARY_BRACKETED_NUMERICALLY

Parent v18.49n SHA256: `35329685d48728db40eaf6d4b1eb8e8a0fe56725e02e4cae1a9687313bbd7579`.
Parent cubic share regression max absolute error: 6.4395e-12.
Unique tested control cases: 12; numerical failures: 0.

## Duration continuation at the identical cubic command shape

- original: opposing endpoint margins in r=[0.326718750, 0.327375000], M=[0.0291175, -0.00548102]. Sample-based continuation, not an interval certificate.
- autonomous: opposing endpoint margins in r=[0.326718750, 0.327375000], M=[0.0222895, -0.0124815]. Sample-based continuation, not an interval certificate.

## Shape perturbation at fixed r

No sampled shape-stress endpoint lost pair 6–7 dominance; no general shape-invariance theorem is implied.

## Numeric controls

- Forward replay error: 3.425e-13.
- Largest ledger error: 3.167e-11.
- Minimum relative eigen-gap: 6.062e-02.

## Evidence boundaries

- Sampled numerical brackets, not interval-certified topology or continuous-time roots.
- Changing ramp duration is distinct from changing shape at fixed duration.
- No universal domination beyond admissible shapes, sampled ramp ranges, or fixed kinetic metric.
- A sign change is a rank-pair contribution cross-over, not proof of physical torsion flip.
- Nonmonotonic recoil shapes may involve temporary re-acceleration without leaving clock rate [-1,1].
- If no opposing-signed endpoints found, no boundary is established.
