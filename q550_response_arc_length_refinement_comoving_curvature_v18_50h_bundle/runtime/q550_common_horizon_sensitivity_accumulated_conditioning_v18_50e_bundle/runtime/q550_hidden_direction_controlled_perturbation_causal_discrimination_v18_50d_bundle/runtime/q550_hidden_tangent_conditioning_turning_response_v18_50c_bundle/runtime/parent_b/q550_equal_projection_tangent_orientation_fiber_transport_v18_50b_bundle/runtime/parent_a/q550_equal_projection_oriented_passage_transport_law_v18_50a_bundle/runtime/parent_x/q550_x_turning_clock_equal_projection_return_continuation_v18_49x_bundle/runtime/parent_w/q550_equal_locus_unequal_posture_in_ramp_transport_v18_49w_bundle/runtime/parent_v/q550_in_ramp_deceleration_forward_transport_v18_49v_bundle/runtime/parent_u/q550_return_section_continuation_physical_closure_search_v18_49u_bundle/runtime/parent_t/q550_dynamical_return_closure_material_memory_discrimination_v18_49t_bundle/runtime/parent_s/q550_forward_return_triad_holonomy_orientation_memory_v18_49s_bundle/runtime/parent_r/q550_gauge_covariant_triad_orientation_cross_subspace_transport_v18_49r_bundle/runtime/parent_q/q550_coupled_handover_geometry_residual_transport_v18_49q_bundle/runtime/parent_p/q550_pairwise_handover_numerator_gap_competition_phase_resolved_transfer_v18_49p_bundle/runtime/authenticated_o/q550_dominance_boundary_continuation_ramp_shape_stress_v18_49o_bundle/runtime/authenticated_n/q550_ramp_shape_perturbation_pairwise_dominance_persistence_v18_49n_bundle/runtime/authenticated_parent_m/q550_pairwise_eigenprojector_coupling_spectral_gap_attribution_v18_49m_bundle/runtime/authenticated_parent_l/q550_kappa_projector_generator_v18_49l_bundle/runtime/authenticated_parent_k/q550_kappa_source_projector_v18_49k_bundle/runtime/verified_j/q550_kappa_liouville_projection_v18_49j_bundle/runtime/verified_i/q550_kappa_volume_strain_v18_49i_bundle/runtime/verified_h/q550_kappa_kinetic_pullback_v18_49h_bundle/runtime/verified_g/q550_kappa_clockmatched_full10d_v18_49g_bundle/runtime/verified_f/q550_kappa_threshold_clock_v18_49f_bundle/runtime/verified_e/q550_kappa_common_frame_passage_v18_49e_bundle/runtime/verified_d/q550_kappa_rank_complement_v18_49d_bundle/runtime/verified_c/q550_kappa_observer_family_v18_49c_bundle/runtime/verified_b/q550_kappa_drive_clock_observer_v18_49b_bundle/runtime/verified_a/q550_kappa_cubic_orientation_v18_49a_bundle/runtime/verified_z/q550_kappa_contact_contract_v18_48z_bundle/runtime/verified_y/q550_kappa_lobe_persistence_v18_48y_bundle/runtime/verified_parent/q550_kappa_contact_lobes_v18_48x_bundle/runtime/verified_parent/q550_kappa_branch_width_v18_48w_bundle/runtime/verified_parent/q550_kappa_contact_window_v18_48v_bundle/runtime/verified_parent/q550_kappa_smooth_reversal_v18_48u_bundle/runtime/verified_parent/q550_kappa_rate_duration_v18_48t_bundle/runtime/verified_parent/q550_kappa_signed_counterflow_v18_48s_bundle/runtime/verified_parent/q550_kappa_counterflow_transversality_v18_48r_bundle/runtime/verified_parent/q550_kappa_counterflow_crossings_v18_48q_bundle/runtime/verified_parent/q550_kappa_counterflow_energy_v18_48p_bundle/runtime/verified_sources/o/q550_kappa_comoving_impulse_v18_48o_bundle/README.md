# Q550 v18.48o — Co-Moving Phase Delay & Impulse-Robust Transport Audit

## Aim

Test whether the exploratory source/observer phase lag reported by v18.48n is stable under an explicit discrete **co-moving observer gauge**, when the sign of `d(log R)/dξ` is retained, and when individual dominant signal impulses are omitted without compressing the time axis. The true data are the 328 full-11D Q550 states, in eight authentic physical IVPs (`xi=3.5..4.5`, 41 common-Theta sections each), and authentic **forward integrated** historical cotangent covectors from v18.48h. Their original data and exact Python genealogy are preserved in the original v18.48n server sendback, nested under `inputs/` and SHA-pinned.

## What *co-moving* means, precisely

