# Q550 v18.48j — Gauge-Covariant Observer Transport & Cancellation Invariance Audit

**Scope:** audited transformation of the *projected analytic Hessian cancellation* under coherent affine changes of the **original frozen 10D chart**; includes a time-dependent tangent-following orthogonal frame and its adjoint connection. This is **not** a proof of observer independence, a gauge-invariant material torsion, a physical branch BVP, or an interval enclosure.

## Reproducible genealogy

- `inputs/v18_48i_original_server_sendback.zip` is the exact original server sendback received after v18.48i, not a regenerated approximation. Its SHA-256 is pinned in `inputs/PARENT_SHA256.json`.
- `scripts/verify_parent.py` checks every manifest-listed file in that archive, the nested original v18.48h sendback (including every member), the SHA-256 of the 41-section physical paths and report, and the authenticity of the extracted three original mathematical source files. It refuses extra/unmanifested entries and unsafe paths.
- `reference/` includes the **actual historical Python source** for analytic `structural_jet`, `generated_base_jet`, and original `ModelParameters`, plus the exact v18.48i `factorial_math.py`.
- The input consists of 8 genuinely integrated Q550 seed IVPs, two κ choices, two independently seeded branches, and 41 common lifted-Theta clock sections each: **328 authentic 11D states** and their 5 recorded covectors.
- **No new Q550 original integration is performed by this package.** Results below are a fresh gauge audit of those authenticated data.

The v18.48h seed phase offset and the original independence of the branch seeds remain unaltered. The physical source was integrated numerically in binary64; this bundle adds no interval certificate.

## Mathematical definitions

Let `w=[chart_scale, 1]` and `z = w^-1 y` in the local frozen chart. The original analytic Hessian decomposition is

\[
  H_z = H_{z,base} + H_{z,coupling},\quad
  H^i_{z,ab}=w_i^{-1}H^i_{y,ab}w_aw_b.
\]

At a genuine trajectory state use the original **material velocity** `v_z = F_y/w` and historical transported chart covector `g` (or the two Lie-transport controls). Each 10-component projected Hessian contribution is

\[
  B_j=g_i H^i_{z,base\,aj}v_z^a, \qquad
  C_j=g_i H^i_{z,coupling\,aj}v_z^a
  \qquad (j=0,\ldots,9).
\]

Its cancellation ratio is `R=(||B||+||C||)/||B+C||`, except coupling-null observers are flagged separately and assigned the accounting value `1`.

For **spatially linear** (at a given time) chart changes `z'=G(ξ)z+b(ξ)` with `G=diag(S,1)` and `S ∈ GL(10)`, tensor and cotangent components obey

\[
H'=G H[G^{-1},G^{-1}],\quad g'=G^{-T}g,\quad
v'_{material}=G v,\quad B'=S^{-T}B,\quad C'=S^{-T}C.
\]

The inhomogeneous frame drift in the transformed ODE is affine in `z'`, so contributes **no second spatial derivative**. It must nonetheless be subtracted when identifying the **material** velocity for the contraction. This affine transformation law is **not** valid without correction for a nonlinear state coordinate change.

The transformed physical *cometric* on covectors is `S S^T`; therefore

\[
\lVert B'\rVert_{new}^2=B'^TSS^TB'=\lVert B\rVert^2,
\qquad R'=R.
\]

Using `||B'||_2` instead is a **different metric** unless `S` is orthogonal. This test reports the intentionally naive ratio as a negative control, not as a physical prediction.

For the time-dependent frame, the variational and cotangent generators transform as

\[
 J'=GJG^{-1}+\dot G G^{-1},\qquad \dot g'=-J'^Tg'.
\]

The instantaneous algebraic connection identity is checked. An independent finite-difference estimate of the **sampled** observer derivative is also reported; 41 sections can be too sparse for a small residual and the latter is **not** represented as a certified adjoint solver convergence test.

## Frame choices

1. Identity chart, used as the baseline.
2. Fixed seeded, proper orthogonal 10D rotation.
3. Genuine-path-dependent co-moving orthogonal frame: its first axis tracks the normalized 10D chart velocity; the remaining axes are advanced by minimal pairwise rotations of successive velocities. **No arbitrary relabeling of branches or interpolated states.**
4. Nonorthogonal, anisotropically rescaled and sheared chart, used to make metric dependence obvious.

