# Q550 v18.49n — Ramp-Shape Perturbation & Pairwise Dominance Persistence Audit

**Scientific task.** Test whether the rank-6–7 eigenprojector pair dominates the initial-frame material generator across *genuinely different* Q550 return-brake commands, not just across the six ramp durations measured in v18.49m. Keep the original 11D Q550 physical ODE, true analytic 10D variational propagation, and declared fixed kinetic metric (tau_ref=1).

## Exact ancestry and experimental controls

`inputs/v18_49m_original_server_sendback.zip` is the authentic, byte-identical original v18.49m server ZIP. Its SHA-256 and root are pinned by `inputs/SOURCE_PINS.json`. `scripts/verify_parent.py` checks root and all ZIP contents, SHA manifests, and recursively validates the Q550 lineage down to v18.48j. Every inherited algebraic/kinetic helper is byte-compared to its authentic source. The runtime extraction is excluded from the child ZIP (the parent ZIP already contains all executable historical ancestors).

Each prescribed return command uses the continuous clock-rate `s(t) = 1 - 2 h(t/r)` on the ramp, with shape completion `h(0)=0, h(1)=1, h'(0)=h'(1)=0`, monotonicity, and the common integral `∫_0^1 h(u)du=1/2`. For `t>=r`, `s=-1`. The phase excursion is the exact antiderivative `-t + 2r∫_0^(t/r) h(u)du` during the ramp and `t-r` after it. Therefore **shape is varied without changing the duration, endpoint rate, or subsequent registered q-clock**. The physical 11D solver is the original solver and receives the new command through its existing ramp interface.

Shapes: `cubic` (original smoothstep), `quintic` (smoother step), `cosine`, `skew_minus`, `skew_plus`. The two skew variants add ±3 times a zero-area even polynomial to the cubic shape (details in `scripts/ramp_shapes.py`). Cases are the 5 shapes × 3 durations (0.285, 0.300, 0.309) × two values of κ₀ (original and autonomous), **30 independent return experiments**, each on 121 phases q=0.35..0.65. Additionally the two authenticated 11D forward trajectories are rerun. No synthetic or interpolated dynamics replaces any physical or tangent integration.

## Mathematical diagnostic and decision

For ordered simple principal spectrum `C a_i = λ_i a_i` of material `C=BᵀB`, and the authentic derivative `Cdot`, compute:

    N_ij = |a_j.T Cdot a_i|
    d_ij = lambda_i - lambda_j > 0
    weight_ij = 2*(N_ij/d_ij)**2
    ||K||_F**2 = sum(weight_ij) for 45 rank pairs
    D_67 = weight_67 / ||K||_F**2
    margin_67 = D_67 - max_{(i,j)!=(6,7)} D_ij

A case shows **late dominance persistence** if 6–7 is the largest rank-pair contribution at *every sampled* q from 0.55 to 0.65. It shows **final majority** if D67(q=0.65)>0.5. Report onset of first lead and majority as sampled/linearly bracketed estimates (not certified roots), domain length within the scanned phase interval, endpoint margin, full cross-case envelope, final 45-pair rank correlation with the original cubic run, minimum relative eigen-gap, plus the previously defined exact two-factor endpoint Shapley algebraic attribution of the change q=0.50→0.65. No redistribution is interpreted as physical mode energy transfer.

`SCIENTIFIC_REPORT.md` is regenerated from the server output, never based on fabricated data. `results/report.json` controls its claim status. A smoke run explicitly reports `SMOKE_DIAGNOSTIC_ONLY` rather than full-domain acceptance.

## Server run

From `/root/elab1/hysteresis`:

```bash
unzip q550_ramp_shape_perturbation_pairwise_dominance_persistence_v18_49n_bundle.zip
cd q550_ramp_shape_perturbation_pairwise_dominance_persistence_v18_49n_bundle
bash run_on_server.sh 2>&1 | tee v18_49n_server.log
```

The runner uses `python3.13` by default, or set `Q550_PYTHON=python3`. Requires Python >= 3.10, numpy, scipy, matplotlib. Generates output tables, plots, scientific report, SHA256 manifest, `../q550_ramp_shape_perturbation_pairwise_dominance_persistence_v18_49n_bundle_sendback.zip` and an in-folder `sendback.zip`. The descriptive ZIP and root directory remain paired. The original v18.49m archive is never modified.

Optional independent short diagnostic (not a substitute for the full experiment): `bash run_on_server.sh --smoke --phase-points 31`.

## Genealogical contents

- `inputs/` immutable ancestor archive and source hashes.
- `scripts/run_audit.py`, `scripts/ramp_shapes.py` actual physical audit and shape interventions.
- `scripts/{frame_math,generator_math,kinetic_metric,pairwise_math}.py` SHA-checked inherited helpers.
- `scripts/verify_parent.py` recursive trusted-ancestry verification.
- `scripts/check_outputs.py`, `scripts/plot_results.py`, `scripts/generate_report.py`, `scripts/pack_sendback.py` complete postprocessing and packaging.
- `tests/` inherited algebraic unit tests and new equal-area/clock/domain controls.
- `results/` pairwise phase contributions (45 pairs per sample), aggregated phase and case statistics, shape controls, full-case envelope, report, four figures, environment.
- `SHA256SUMS_OUTPUT.json` hash manifest once packaged.

## Boundaries

The test assesses only these five specified command profiles, three durations, two κ choices, q∈[0.35,0.65], and the declared kinetic metric. A simple 10D spectral ordering is required. It does not establish all-ramp universality, a coordinate- and metric-independent invariant, rigorously validated interval onsets, any mode energy flux, or a physical mechanism for the dominance.