`g_i` is the normalized 10D **projected** historical cotangent covector in the inherited frozen Euclidean chart. Projective signs are aligned successively. Between sections, the unique minimal rotation in `SO(10)` that is the identity on the orthogonal complement of the two observer directions carries `g_i` to the aligned `g_{i+1}`. The cumulative orthogonal frames are `R_i`, with `R_i*g_0≈g_i`. For each instantaneous cancellation projector `P_i` computed from the inherited real Hessian source geometry, pull back:

```
P_i^co = R_i.T @ P_i @ R_i.
pace_fixed = ||P_{i+1} - P_i||_F / delta_xi
pace_comoving = ||P_{i+1}^co - P_i^co||_F / delta_xi
```

**Crucial boundary:** this is a reproducible *discrete projective minimal-turn gauge*, **not** an integrated material tangent/cotangent transport law, nor the actual unique gauge-covariant connection. The 11th original covector component is excluded by the inherited frozen chart. Because this gauge parallelizes only one observer line, an alternative transverse frame can produce different co-moving projector speeds. Constant orthogonal coordinate rotations leave the diagnostics covariant; time-dependent arbitrary gauge choices require their connection corrections. Orthogonality, projective line tracking, source threshold and original scalar invariants are tested.

## Measured observables

At source cutoffs 1e-6 and 1e-10, cancellation cutoff 0.01, in 40 intervals per original trajectory:

- Fixed chart / co-moving projector step norm; original forward historic observer-line angular pace.
- The authentic historical `log R`, signed `d(log R)/dξ`, and absolute magnitude `|d(log R)/dξ|`.
- Signed change in source imbalance `(||Bg||-||Cg||)/(||Bg||+||Cg||)`; this is **not material energy**.
- Historical observer alignment with instantaneous near-cancellation projector (typically extremely small).
- Signed cross-correlations over lags -6...+6 steps. Positive lag means the **response** follows the driver. Report all lags and sample counts, not just the maximum.
- Whole-history, central 80% and 60% windows; leave-one-local-impulse-out for the four largest sufficiently separated driver spikes and four largest response spikes, removing the spike and one neighboring interval each side. **Removed intervals become masked; indices are not compressed**. Lags are recomputed on aligned indices. Cyclic-shift controls for the three windows are descriptive, not inferential p-values.

Regression gates compare historical `R`, signed rate and fixed-chart projector pace against v18.48n records, not just archive metadata. No new long physical integrations occur.

## Reproduction on server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_comoving_impulse_v18_48o_bundle.zip
cd q550_kappa_comoving_impulse_v18_48o_bundle
bash run_on_server.sh 2>&1 | tee v18_48o_server.log
```

Python 3.13 or override `Q550_PYTHON=python3.13`; needs `numpy scipy mpmath matplotlib` (requirements.txt). Complete nested v18.48n->m->k->j->i->h history is authenticated automatically; no external orbit files.

Optional runner arguments: `--source-cutoffs 1e-6,1e-10 --cancel-cutoff 1e-2 --max-lag-steps 6 --pulse-radius 1 --max-events 4`.

## Outputs

`results/phase_states.csv`, `phase_steps.csv`, `lag_cases.csv`, `lag_scans_full.csv`, `impulse_stability.csv`, `comoving_frame_quality.csv`, `report.json`, plus plots `phaseblind_branch0_comoving_rhythm.png`, `phasecov_branch0_comoving_rhythm.png`, corresponding `*_lag_compare.png`, `phasecov_impulse_stability.png`. Original runnable scripts in `scripts/`, mathematical unit tests in `tests/`, the immutable parent ZIP and hashes in `inputs/`. `pack_sendback.py` generates SHA256SUMS_OUTPUT.json and `sendback.zip`, including original input and whole reproduction chain.

## Preflight reading

Phasecov branch 0, original κ0 and source cutoff 1e-6, **absolute** logR response: both fixed-chart and co-moving driver select +2 samples (`+0.050 xi`) on the full 40-step trace with Pearson r≈0.5833 and descriptive cyclic exceedance 0.025. Six out of eight masked leave-one-impulse scans also select +2; two select +1; both central windows select +1. The **signed** dlogR trace instead selects lag 0 on the full trace (r≈0.553), with only four out of eight masked leave-one-impulse scans preserving that lag. There is no robust unique response time.

At cutoff 1e-6 the fixed and co-moving projector speeds nearly coincide on this branch (relative to the observably tiny near-null observer overlap). At cutoff 1e-10 the fixed median pace drops to ~0.0203/xi but co-moving median is ~0.2518/xi, a pronounced **reference-dependent** difference, not additional physical motion.

### What is NOT supported

No genuine inverse-time physical integration, no anti-flow navigation experiment, no verified energy balance, no dissipative hysteresis law, no unique model-independent phase-lag, no inference in seconds, and no physical 11D rigid-body rotation is established. Cross-correlation from a 40-step deterministic record is descriptive; additional independent trajectories, stability controls, and a defined material energetic observable are needed.
