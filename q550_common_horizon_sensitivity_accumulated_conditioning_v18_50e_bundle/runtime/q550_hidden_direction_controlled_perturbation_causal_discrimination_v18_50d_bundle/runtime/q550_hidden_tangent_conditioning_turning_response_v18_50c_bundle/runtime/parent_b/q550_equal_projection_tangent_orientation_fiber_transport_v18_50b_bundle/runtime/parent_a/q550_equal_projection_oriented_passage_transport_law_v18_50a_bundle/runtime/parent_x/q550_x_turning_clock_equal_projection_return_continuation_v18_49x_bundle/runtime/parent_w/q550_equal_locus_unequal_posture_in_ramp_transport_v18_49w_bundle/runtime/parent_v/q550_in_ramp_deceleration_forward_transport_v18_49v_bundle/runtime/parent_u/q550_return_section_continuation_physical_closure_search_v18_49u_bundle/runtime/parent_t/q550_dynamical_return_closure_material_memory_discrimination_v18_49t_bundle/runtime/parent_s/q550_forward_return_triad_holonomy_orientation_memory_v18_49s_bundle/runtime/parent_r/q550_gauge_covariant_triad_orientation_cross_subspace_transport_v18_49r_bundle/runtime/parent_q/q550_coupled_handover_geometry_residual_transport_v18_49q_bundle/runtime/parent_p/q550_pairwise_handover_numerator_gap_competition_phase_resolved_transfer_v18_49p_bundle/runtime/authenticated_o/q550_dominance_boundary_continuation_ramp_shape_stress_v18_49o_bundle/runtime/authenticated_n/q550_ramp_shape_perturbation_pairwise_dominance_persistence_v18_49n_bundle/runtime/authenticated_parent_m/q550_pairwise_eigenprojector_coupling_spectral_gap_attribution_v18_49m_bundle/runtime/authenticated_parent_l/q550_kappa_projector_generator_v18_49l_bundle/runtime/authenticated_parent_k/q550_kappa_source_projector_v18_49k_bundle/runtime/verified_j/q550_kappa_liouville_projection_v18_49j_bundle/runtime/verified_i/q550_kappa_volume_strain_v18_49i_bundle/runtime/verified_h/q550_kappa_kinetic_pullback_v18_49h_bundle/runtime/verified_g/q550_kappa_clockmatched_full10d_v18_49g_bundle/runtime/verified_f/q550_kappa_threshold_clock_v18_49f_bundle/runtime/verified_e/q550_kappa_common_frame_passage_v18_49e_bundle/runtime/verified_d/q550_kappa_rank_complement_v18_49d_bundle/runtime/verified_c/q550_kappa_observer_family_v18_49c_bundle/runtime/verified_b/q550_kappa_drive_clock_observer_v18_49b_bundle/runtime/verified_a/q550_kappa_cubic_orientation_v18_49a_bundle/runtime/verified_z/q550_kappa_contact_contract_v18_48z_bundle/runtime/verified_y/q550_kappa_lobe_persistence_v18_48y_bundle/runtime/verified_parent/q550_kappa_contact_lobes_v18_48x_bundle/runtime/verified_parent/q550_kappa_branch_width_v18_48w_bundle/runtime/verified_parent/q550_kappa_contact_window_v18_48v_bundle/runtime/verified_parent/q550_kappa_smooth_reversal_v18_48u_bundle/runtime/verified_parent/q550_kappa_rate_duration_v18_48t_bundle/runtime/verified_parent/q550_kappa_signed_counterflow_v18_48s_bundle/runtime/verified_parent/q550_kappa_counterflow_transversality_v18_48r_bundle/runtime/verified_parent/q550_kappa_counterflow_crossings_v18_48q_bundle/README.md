# Q550 v18.48q — Counterflow Near-Crossings & Phase–Energy Separation Audit

**Status:** executable 11D original-support model replay; genuine reverse-drive IVPs; no global crossing or thermodynamic irreversibility certificate.

## Scientific question

Can the material 11D trajectory on the return leg approach its outward **three-coordinate shape** while failing to reproduce the outward phases, internal tau velocities, and mechanical energy? How does this depend on reverse-clock rate, duration, and an idealized initial tau-velocity flip?

This audit follows v18.48p and does not reduce a real 11D trajectory to an invented curve. It reproduces eight original physical Q550 initial-value problems and solves new control-response IVPs using the pinned original support RHS.

## Authentic source and reproducibility

The unchanged server archive `inputs/v18_48p_original_server_sendback.zip` contains the original v18.48p results and the SHA-verified v18.48o and v18.48j source hierarchy. `scripts/verify_parent.py` authenticates the ZIP root, all 27 parent file digests, ancestor manifests, and the original v18.48h 11D source SHA. The energy and original-support formulas in `reference/physical_math.py` are byte-for-byte identical to the pinned v18.48p source. `inputs/SOURCE_PINS.json` records exact archive/source SHA-256.

Scientific program: `scripts/run_audit.py`, `scripts/crossing_math.py`, `scripts/plot_results.py`, `scripts/pack_sendback.py`. Dependencies are in `requirements.txt`; tests in `tests/`.

## Forward / counterflow definitions

For each of the eight physically authenticated paths, the program reintegrates an original forward IVP from xi=3.5 to 4.5 and compares against the original full 11D sections and against the v18.48p saved replay.

