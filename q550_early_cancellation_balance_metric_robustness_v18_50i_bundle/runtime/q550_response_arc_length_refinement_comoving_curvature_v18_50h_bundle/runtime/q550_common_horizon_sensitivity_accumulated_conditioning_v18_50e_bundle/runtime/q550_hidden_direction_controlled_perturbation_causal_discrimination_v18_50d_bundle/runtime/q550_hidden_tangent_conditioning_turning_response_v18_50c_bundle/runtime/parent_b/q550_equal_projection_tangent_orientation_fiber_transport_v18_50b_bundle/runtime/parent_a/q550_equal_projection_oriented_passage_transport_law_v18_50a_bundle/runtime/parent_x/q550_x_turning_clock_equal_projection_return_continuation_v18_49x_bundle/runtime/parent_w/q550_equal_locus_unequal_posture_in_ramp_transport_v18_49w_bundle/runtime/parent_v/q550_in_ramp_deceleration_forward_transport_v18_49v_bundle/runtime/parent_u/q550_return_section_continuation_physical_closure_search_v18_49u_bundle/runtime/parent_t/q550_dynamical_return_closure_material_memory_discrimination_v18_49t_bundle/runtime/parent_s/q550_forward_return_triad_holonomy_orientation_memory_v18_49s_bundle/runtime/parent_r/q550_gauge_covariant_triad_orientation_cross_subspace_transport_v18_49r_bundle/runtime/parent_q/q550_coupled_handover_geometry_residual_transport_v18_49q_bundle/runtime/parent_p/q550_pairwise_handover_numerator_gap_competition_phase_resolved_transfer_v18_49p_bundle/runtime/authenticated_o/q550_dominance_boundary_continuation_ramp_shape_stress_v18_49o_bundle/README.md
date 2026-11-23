# Q550 v18.49o — Dominance-Boundary Continuation & Ramp-Shape Stress Audit

## Scientific question
Where, within a specified equal-phase-area command family and physical ramp-duration range, does the leading rank-pair **6–7** lose first place relative to one of the other 44 projector-coupling pairs? Distinguish loss of **majority** from loss of **leadership**. The target is a numerical, two-sided sign bracket of `M_67=D_67-max_other(D_ij)`, at the same registered return phase `q=0.65`, with spectral-gap/ledger checks.

## Authentic genealogy
`inputs/v18_49n_authentic_server_sendback.zip` is the untouched original user-provided v18.49n server sendback (SHA256 pinned in `inputs/SOURCE_PINS.json`), including the immutable authentic v18.49m source. `scripts/verify_parent.py` checks 34/34 n files and replays n→m→historical ancestry to v18.48j. The four inherited mathematical helper scripts are byte-checked. The solver uses the original physical 11D equations, genuine 10D tangent frame, original gauge/metric `tau_ref=1`. The first case reproduces original n cubic q=0.65 within 2e-6 before testing further parameters.

## Controls and staged scan

1. **Duration-boundary scout**: fixed cubic control shape `beta:2:2` (identical to `3u²-2u³`), durations `r=[0.08,0.12,0.18,0.24,0.285,0.3,0.309,0.33,0.36,0.40,0.46,0.55,0.70,0.90]`, `q=[0.35,0.50,0.55,0.60,0.65]`; original and autonomous κ. These alter duration and cannot be treated as pure shape effects.
2. **Fixed-r shape stress**: `r=0.300` and `0.309`, two κ choices. Monotone beta-profile symmetric sharpening or symmetric two-stage plateaus, skew bulges, and bounded nonmonotone recoil shapes. All satisfy `h(0)=0,h(1)=1,h'(endpoints)=0,0<=h<=1,integral(h)=1/2`, so post-ramp clock registration agrees even when the command shape differs.
3. **Bisection** of every detected opposing-sign *duration* pair, up to four brackets × seven bisections. A sign bracket is numeric, not an interval-certified root. If no bracket occurs, report that honestly; do not claim no boundary exists.
4. **Dense phase** evaluation over 61 q samples of cubic control plus bracket neighbors, to distinguish an endpoint crossing from intermittent sampled late-phase changes.

A rank-pair contribution is `2 |a_j^T Cdot a_i / (lambda_i-lambda_j)|²`. All 45 unordered rank pairs are considered, with positive simple ordered eigengaps. The generator and physical state are genuinely reintegrated for each parameter case; no interpolated physical dynamics.

## Run on server
From `/root/elab1/hysteresis`:

```bash
unzip q550_dominance_boundary_continuation_ramp_shape_stress_v18_49o_bundle.zip
cd q550_dominance_boundary_continuation_ramp_shape_stress_v18_49o_bundle
bash run_on_server.sh 2>&1 | tee v18_49o_server.log
```

Focused numerical two-sided boundary replication (the run included in this archive):

```bash
bash run_on_server.sh --focus --bisection-steps 5 --dense-phase-points 31
```

For the larger discovery survey (more expensive), omit `--focus` and use the default run above. The focused archive establishes only its narrow local bracket, not all scanned shape/duration regions.

Optional short check, **not** a full scientific result:

```bash
bash run_on_server.sh --smoke --dense-phase-points 31
```

Needs Python 3.10+ (`Q550_PYTHON` override), numpy, scipy, matplotlib. Outputs report, two figures, per-case phase CSVs, numeric failure ledger, certified input hashes, and a descriptive `q550_dominance_boundary_continuation_ramp_shape_stress_v18_49o_bundle_sendback.zip` alongside the bundle directory.

## Interpretation
A sign change of the sampled pairwise lead means that the rank-based projector-coupling dominance changed in this **specific** kinetic frame and metric. It is not an eigenvalue degeneracy, a physical flip, or a universal invariance statement. A scan with no sign change is an evaluated robust region, not proof of global permanence. Nonmonotone recoil commands remain physically bounded in instantaneous clock rate, but differ categorically from a single-pass monotone reversal.
