# Q550 v18.49r — Scientific report

**Status:** PHASE_RESOLVED_NUMERICAL_AUDIT

## Authenticity

- v18.49q SHA-256 pinned: `b728f00924d688dc8a070e0745e7d9880e79af0783002916f1625e45e752710f`
- Its inherited v18.49p-to-v18.48 solver source is verified recursively.

## The mathematical distinction

- The sign of a coefficient in a newly diagonalized eigenbasis is not a physical orientation observable.
- Individual pair generators K_ij and their commutator are invariant under eigenline sign flips.
- The normalized commutator–K68 alignment is algebraically constrained to ±1; it cannot certify a dynamical flip.
- Cross-subspace Kcross follows the *whole* triad projector S, while Kinternal rotates the eigenlines inside it.

## Numerical case results

| κ₀ | Duration | Handover q | χ at end | Cross share at end | Relative SO(3) angle | Cross-only transport error |
|---|---:|---:|---:|---:|---:|---:|
| original | 0.32671875 | none | 1.0000000000000002 | 0.08410071 | 10.6366737° | 5.254e-09 |
| original | 0.32737500 | 0.6498761839 | 1.0 | 0.08282613 | 10.6622046° | 5.417e-09 |
| original | 0.33000000 | 0.6467245506 | 0.9999999999999999 | 0.07661731 | 10.8331327° | 6.136e-09 |
| autonomous | 0.32737500 | 0.6497188832 | 1.0000000000000004 | 0.08246128 | 10.6752497° | 5.424e-09 |
| autonomous | 0.33000000 | 0.6465678137 | 1.0 | 0.07616992 | 10.8520474° | 6.145e-09 |

## Geometric interpretation

In the phase interval q=0.63–0.65, all relative SO(3) angles evolve continuously from zero to about 10.64–10.85 degrees. The internal relative rotation exists both before and after the pairwise power exchange. The cross-block fraction near the end remains about 7.62–8.41% of the instantaneous generator squared norm.
The gauge-invariant bracket alignment χ is +1 within numerical precision in all tested cases; this is largely an algebraic identity and supplies NO independent physical chirality/flip evidence. The correct distinction is between the continuously oriented, reference-anchored eigenframe and the motion of its three-dimensional spectral subspace.

## Control metrics

- `max_parent_endpoint_regression`: `0.0`
- `max_gauge_sign_invariance_error`: `0.0`
- `max_constant_orthogonal_chart_error`: `2.6645352591003757e-15`
- `max_block_closure`: `1.9087599968841302e-16`
- `max_cross_derivative_closure`: `1.047424265162753e-13`
- `max_subspace_fd_error`: `1.456284986629284e-08`
- `min_relative_spectral_gap`: `0.06061780386249581`
- `min_eigenline_overlap`: `0.9999990667963795`
- `max_parallel_rotation_orthogonality`: `9.132417715101585e-15`
- `max_parallel_subspace_error`: `6.145183321904567e-09`
- `max_chi_collinearity_error`: `5.551115123125783e-16`
- `max_ledger_error`: `1.3353661926229776e-11`

## Scope and limitations

- An unordered or unoriented set of eigenlines does not have a gauge-independent intrinsic orientation.
- The scalar commutator alignment chi has |chi|=1 by a three-index Lie algebra identity wherever defined; it is not by itself independent evidence of physical torsion.
- The relative SO(3) rotation depends on the initial oriented eigenframe and chosen path; only conjugacy-invariant summaries such as angle are sign-gauge robust.
- Results are in the authenticated kinetic metric with a fixed external observer reference; no arbitrary time-dependent observer covariance or material flip theorem.
- These are high-precision floating-point replay diagnostics; no rigorous interval certificate.

No material flip, gauge-universal chirality, or interval certification is claimed.
