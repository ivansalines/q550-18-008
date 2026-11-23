# Q550 v18.49a — Contact-Lobe Cubic Skew & Phase-Orientation Audit

**Real physical source:** the byte-exact server sendback from v18.48z, `sendback(20261027-153539).zip`, is embedded in `inputs/`; exact SHA-256 pin, all original 39 manifest files, recursively verified historical genealogy through v18.48j. Original 11D equations and all historical scripts remain unchanged inside their original nested source ZIPs.

## Aim

The Z experiment measured a positive cubic Taylor coefficient at the `phaseblind branch0` inter-lobe maximum for both kappa models. But cubic sign is generally chart-dependent. This audit measures the distinction between **physically oriented response relative to prescribed drive phase** and **coordinate-dependent cubic skew**. It checks both root midpoints from real dense-IVP threshold roots and Taylor-jet transport with independent refits on genuine Y 11D-generated profile samples.

## Exact local transformation

Let `q` be the increasing phase offset **against the external rotating drive** after the reversal prelude, such that `Theta_return=Theta_turn-omega*q`. Let `x=q-qb` and chart `s=e*(x+beta*x^2/2)`, `e=+1` or `-1`; within the tested interval the chart is monotone. At the stationary inter-lobe maximum:

- `C_s=C_q`
- `D3_s=e*(D3_q-3*C_q*beta)`
- `D3_q=e*D3_s+3*C_q*beta`

Consequently the local cubic vanishes for the beta chosen as `beta*=D3_q/(3*C_q)`. Even an **orientation-preserving** monotone nonlinear chart can reverse the raw cubic sign. The original `q` chart is privileged *for a phase-locked diagnostic* because it is calibrated to the actual commanded angle, not because a cubic coefficient becomes a coordinate-free physical invariant.

Direct root midpoint displacement `m=(q_left+q_right)/2-qb` is signed in the drive-calibrated q; an arbitrary chart changes its value. The original roots are always recovered numerically after inverse transformation; there are no fake roots from a surrogate polynomial. Strict sublevel-set connectedness is preserved by a monotone rechart even when width and coefficient signs change.

## Authenticated data, experiments, results

- Parent Z: six ramps `r=[.285,.292,.296333,.300,.305,.309]`, two kappa values, four level offsets `delta=[1e-5,3e-5,1e-4,3e-4]`: **48** genuinely IVP-refined threshold root pairs.
- Parent Y: **46** authentic physical contact profiles (1601 q samples each). A local degree-six fit in the original and four counterfactual charts is repeated directly on the original Y profiles.
- **240** chart transforms of authentic root pairs, **60** independent local chart fits, **36** command-clock checks, including monotone reversal and cubic-zeroing charts.
- **Default server runner also repeats 14 actual original 11D IVPs** (two historical forwards + twelve reverse smoothstep protocols) with original Z code and compares the 48 regenerated root pairs against the embedded authenticated original data. Numerical energy ledger is independently checked by the historical solver.
- The authenticated full replay found all 48 physical-clock midpoint shifts **positive** across this experimental domain; 12 of 12 orientation-preserving beta=-1 chart checks made the raw cubic **negative**; beta* makes the local cubics algebraically zero. Nonlinear-chart refits follow the chain rule within explicitly reported finite-fit error.
- The original full 11D states remain separated at the barrier. All reported geometric contact events are sublevel events of a chosen 3D projection, not material-state crossings.

## Run on server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_cubic_orientation_v18_49a_bundle.zip
cd q550_kappa_cubic_orientation_v18_49a_bundle
bash run_on_server.sh 2>&1 | tee v18_49a_server.log
```

The ZIP root is **exactly** `q550_kappa_cubic_orientation_v18_49a_bundle/`, with no extra directory level. Uses `python3.13` unless `Q550_PYTHON` overrides it. No manual orbit symlink, external path, or missing original input required. End product: `sendback.zip` with source, outputs and manifest.

Faster authenticated reanalysis without any new integration:

```bash
python3.13 scripts/run_audit.py
python3.13 scripts/check_outputs.py
python3.13 scripts/plot_results.py
python3.13 scripts/pack_sendback.py
```

The report clearly distinguishes `AUTHENTIC_PARENT_11D_REANALYSIS` (zero new integrations) from `FULL_FRESH_11D_CHART_AUDIT` (14 new integrations).

## Outputs

- `results/report.json`: scope, true counts, errors, key outcomes.
- `results/continuous_11D_root_validation.csv`: 48 original physics root pair records.
- `results/physical_phase_skew.csv`: 48 physical phase-locked root-midpoint asymmetries and energy-state separation.
- `results/chart_counterfactuals.csv`: 240 exact original-root transformations and coordinate-dependent finite-level ratios.
- `results/independent_chart_jet_refits.csv`: 60 comparisons of chain-rule jet and actual independent Y phase-profile fits.
- `results/physical_drive_phase_clock.csv`: 36 actual prescribed drive-clock calibration checks.
- `results/topological_contact_control.csv`: original-vs-chart component counts in two genuine Y ramps.
- Four plots generated from the above.
- Full ancestor ZIP, pin SHA, independent tests, manifest, source and README.

## Scientific limits

No certified global normal form, interval-proof contact topology, branch-universal invariance, continuous symmetry of material equations, unique material direction, fundamental chirality or entropy-production law is claimed. The orientational sign is meaningful only with the specified physical drive-clock calibration; varying q nonlinearly without carrying that calibration changes it. The local fit coefficients depend on the chosen fit window and finite source samples.
