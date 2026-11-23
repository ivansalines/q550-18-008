# Q550 v18.49p — Pairwise Handover: Numerator–Gap Competition & Phase-Resolved Transfer Audit

**Status:** PHASE_RESOLVED_NUMERICAL_AUDIT

Original v18.49o server SHA256: `32e18e3dcb9eace605569cde098e528b4ddf5402e816423683f2d1c0d6d1d65a`. Its 152 manifest entries and all historical parents were checked. Original physical 11D and 10D tangent dynamics and the fixed kinetic metric are preserved.

## Phase-resolved event table

| κ₀ | r | numerical event q | pair shares at equality | top-2 check |
|---|---:|---:|---:|---|
| original | 0.327375000 | 0.649876183868 | 0.296187 | PASS |
| original | 0.330000000 | 0.646724550620 | 0.295406 | PASS |
| autonomous | 0.327375000 | 0.649718883171 | 0.296403 | PASS |
| autonomous | 0.330000000 | 0.646567813722 | 0.295625 | PASS |

The numerical roots are found by re-evaluating the integrated physical trajectory and its variational operator, not by fitting the old CSV values. They are not rigorous interval-certified roots.

## Exact two-factor endpoint accounting

For each rank pair, raw squared generator contribution is `A_ij=2(N_ij/g_ij)^2`. The pairwise difference satisfies `Δ(A78−A67)=Δ_N+Δ_g` exactly under symmetric endpoint Shapley accounting. This algebraic partition is not causal attribution.

| κ₀ | r | Δ_N / Δ(A78−A67) | Δ_g / Δ(A78−A67) | endpoint leader |
|---|---:|---:|---:|---|
| original | 0.300000000 | 62.0551% | 37.9449% | 6-7 |
| original | 0.326718750 | 55.7880% | 44.2120% | 6-7 |
| original | 0.327046875 | 56.1234% | 43.8766% | 6-7 |
| original | 0.327375000 | 56.4349% | 43.5651% | 7-8 |
| original | 0.330000000 | 58.2827% | 41.7173% | 7-8 |
| autonomous | 0.300000000 | 62.0569% | 37.9431% | 6-7 |
| autonomous | 0.326718750 | 55.9397% | 44.0603% | 6-7 |
| autonomous | 0.327046875 | 56.2642% | 43.7358% | 6-7 |
| autonomous | 0.327375000 | 56.5657% | 43.4343% | 7-8 |
| autonomous | 0.330000000 | 58.3583% | 41.6417% | 7-8 |

## Numerator and gap of the handover pair at r=0.327375

- **original, pair 6-7:** |N| 0.462377451 → 0.435145719 (0.9411×); gap 0.058525272 → 0.066220174 (1.1315×); raw power 124.83501397 → 86.36122342.
- **original, pair 7-8:** |N| 0.006369967 → 0.172456941 (27.0734×); gap 0.044947194 → 0.026002957 (0.5785×); raw power 0.04016976 → 87.97228588.
- **autonomous, pair 6-7:** |N| 0.462663278 → 0.434087408 (0.9382×); gap 0.058417103 → 0.066220860 (1.1336×); raw power 125.45270327 → 85.93987822.
- **autonomous, pair 7-8:** |N| 0.006060067 → 0.173601702 (28.6468×); gap 0.044921557 → 0.025932959 (0.5773×); raw power 0.03639781 → 89.62595479.

## Controls and limits

- maximum_pair_generator_norm_sq_residual: 6.8212102633e-13
- maximum_log_ratio_identity_residual: 1.99840144433e-15
- maximum_parent_o_pair67_share_difference: 1.00572883355e-11
- minimum_relative_eigen_gap: 0.0606178038625
- maximum_11D_mechanical_ledger_error: 1.33536619262e-11
- maximum_11D_forward_replay_error: 3.42499198739e-13

All 45 pairs are ranked to determine global leadership; the two compared couples are tracked by eigenvalue rank in one fixed initial kinetic metric. Phase-resolved pair equality is not automatically a material torsion flip or a new physical law. Numerical sampling does not certify uniqueness on the continuous phase interval.

