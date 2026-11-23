# Q550 v18.48k — Observer-Space Cancellation Geometry & Crest Width Audit

**Scientific scope.** This audits the geometry of two previously observed large cancellations of the **projected analytic Hessian kernel**, varying the *physical observer covector* at a **fixed, original Q550 state**. It does not vary the actual 11D physical trajectory, continue an adjoint observer, or claim observer-independent material torsion. This is the next step after v18.48j's verified affine-gauge covariance.

## Autenticated provenance

- Input `inputs/v18_48j_original_server_sendback.zip` is the original v18.48j **server** archive from the conversation, not a synthetic or reconstructed IVP. Its SHA-256 is in `inputs/SOURCE_PINS.json`.
- `scripts/verify_parent.py` compares the hash of that archive, all its 25 manifest-listed members, the original scientific source hashes, and invokes the exact **unmodified v18.48j genealogical verifier** extracted from that archive. That verifier checks its own nested original v18.48i and v18.48h archives including their file manifests and the original 11D physical paths.
- Three historical Python sources (`structural_jet.py`, `generated_base_jet.py`, `test_support_mobius_monodromy_audit.py`) are preserved in `reference/` with identical source hashes. `reference/gauge_math.py` is the unchanged v18.48j affine-covariance helper.
- **Eight original physically integrated Q550 IVPs, 41 sections per path = 328 original 11D states**. There are no new integrations in this experiment.

## Mathematical object

In the exact historical frozen 10D chart, with the physical 11D state `y`, the actual field velocity `f`, frozen chart scales `s`, original decomposed Hessian `H = H_base + H_coupling`, and 10-component observer covector `g`, set

\[
 (L_H)_{ji}=\frac{s_j}{s_i}\sum_{a=0}^{10} H^i_{aj}f_a,
 \qquad B(g)=L_{base}g,\quad C(g)=L_{coupling}g.
\]

The algebraic equality with `structural_jet.chart_kernel` is independently verified on all 328 original states. The cancellation diagnostic is

\[
 R(g)=\frac{\|B(g)\|+\|C(g)\|}{\|B(g)+C(g)\|}.
\]

It is homogeneous in `g` and unchanged by its sign. A coupling-null observer is flagged and *not* called compensated. Original historical `g[:10]` is normalized in the same fixed 10D chart. The 11th observer coordinate is not present in this specific projected contraction.

### Measuring crest width

For each focal crest (`phaseblind`, branch 0, \(\xi=3.575\); `phasecov`, branch 0, \(\xi=4.25\)), each at original and autonomous \(\kappa_0\):

1. Compute the exact (floating-point evaluated) linear maps `L_base` and `L_coupling` from the analytic Hessian, using the authenticated original field.
2. Compute the tangential gradient of `log R` on the unit observer-covector sphere; test signed geodesics `g(t)=cos(t)g0+sin(t)d` in that specific direction.
3. Report **first** positive and negative crossings below **half the ratio at the historical observer**. The *sum* of signed angular distances is a diagnostic local half-baseline span, **not** necessarily the full width at half maximum of a globally optimized peak. Also report threshold R=10 widths.
4. Repeat with 64 seeded random unit transverse directions per crest and probe 8 angular radii per crest (64 samples each). These samples do not estimate a rigorously certified fraction of the unit sphere.
5. Independently recompute the Hessian contractions via `chart_kernel` at both crossing points and compare against `L g`. Report the complete singular-value spectra of `stack([L_base,L_coupling])` and `L_base+L_coupling`, without silently asserting that a cutoff-selected numerical rank is an invariant.
6. On all 328 original Q550 states, perform a nonorthogonal affine chart change, consistently transforming input and output covectors with the appropriate **cometric**. Confirm that the cancellation ratio is preserved. Naive Euclidean observer angles after shear are *not* comparable.

**Important scale boundary:** Here angles are degrees on the unit sphere of the **original frozen 10D covector chart**. They are **not** physical rotations of Q550's material body. Extremely narrow angles require floating-point crossing and conditioning diagnostics; no interval enclosure is claimed.

## Local end-to-end preflight results

This bundle was executed locally using the authentic v18.48j server archive. The original historical cancellation ratios were reproduced:

| Crest and \(\kappa_0\) | Historical ratio | Half-baseline total span along locally steepest direction (degrees) | Median span over 64 random tangent directions (degrees) |
|---|---:|---:|---:|
| `phaseblind` \(\xi=3.575\), original | 326.528095 | 4.688e-6 | 2.400e-5 |
| `phaseblind` \(\xi=3.575\), autonomous | 349.798777 | 4.375e-6 | 2.224e-5 |
| `phasecov` \(\xi=4.25\), original | 59.967691 | 3.273e-7 | 9.835e-7 |
| `phasecov` \(\xi=4.25\), autonomous | 59.995692 | 3.273e-7 | 1.639e-6 |

These are direction-dependent local diagnostics, **not** a geometric thickness of an observer-independent physical structure. The numerical results and limits are in `results/report.json` and full CSV ledgers. The `original` and `autonomous` random samples are seeded deterministically but not pairwise identical directions; compare directional distributions descriptively, not as paired causal changes.

## Server command

From `/root/elab1/hysteresis`:

```bash
unzip q550_kappa_observer_width_v18_48k_bundle.zip
cd q550_kappa_observer_width_v18_48k_bundle
bash run_on_server.sh 2>&1 | tee v18_48k_server.log
```

The runner defaults to `python3.13` (override with `Q550_PYTHON`); needs `numpy scipy mpmath matplotlib` for the original model imports and plotting. No manual symbolic links to orbit/event CSV files, or external historical scripts, are required.

## Outputs

- `results/observer_crest_atlas.csv`: 328 actual states and the reference ratios and norms.
- `results/observer_widths.csv`: signed threshold crossings for the steepest and random transverse observer directions.
- `results/crest_width_summary.csv`: focal direction and directional distribution summaries.
- `results/observer_direction_profiles.csv`: signed geodesic profiles around each crest.
- `results/observer_random_sphere.csv`: radius-conditional random direction probes (not certified spherical volume).
- `results/observer_singular_spectra.csv`: all singular values, without rank overclaim.
- `results/covariant_metric_controls.csv`: gauge/cometric invariance controls, all 328 states.
- `results/independent_crossing_checks.csv`: independent direct `chart_kernel` comparison at threshold crossings.
- `results/phaseblind_observer_crest_width.png`, `results/phasecov_observer_crest_width.png`, `results/observer_random_direction_medians.png`.
- `results/report.json` summary; source Python, tests, `inputs/SOURCE_PINS.json`, `SHA256SUMS_OUTPUT.json`, `sendback.zip`.

**Decision rule:** If the width spans are consistently narrow across independent observer directions and the direct analytic contraction checks pass, call it a **thin observer-space cancellation crest** in the chosen physical diagnostic. Do **not** infer material torsion, a unique observer, observer-invariant width, or a long-term physical hysteresis from this alone.
