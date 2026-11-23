# Q550 v18.50h — Response Arc-Length Refinement & Co-Moving Curvature Audit

This is an executable Q550 audit, not a curve fit to v18.50g's five points. It recovers the **authenticated original Q550 RHS and sensitivity protocol** through the byte-identical v18.50g server sendback nested in `inputs/`, and re-executes the unmodified v18.50e integrator with 33 nested horizon observations on each of 20 protocols. All scripts, reports, identifiers, and comments are in English.

## Run (working directory `/root/elab1/hysteresis`)

```bash
unzip q550_response_arc_length_refinement_comoving_curvature_v18_50h_bundle.zip
cd q550_response_arc_length_refinement_comoving_curvature_v18_50h_bundle
bash run_on_server.sh 2>&1 | tee v18_50h_server.log
```

Use Python 3.13 if available (fallback `python3`), NumPy, SciPy, and Matplotlib.

**Note:** the public `run_on_server.sh` executes the 20-case 33-point audit and then a *separate genuine physical replay* focused on the early near-zero interval, for original κ₀ and cubic r=0.24. The second pass operates in an ephemeral `runtime/` copy of v18.50e; it does not overwrite v18.50h's outputs. Running `--smoke` performs a 2-case main audit, omits the early zoom, and overwrites the main result CSVs; rerun without `--smoke` before packing a complete sendback.

## Method

1. Verify the exact v18.50g archive manifest and member hashes, then the nested f and e archives, followed by v18.50e's full Q550 solver ancestry (v18.50d and earlier).
2. Execute the authenticated v18.50e `scripts/run_audit.py` **unchanged**, with 33 equally spaced observations, `Δξ = 0, 0.0015625, ..., 0.05`. Each protocol uses the same initial conditions, phase treatment, centered logit-x state kick, and common 4D metric as the original v18.50e.
3. Compare the five inherited time samples with the original v18.50e vectors, and check residuals of the directional linearization.
4. Measure polygonal length on the nested 5/9/17/33-point subsets. The nested polyline is a lower bound on the true continuous response-curve arc-length. Record straightness, sampled chord turns, cancellation, and any peak brackets.
5. Refine the reference early cancellation window with 160 additional samples between `Δξ = 0.000025` and `0.004`, plus original horizon anchors. This is a physical ODE resimulation, not interpolation of the old five points.

## Key files

- `scripts/verify_ancestry.py` — complete ZIP/hash validation and original integrator staging
- `scripts/run_audit.py` — authentic 33-point experiment orchestration and geometric analysis
- `scripts/early_zoom.py` — additional physical replay of initial cancellation peak
- `scripts/plot_results.py` — reproducible plots
- `scripts/pack_sendback.py` — full descriptive sendback archive and SHA-256 manifest
- `tests/test_geometry.py` — numerical geometric invariants
- `results/dense_response_vectors.csv` — all 660 authentic response vectors and decomposition terms
- `results/arc_grid_refinement.csv` — per-protocol 5/9/17/33 polyline lengths
- `results/early_cancellation_zoom.csv` — sampled near-zero peak on original κ₀
- `results/report.json`, `results/early_zoom_report.json`, `SCIENTIFIC_REPORT.md`

## Scientific boundary

The original and autonomous Q550 parameter families are both processed; the autonomous value for n=10, Q=550 is 7π/132. None of the observed response-coordinate features validates this value physically; both parameters are input choices to the solver. Neither finite chord sums nor sampled peaks are strict interval-certified continuous invariants. The local/transport split is a coordinate ledger, not an independent material-energy split. No material-memory, physical fiber, new spatial volume, universal phase clock, or bifurcation is certified.
