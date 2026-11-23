# Q550 v18.48m — Principal-Angle Subspace Transport & True-Intersection Audit

## Scope and scientific boundary

Investigates source-active and near-cancellation covector subspaces in the frozen normalized **10D** observer chart obtained from authenticated 11D Q550 physical states. Source models and transport data are inherited byte-for-byte from the authenticated v18.48l server sendback, which includes nested v18.48k/j/i/h provenance. No new physical Q550 integrations are performed.

**Numerical proximity ≠ mathematically proved intersection.** Dimensions are numerical and depend on declared source and cancellation cutoffs. A dimension-forced intersection is distinguished from mere 2D projected overlap and from directions where BOTH source contributions vanish. Candidate shared directions are tested for source activity and cancellation at both adjacent states. No physical material-branch continuity or new torsional invariant is claimed.

## Mathematical objects

At a fixed state, let `B,C: R^10 -> R^10` be the source-base and coupling projected Hessian maps. Let `A=[B; C]` and `T=B+C`. Compute SVD of `A`, retain source-active right singular vectors with singular value `> source_cutoff * sigma_A_max`. Let `W = V_r diag(1/sigma_r)` whiten source activity. The singular vectors of `T W` measure the generalized ratio `||Tg||/||Ag||`. Retain the span of `W v_i` where the singular values are `<= cancellation_cutoff`; QR gives a Euclidean orthonormal basis `U` for that near-cancellation plane.

For consecutive sections, compute all principal angles between these U subspaces, `||P_a-P_b||_F`, `||P_a-P_b||_2`, and source-plane analogues, where `P=UU^T`. Test principal shared-direction candidates using original `A_a,A_b,T_a,T_b`. A 2D projected angle is always compared to the actual full-10D line angle.

When ranks vary, **projector gaps include the dimension mismatch**; angles alone are incomplete. Any intersection forced by `dim U+dim V > 10` is reported separately as an elementary dimension lower bound, not evidence of a physical relation. Geometry is compared along each of eight original trajectories only, without re-labeling independent branches.

## Run

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_subspace_intersection_v18_48m_bundle.zip
cd q550_kappa_subspace_intersection_v18_48m_bundle
bash run_on_server.sh 2>&1 | tee v18_48m_server.log
```

Optional: `bash run_on_server.sh --source-cutoffs 1e-4,1e-6,1e-8,1e-10,1e-12 --cancel-cutoffs 1e-3,1e-2,5e-2`.

Uses `python3.13` and `numpy, scipy, mpmath, matplotlib` (see environment.json and requirements.txt). All reference scripts and nested historical ZIPs are authenticated before processing. The script doesn't rely on symlinks to external orbit caches.

## Results

- `results/subspace_atlas.csv`: ranks and generalized source-normalized singular spectra across all 328 states.
- `results/adjacent_principal_angles.csv`: principal-angle extrema, source- and cancellation-projector gaps, and candidate source/residual checks.
- `results/shared_direction_checks.csv`: explicitly qualified near-shared candidates at 1e-6 and 1e-10 source cutoffs.
- `results/projection_false_crossings.csv`: selected coordinate projections against full-10D line angles.
- `results/report.json`: summary, all cutoffs, provenance and scientific limitations.
- `results/*.png`: subspace transport, rank changes and projection diagnostics.
- `SHA256SUMS_OUTPUT.json`, `sendback.zip`: verified output genealogy.

## Reproducibility

The real source functions are `reference/structural_jet.py`, `reference/generated_base_jet.py`, `reference/observer_geometry_v18_48k.py`, `reference/test_support_mobius_monodromy_audit.py`. The Python scripts actually used are retained in `scripts/`, as are the unit tests. No historical source is edited. `inputs/v18_48k_original_server_sendback.zip` is SHA-pinned by `inputs/SOURCE_PINS.json` and nested checks reconstruct `runtime/` on demand. No cached runtime is included in the distribution.

## Limitation

All Q550 states are inherited floating-point observations. Full algebraic rank and exact common subspaces would require symbolic rank identities or rigorous interval bounds beyond this audit. The principal-angle calculation in the normalized 10D covector chart is numerically gauge-defined; it must not be mistaken for an observer-independent intrinsic angle under arbitrary nonorthogonal coordinate transforms without a transformed metric.