Each reverse-drive IVP **starts at the physical turnaround state** with external clock speed `dTheta/dxi = -rate*omega`, where `omega=0.844357915384206 rad/xi`. Apart from the explicitly prescribed clock sign/speed, the pinned 11D material RHS is unchanged. Two initial conditions are examined:

1. Keep original tau velocities at turnaround.
2. Flip initial `(v1,omega1,v2,omega2,vz)` once, and then integrate the same material law in positive xi. An instantaneous flip is an idealized impulse/intervention, not a passive material return. Its direct energy jump is recorded (zero for the chosen quadratic kinetic terms).

Five designs per initial condition:

| Design | rate | reverse xi duration | prescribed phase change |
|---|---:|---:|---:|
| phase_closed | 0.5 | 2 | -omega |
| phase_closed | 1 | 1 | -omega |
| phase_closed | 2 | 0.5 | -omega |
| fixed_duration | 0.5 | 1 | -0.5*omega |
| fixed_duration | 2 | 1 | -2*omega |

Thus 8 reference forwards + 8 paths x 5 designs x 2 initial conditions = **88 new 11D integrations**. Phase-closed tests couple rate and duration, while fixed-duration controls do not return the clock to the original phase. **Do not compare their terminal states as if they obeyed the same imposed phase history.**

## Continuous near-crossing analysis

Two distinct geometric candidate searches, both on numerical dense-output DOP853 original 11D IVPs:

1. `progress_matched`: compare return at normalized progress `u` with reference outward at `s=1-u`; minimize `||(logrho1,logrho2,x)_reverse(u) - (...)_forward(1-u)||` over `u in [0.06,1]`, excluding the identical turnaround.
2. `asynchronous_free_pair`: allow `u` and `s` to be independent; 61x61 coarse grid, 501-sample cubic geometric guide, 17 multistart least-squares searches, and direct reinsertion/refinement with the genuine dense 11D IVP. This search uses `u in [0.25,0.96]`, `s in [0.04,0.75]` **to exclude a deliberately broad vicinity of the shared turnaround**. Multistart is numeric, not a proven global optimum. Boundary solutions are flagged.

For every selected pair export source-time progress, 3D shape gap, all three modulo-2pi phase offsets, all five tau-velocity offsets, an 11-coordinate phase-wrapped residual, and the mechanical energy gap. The asynchronous time offset is a **comparison offset** `u+s-1`, not an inferred physical response delay.

Energy function and integral components are inherited exactly from v18.48p: rotational drive work, radial damping, x damping, and nonconservative active x work. Mechanical E is model-defined and need not be conserved. The continuous identity is checked for every new IVP.

## Server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_counterflow_crossings_v18_48q_bundle.zip
cd q550_kappa_counterflow_crossings_v18_48q_bundle
bash run_on_server.sh 2>&1 | tee v18_48q_server.log
```

Use `Q550_PYTHON=python3.13` (default) or override with a compatible interpreter. The runner verifies genealogy, executes `unittest`, performs the full physical integrations, produces CSV/JSON/PNG artifacts, and writes `sendback.zip` with a cryptographic file manifest. No external data symlinks or reconstructed orbits are needed.

## Output map

- `results/report.json`: aggregate diagnoses, numerical settings, exact provenance, and scientific boundary.
- `results/sweep_summary.csv`: 80 protocol-specific counterflows, rates, durations, terminal gaps, clock offset, and energy work.
- `results/near_crossing_pairs.csv`: 160 refined near-pair results, with flags for interior/boundary extrema.
- `results/energy_balance.csv`: independent 80-trajectory work/dissipation ledger.
- `results/matched_progress_samples.csv`: 81 progress samples per return protocol and their phase/energy/velocity differences.
- `results/source_regression.csv`: regression against 328 authenticated 11D source states and original v18.48p replay.
- `results/selected_case_dense_samples.npz`: 81 full 11D samples from the displayed `phasecov` branch 0, original kappa, phase-closed rate 1, velocity-flipped case.
- `results/*.png`: actual geometric and mechanical source plots.
- `inputs/`, `reference/`, `scripts/`, `tests/`, `SHA256SUMS_OUTPUT.json`: complete executable provenance.

## Preflight findings (not an interval certificate)

- 88 original-support 11D integrations; 160 numerical closest-pair candidates.
- Original forward path max absolute 11D regression below `9e-12` and mechanical balance normalized residual below `2.1e-15`.
- `phasecov` branch 0 original kappa, rate 1 phase-closed velocity-flipped: interior progress-matched minimum at `u≈0.669`, three-coordinate gap `≈0.001561`, full phase-aware 11D gap `≈2.308977`, tau-velocity L2 gap `≈2.290404`, theta2 gap `≈-0.292248 rad`, energy difference `≈-0.006543`. External Theta matches within numerical error.
- This confirms a **near-return in the reduced geometry without a return in the 11D material state**, in this protocol. It does not prove an exact 3D curve intersection, an exact phase/energy invariant, or a universal material law.

## Decision boundary

The observed differences depend on imposed protocol, elapsed time, and idealized velocity flip. Multistart minima are not rigorous interval-certified or globally exhaustive. Never reinterpret the phase-closed return as the mathematical inverse trajectory; never interpret a near-crossing of three selected coordinates as an 11D full-state crossing. No general thermodynamic irreversibility or intrinsic memory-time claim follows from this diagnostic alone.
