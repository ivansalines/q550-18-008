# Q550 v18.49c — Observer-Family Invariant Envelope & Material Separation Audit

## Purpose

Determine whether a **whole transported family of observers**, rather than a hand-picked observer covector, yields a reproducible amplitude for the finite material-state difference between outgoing and counterflow paths. Explicitly distinguish (1) basis-independent quantities for a *fixed* observer subspace and chosen metric, (2) changes caused by admitting more observers, and (3) the full 10D material displacement and mechanical energy difference.

**Actual result from the authenticated server-B genealogy, recomputed here:** For the twelve `phaseblind` branch-0 counterflow paths (two kappa prescriptions, six smooth ramps), at the twelve *distinct* barrier states, using an explicit Euclidean tangent chart metric, the range of observable fractions is **0.244852–0.248136 (two covectors)** and **0.575889–0.593971 (five covectors)**. The best five-dimensional family still leaves a nonzero metric-orthogonal material displacement. The chosen metric and the selected historical covectors are not intrinsic physical observables.

## Mathematical definition

Let \(d\in\mathbb R^{10}\) denote a lifted **finite** material-state difference. Let \(G\) have as columns the covectors in an observer family, and let \(M\) be a fixed declared positive-definite **tangent** metric on the chosen ten material coordinates. Define

\[
\mathcal A(G,d;M)=\sup_{g\in\operatorname{span} G,\;g^TM^{-1}g=1}|g^T d|
=\sqrt{d^T G(G^T M^{-1}G)^+G^T d}.
\]

The code uses a whitening/SVD representation with rank tolerance `--family-rank-tol` (default `1e-10`, relative to the largest singular value) instead of explicitly inverting the ill-conditioned Gram matrix. The signed envelope is symmetric, \([-\mathcal A,+\mathcal A]\): **the envelope cannot retain a universal handedness or preferred sign** unless an extra oriented observer convention is independently specified.

The full declared metric material separation is \(D=\sqrt{d^T M d}\), with residual \(\sqrt{D^2-\mathcal A^2}\) and captured fraction \(\mathcal A/D\). Under an invertible material chart change \(y'=Sy\), **all** of the material increment, covector and metric must transform as \(d'=Sd\), \(g'=S^{-T}g\), \(M'=S^{-T} M S^{-1}\). This makes \(\mathcal A\) invariant up to numerical error. Holding the metric fixed while changing the coordinates is NOT this experiment.

The physical 11D state has externally prescribed \(\Theta\); the linearized tangent and cotangent IVPs are the **10D material subsystem at fixed prescribed control**, not an 11D autonomous Hamiltonian flow. Tangent–cotangent duality is exact for the linearized equations but is **not** claimed for finite differences between two trajectories.

For each counterflow path this audit uses **five distinct, SHA-authenticated historical v18.48j covectors** *only as seeds at the turning point*, integrates them on the new material history with the original analytic Jacobian, and compares subfamilies of the first two versus all five. The five historical directions are closely conditioned: the effective rank depends on the SVD tolerance. In the specified cases with default tolerance both families resolve full nominal ranks 2/5. The phase-angle finite differences are lifted to the principal signed branch before constructing \(d\); this convention can break down at a branch-cut transition.

## Reproduction on the user's server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_observer_family_v18_49c_bundle.zip
cd q550_kappa_observer_family_v18_49c_bundle
bash run_on_server.sh 2>&1 | tee v18_49c_server.log
```

`Q550_PYTHON=python3.13` can override the interpreter. The CLI also exposes the physical integration tolerances (`--rtol`, `--atol`, `--max-step`), independent cotangent tolerances, SVD rank threshold and explicit numerical gates.

`--smoke` executes only one representative `(kappa, ramp)` case; it writes to the same `results/` directory, so **rerun the full command before making a final sendback**.

The runner: checks Python dependencies, executes nine independent algebraic unit tests, reauthenticates the **unaltered original server v18.49b sendback** and its entire nested genealogy, integrates 14 original 11D physical trajectories and 12 fresh five-covector material adjoint systems, creates the CSV/report and 3 plots, independently checks scientific gates, and packs `sendback.zip` with a deterministic SHA-256 manifest.

## File provenance, actual scripts and output

- `inputs/v18_49b_original_server_sendback.zip`: unchanged user-server original v18.49b output, SHA pinned in `inputs/SOURCE_PINS.json`. This contains A → Z → Y → X → W → V → U → ... → J recursively.
- `reference/`: mathematical source files from that original B archive **byte-for-byte copied**, each SHA pinned.
- `scripts/verify_parent.py`: validates source archive CRC, SHA membership, canonical root hierarchy, source equality, and invokes original B's recursive parent verification.
- `scripts/run_audit.py`: true 11D physical and 10D cotangent replay, family metric calculations, continuity checks and regressions against B's projected readouts and A's continuous roots.
- `scripts/family_math.py`: explicit finite-observer-family envelope/whitening, metric and chart transformation math, local phase lift.
- `scripts/check_outputs.py` and `tests/test_family.py`: scientific gates and independent SVD covariance/basis/rank algebra tests.
- `scripts/plot_results.py`: graphs computed directly from actual CSV results.
- `scripts/pack_sendback.py`: source-preserving SHA-256 output archive.
- `results/observer_family_envelopes.csv`: 576 measurement rows = 144 phase/root occurrences × two families × two metrics. Twelve distinct barrier states repeat over four threshold offsets each; do not count repeats as independent states.
- `results/transported_family_duality.csv`: independent numerical checks of transported 5-covector duality against a propagated tangent.
- `results/report.json`: key numerical regressions, observed ranges, metadata, and limitations.
- `results/*.png`: three actual plots, no synthetic line art.

## Scope and explicit limitations

Results are **floating-point diagnostics**, not interval-validated inequalities or intrinsic laws of material chirality/entropy. We do not infer that the 10D chart Euclidean metric is the model's unique physical metric, that the five directions span every possible observer, that the full material state equals the 3D shape projection, or that the observer subspace is independent of the initial historical seeds.

The physical-root geometry and energy are held fixed under observer/chart counterfactuals, while the observer-based signed scalar can change. The metric-covariant full-family envelope is basis invariant *conditional on the specified observer span and material metric*. It must not be called observer-family independent or physically absolute.