We transform state-frame vectors, complete tensors (spot-checked), the historical or Lie-transported covector, and the cometric together. The full dense tensor-first binary64 implementation is *independently evaluated* but intentionally **not trusted as ground truth**: mixing vastly different frozen-chart scales can cause severe subtractive cancellation even though the exact tensor identity is true. The stable factored route contracts the original analytic jet first, then transforms the resulting covector. Those two floating-point evaluation orders are compared explicitly.

## Local preflight results

The release was actually run with Python 3.13 on the original authenticated v18.48i server data.

| Quantity | Local preflight |
|---|---:|
| Genuine original 11D states | 328 |
| Covariance checks (4 gauges × 3 observers × 328) | 3,936 |
| Complete dense tensor pushforward spot checks | 120 |
| Maximum relative metric-covariant ratio discrepancy | 3.12e-12 |
| Maximum binary64 dense tensor-first disagreement (normalised by component norms) | **0.14882** |
| Maximum naive changed-metric ratio deviation | **0.67258** |
| Maximum algebraic adjoint-connection identity residual | 1.49e-11 |
| Maximum original finite-sample adjoint derivative residual | **0.12268** (not converged) |
| Maximum co-moving finite-sample adjoint derivative residual | **0.12268** (not converged) |
| Maximum common-frame two-factor interaction discrepancy | 7.99e-15 |
| Unit tests | 5 passed |

The 14.9% worst-case **tensor-first** discrepancy is an evaluation-order/conditioning warning, not a violation of mathematical gauge covariance. The original chart scales range from ~2e-6 to ~1e2 and make dense rotations numerically dangerous. A higher-precision symbolic/component-level pushforward is a separate future numerical task.

### Two real crests — original κ and historical observer

| Genuine Q550 state | Source cancellation | Consistently changed chart | Deliberately changed physical observer |
|---|---:|---:|---:|
| `phaseblind` branch 0, ξ=3.575 | 326.528095 | same within ~1e-9 absolute | 1.887818 |
| `phasecov` branch 0, ξ=4.25 | 59.967691 | same within ~1e-9 absolute | 5.542646 |

The observer-only negative control changes `g` but **not** the physical field and does *not* represent a coordinate gauge. It proves these crests are properties of the chosen projected observer diagnostic, not observer-independent scalar invariants.

At `phasecov` xi4.00→4.25, the v18.48i four-corner log-cancellation interaction remains the same when **all four counterfactual evaluations use a single common transformed chart and its cometric**. A separate time-dependent frame at each corner would not supply a canonical cross-state identification and is intentionally **not** used for the factorial test.

## Server run

From `/root/elab1/hysteresis` after downloading the bundle:

```bash
unzip q550_kappa_gauge_covariant_v18_48j_bundle.zip
cd q550_kappa_gauge_covariant_v18_48j_bundle
bash run_on_server.sh 2>&1 | tee v18_48j_server.log
```

`python3.13` is the default, overridable with `Q550_PYTHON`. The archive contains its own authenticated inputs and original math sources; it **does not need manually linked orbit files or the metrology events CSV**, and does not rewrite historical Q550 scripts. NumPy, SciPy, mpmath are required by the original imports; matplotlib is used to render the two result plots.

`run_on_server.sh` performs five unit tests, provenance checks, the actual analytic gauge audit, two original-data plots, then packages `sendback.zip`. Rerunning does not mutate inputs.

## Outputs and interpretation boundaries

- `results/gauge_invariance.csv`: original and cometric-corrected ratios, intentionally naive Euclidean ratios, 3 observers × 4 gauges × 328 genuine states.
- `results/full_tensor_checks.csv`: quantitative binary64 dense tensor-first numerical floor vs stable factored gauge transformation.
- `results/adjoint_frame_connection.csv`: exact algebraic connection checks and distinct finite-sample historical-covector transport residuals.
- `results/crest_atlas.csv`: focal crests and original/autonomous κ.
- `results/factorial_common_gauge.csv`: nonadditivity test on four corners with a *common* transform, not a material cross-path BVP.
- `results/observer_change_negative_control.csv`: observer-only change, not gauge change.
- `results/phaseblind_gauge_vs_naive.png` and `results/phasecov_gauge_vs_naive.png`: numeric plots using the actual CSVs.
- `results/report.json`, `runtime/provenance.json`, `SHA256SUMS_OUTPUT.json`, `sendback.zip`.

All source comments and docs are in English. The original code, parameters and SHA pins are included. The observational result is **coordinate-covariance of one projected kernel diagnostic under defined affine gauges**, not an invariant of the full physical system under arbitrary observers, nonlinear charts, or long-term transport.
