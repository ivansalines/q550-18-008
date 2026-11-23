# Q550 v18.49d — Observer-Family Rank Stability & Hidden-Complement Transport Audit

**Status:** authentic, independently replayed floating-point diagnostic of the phaseblind/branch-0 Q550 physical 11D histories and cotangent observer transport. It is not a certified observer-independent material invariant, phase-cycle theorem, or hidden-information law.

## The question

The authenticated v18.49c server sendback showed that five transported historical covectors resolve about 58% of the metric 10D finite material separation around a barrier, while the metric-orthogonal residual remains substantial. The fifth historical direction is relatively weak. This audit asks (i) how strongly the rank cutoff affects the residual, (ii) how that subspace changes along one return and between *different* return protocols, and (iii) whether adding new independent observers changes the result.

## Actual authenticated replay

- Reuses **unaltered** `inputs/v18_49c_original_server_sendback.zip` (SHA-256 pinned; original user server C output). The recursive verifier follows C → B → A → Z → Y → ... → J and validates every declared source and ancestor hash.
- Reintegrates 2 historical outgoing paths + 12 genuine counterflow physical 11D IVPs (6 ramps × original/autonomous kappa).
- Reintegrates 12 genuine material cotangent/tangent IVPs on the NEW return histories, each with the 5 original historical covector seeds and **5 additional independent *synthetic mathematical* seeds**. New seeds are not discovered physical modes or historical observer data.
- Uses both the explicitly declared Euclidean material-chart tangent metric and a declared weighted metric. For 2, 5, 6, 8, and 10 observer directions, recomputes metric-orthogonal projectors at rank thresholds `1e-4`, `1e-6`, `1e-8`, `1e-10`, `1e-12`.
- Measures full finite material displacement, its observed envelope, orthogonal residual, projector changes within each return, and a matched-phase comparison *between different ramp protocols*.
- Tests the earlier `Delta xi=0.2` / `kappa0 ≈ 1/6` scale suggestion against a direct `Delta xi=kappa0` probe. **These are subspace-recurrence diagnostics, NOT evidence that kappa0 constitutes a period or completed material evolution.**

## Real numerical results (full preflight)

- **14 physical 11D integrations**, **12 new 10D cotangent integrations** with ten covectors each, **9,000 individual rank/family/phase/metric records**, **6,720 within-return projector comparisons**, 10 comparisons across ramps, 96 kappa-length comparisons.
- At phase `q=0.50`, **all 12 five-historical-covector cases resolve rank 4 at cutoffs `1e-4`, `1e-6`; rank 5 at `1e-8`, `1e-10`, `1e-12`**. This is rank *with a declared tolerance*, not an algebraic rank theorem.
- Euclidean residual for the historical five at `1e-10` and phase `q=0.50`: **1.498624–1.510591**; observed amplitude fraction **0.562044–0.582463**.
- At the same phase, a historical+synthetic family of eight covectors intercepts about **99.18–99.25%** of the metric distance; ten independent covectors capture 100% to machine precision. The ten-covector result is **linear algebra by construction**, not new physical detection.
- Along matched phase `q=0.50` and increasing ramp from `0.285` to `0.309`, five-observer residual changes from 1.510591 to 1.498878 for original kappa while the *fraction* declines from 58.24% to 56.20%. So the increased hidden residual reported at **barrier locations** in C must **not** be generalized to every fixed phase. The choice of section matters.
- For Euclidean historical-five projector at `1e-10`, the `Delta xi=0.2` comparison yields Frobenius gaps around **1.01–1.26** rather than a projector return. This **does not** support a simple five-covector subspace closure on that window; other physical or oriented markers have not been tested.
- Parent C envelope regression: max **4.71e-11**; 11D forward history: **3.44e-13**; tangent/cotangent pairing: **1.83e-14**; metric chart covariance: **1.27e-11**; decomposition Pythagorean identity **3.46e-15**. Floating-point errors, not rigorous interval bounds.

## Reproduction

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_rank_complement_v18_49d_bundle.zip
cd q550_kappa_rank_complement_v18_49d_bundle
bash run_on_server.sh 2>&1 | tee v18_49d_server.log
```

The runner uses `Q550_PYTHON=python3.13` by default; Python 3.13, NumPy, SciPy and Matplotlib are needed. Use `--smoke` for only one kappa and one ramp; **rerun the full protocol for a final server sendback**, since smoke overwrites outputs. Numerical integration settings can be changed with `--rtol`, `--atol`, `--max-step`, and their `--adjoint-*` analogs.

The runner tests algebra, authenticates original C and nested ancestry, runs physical and cotangent IVPs, applies scientific gates, generates **four actual CSV-backed plots** and packages SHA256-manifested `sendback.zip`.

## Executable genealogy

- `scripts/verify_parent.py`: recurses through unchanged parent C ZIP and its verified historical ancestors; no remote downloads or untrusted dependencies.
- `scripts/run_audit.py`: actual replay of the physics, transported families, rank and complement scans, measured phase-window comparisons.
- `scripts/subspace_math.py`: metric-whitening, projected envelope, residual, principal angles, fully disclosed independent test directions.
- `scripts/check_outputs.py`: scientific gates and nesting/monotonicity checks.
- `tests/test_subspace.py`: six independent algebraic tests.
- `scripts/plot_results.py`: numerical CSV graphics; no invented plot data.
- `scripts/pack_sendback.py`: source, parameters, results and original C archive with checksums.
- `inputs/SOURCE_PINS.json`: exact SHA of parent original C server sendback.
- `results/`: CSV, reports and plots of this specific run.

## Scientific scope and limitations

All geometry is within the **declared 10D material chart** and declared metrics; the physical model is 11D with externally driven theta. The covector complement is observer-family dependent; a pointwise orthogonal complement in a fixed chart is not automatically a canonically transported material bundle or a physically hidden degree of freedom. Comparing projector matrices at different times assumes the chosen trivialization; transporting them invariantly would require a specified connection/metric transport. Matching ramp protocols at the same phase is not one trajectory. The `kappa0`-length comparison does not prove an orientational return nor a periodic cycle. No intrinsic physical torsion, entropic law or energetic nonreciprocity is inferred.
