# v18.49n — Ramp-Shape Perturbation & Pairwise Dominance Persistence Audit

Run classification: **NUMERICAL_AUDIT_COMPLETED**.

## Main measured decision

- Physical controls: 5 shapes, 3 ramp durations, 2 kappa choices.
- Total Q550 experiments: 30.
- Pair 6–7 is the final leader in every tested case: **YES**.
- Pair 6–7 has final majority in every case: **YES**.
- Pair 6–7 remains the leader at every tested sample q∈[0.55,0.65] in every case: **YES**.
- Lowest final share across tested cases: **61.0214%**.
- Smallest final advantage over strongest rival: **47.4578 percentage points**.
- Minimum advantage at sampled q>=0.55: **4.0895 percentage points**.

## What was controlled

The original Q550 11D ODE and 10D analytic variational equations are replayed from the SHA-authenticated parent genealogy. All brake shapes keep the same end values, duration and integral of the clock-reversal completion function (1/2). Thus the registered return clock after the ramp is common, and the shape of the command is the actual intervention.

## Numerical lineage and quality

- Physical forward runs: 2; physical return runs: 30; genuine 10D tangent propagators: 30.
- forward_regression: 3.424992e-13
- mechanical_ledger: 2.210267e-10
- pair_frobenius_identity: 4.831691e-13
- upstream_cubic_max_abs_share_difference: 1.727785e-11
- identity_at_q050_q065: 5.684342e-14

## Per-case results

| kappa | ramp | shape | 6–7 final % | first lead (estimated q) | q>=.55 lead? |
|---|---:|---|---:|---:|---|
| original | 0.285000 | cubic | 67.7644 | 0.538454 | YES |
| original | 0.285000 | quintic | 67.7150 | 0.538639 | YES |
| original | 0.285000 | cosine | 67.7551 | 0.538488 | YES |
| original | 0.285000 | skew_minus | 67.7639 | 0.538465 | YES |
| original | 0.285000 | skew_plus | 67.7650 | 0.538444 | YES |
| original | 0.300000 | cubic | 67.0577 | 0.522780 | YES |
| original | 0.300000 | quintic | 66.9338 | 0.522978 | YES |
| original | 0.300000 | cosine | 67.0347 | 0.522817 | YES |
| original | 0.300000 | skew_minus | 67.0615 | 0.522793 | YES |
| original | 0.300000 | skew_plus | 67.0540 | 0.522768 | YES |
| original | 0.309000 | cubic | 61.3223 | 0.513349 | YES |
| original | 0.309000 | quintic | 61.1019 | 0.513558 | YES |
| original | 0.309000 | cosine | 61.2817 | 0.513388 | YES |
| original | 0.309000 | skew_minus | 61.3320 | 0.513364 | YES |
| original | 0.309000 | skew_plus | 61.3126 | 0.513335 | YES |
| autonomous | 0.285000 | cubic | 67.8239 | 0.538404 | YES |
| autonomous | 0.285000 | quintic | 67.7741 | 0.538589 | YES |
| autonomous | 0.285000 | cosine | 67.8145 | 0.538438 | YES |
| autonomous | 0.285000 | skew_minus | 67.8234 | 0.538414 | YES |
| autonomous | 0.285000 | skew_plus | 67.8244 | 0.538394 | YES |
| autonomous | 0.300000 | cubic | 67.0504 | 0.522735 | YES |
| autonomous | 0.300000 | quintic | 66.9257 | 0.522932 | YES |
| autonomous | 0.300000 | cosine | 67.0273 | 0.522771 | YES |
| autonomous | 0.300000 | skew_minus | 67.0542 | 0.522747 | YES |
| autonomous | 0.300000 | skew_plus | 67.0466 | 0.522722 | YES |
| autonomous | 0.309000 | cubic | 61.2432 | 0.513305 | YES |
| autonomous | 0.309000 | quintic | 61.0214 | 0.513514 | YES |
| autonomous | 0.309000 | cosine | 61.2022 | 0.513343 | YES |
| autonomous | 0.309000 | skew_minus | 61.2529 | 0.513319 | YES |
| autonomous | 0.309000 | skew_plus | 61.2333 | 0.513291 | YES |

## Interpretation boundary

- Finite selected shape families only, not all possible ramp shapes.
- Sampled dominance on the phase grid, bracket/linear onset estimates, not interval-certified roots.
- Metric and initial kinetic frame are inherited from v18.49m; no metric-universal dominance claim.
- Pair ranks require a simple ordered eigenvalue spectrum; algorithm rejects small spectral gaps.
- Numerator/gap Shapley split is an endpoint algebraic attribution, not a physical causal intervention.
- No test of nonlinear forcing mechanism or energy transfer between pair modes.

Numerical onset markers are sample-bracketed estimates. Claim persistence only for the tested families, ramps, kappa choices, and declared kinetic metric.
