# Scientific report — Q550 v18.49l

## Authentication

Direct Python audit of the historical v18.48j→v18.49k genealogy within the unchanged original uploaded K server sendback, followed by twelve authentic return histories with analytic 10×10 variational transport. New source files, inputs, reports, graphs and SHA-256 manifests travel together.

## Primary calculation

The eigenspace generator is computed from `Cdot` via the simple-spectrum perturbation identity `Omega[j,i]=(A.T Cdot A)[j,i]/(lambda_i-lambda_j)`. Its validity is checked independently against numerical derivatives of the original principal projectors from K. This is a tensorial construction in the declared kinetic frame and fixes the sign ambiguity of individual eigenvectors.

At `q=0.50` for **original** kappa:

| Ramp xi | Generator norm | Principal log-strain-rate norm |
|---:|---:|---:|
| 0.285 | 5.49487 | 0.96850 |
| 0.292 | 5.55107 | 0.98571 |
| 0.296333 | 5.59021 | 0.99722 |
| 0.300 | 5.62643 | 1.00745 |
| 0.305 | 5.68112 | 1.02209 |
| 0.309 | 5.72992 | 1.03435 |

The ramp=0.300 `Cdot` off-diagonal Frobenius fraction at q=0.5 is 0.98419; the normalized commutator fraction is 0.59550. These are representations of the same local tensor time derivative, not independent experimental causes. The principal-stretch rates and the local projector rotation have different meanings despite their concurrent ramp dependence.

## Numeric checks (first authentic preflight)

- Forward trajectory regression: 3.43e-13.
- K historical log-volume regression: 1.15e-14.
- K rank-one occupation regression: 7.77e-15.
- Generator vs independent finite-difference projector derivative (121 phase nodes): 7.11e-3 absolute max, dominated by finite-difference discretization.
- Generator vs historical finite-difference projector line speed: 6.58e-3 absolute max.
- `sum(sigma_i'/sigma_i)-tr(B^-1 Bdot)`: 1.44e-14 max.
- Volume generator vs historical kinetic Liouville source: 1.84e-10 max.
- Constant orthogonal gauge consistency: 6.52e-14 norm.
- Minimum relative principal eigenvalue separation: 0.08460.

## Decision

**PASS: authenticated numerical reconstruction of the covariant principal-projector generator in a fixed declared kinetic frame.**

**NOT ESTABLISHED:** metric-independent physical holonomy, universal material torsion, causal linkage to the selected ramp, or a new conservation law. The main reason is that the kinetic embedding scale and the variation protocol define the metric and the family of histories; a time-dependent comparison frame must include a connection.
