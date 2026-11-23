# Q550 v18.48p — Controlled Counterflow Trajectory & Mechanical Balance Audit

## Experimental question

Does genuinely reversing the rotating phase drive make the full 11D Q550 material trajectory retrace its preceding path, or does it evolve along a distinct history? Does an explicitly derived mechanical-energy accounting distinguish the two protocols?

This experiment follows Q550 v18.48o and the original user's hypothesis about phase-response delays on a unidirectionally rotating moving surface, and temporally, geometrically and energetically imbalanced anti-flow navigation. The hypothesis is not pre-certified.

## Authentic inputs

- `inputs/v18_48o_original_server_sendback.zip` is the actual final server archive returned by the user. Recursive original v18.48o genealogy is verified, including v18.48n/m/k/j/i/h.
- `inputs/v18_48j_original_server_sendback.zip` is the original server archive of v18.48j, independently verifying the exact v18.48i->h 11D trajectory array, 41 sections per eight physical paths.
- Unmodified SHA-pinned **original reference** `test_support_mobius_monodromy_audit.py`, `test_support_q550_support_ode_interval_residual_pilot_v1.py`, `structural_jet.py`, `generated_base_jet.py`. `SOURCE_PINS.json` records exact bytes of both archive sources and all four reference Python files.

## Five 11D IVPs per authentic trajectory

Every case (two families × two historical seed branches × two values of kappa0) uses one authentic historical 11D state at xi=3.5 and a common phase clock. For each case:

1. **Forward replay**: independently integrate the actual original 11D material ODE xi=3.5..4.5; verify against all 41 recorded original states.
2. **Mathematical inverse**: integrate that same ODE with decreasing xi=4.5..3.5, from the actual recomputed forward terminal state. This should close to the start in exact deterministic arithmetic, but does *not* model external anti-flow navigation.
3. **Reverse phase drive**: starting at the same terminal state, integrate in *positive* time, replace only the prescribed original `dTheta/dxi=+omega_clock` by `-omega_clock`.
4. **Reverse phase drive + reversed velocities**: also flip `v1,omega1,v2,omega2,vz` at the terminal turning point and integrate the reversed drive forwards in time. This is a declared intervention, not canonical physical time reversal.
5. **Unchanged forward drive**: continue the original command forwards in time as a control.

The physical RHS for the first ten states is always the historical function. The only change to the ODE in protocols (3-4) is the externally driven last component. No interpolation of states produces trajectories.

## Measured observables

- Geometric return gap in `(log rho1,log rho2,x)`, corresponding phase-clock mismatch, full frozen-chart return gap (the latter is highly sensitive to chart conditioning and **is not a material distance**).
- Explicit mechanical energy E and its exact source identity. Losses from the two radial dampers and the `x` damper; drive work due to changing `Theta`; nonconservative work due to `x`-forcing and the x-dependence of `kappa_eff` (see `SCIENTIFIC_DECISION_RULES.md`). The identity is independently tested against the original RHS.
- All 41 states and four cumulative work integrals per IVP. Each energy endpoint gap is compared with integrated source terms, using the same true adaptive DOP853 trajectory. No ad hoc energy proxy is presented as a conserved physical Hamiltonian.

## Reproduce on the Q550 server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_counterflow_energy_v18_48p_bundle.zip
cd q550_kappa_counterflow_energy_v18_48p_bundle
bash run_on_server.sh 2>&1 | tee v18_48p_server.log
```

`python3.13` default; `Q550_PYTHON=python3.13` override if needed. Dependencies listed in `requirements.txt`. Optional arguments: `--rtol 3e-12 --atol 3e-13 --max-step .0125`; the original 41-section grid is mandatory.

## Outputs

`results/protocol_summary.csv` (40 protocol/case summaries), `results/trajectory_samples.csv` (1,312 return protocol samples), `results/energy_balance.csv` (40 exact-balance quadratures), `results/reference_regression.csv` (8 original full-11D forward checks), `results/full_11d_protocol_trajectories.npz` (all 1,640 new real 11D samples, including the four accumulated energy-source integrals), `results/report.json`, and three numerical figures. `sendback.zip` and `SHA256SUMS_OUTPUT.json` are generated and verified by the runner. Full source scripts and pinned original nested archives are part of the executable genealogy.

### Scientific interpretation and limitations

The backwards integration of the same ODE is the mathematical inverse of a flow map and should retrace to numerical tolerance. Reversing only the drive (or drive and turnaround velocities) is a distinct externally prescribed experiment and need not retrace. A disparity is a well-defined *protocol-dependent non-retracing* observation; it is not yet a universal thermodynamic non-reciprocity or a reversible-work theorem. Mechanical E is a declared potential-and-kinetic energy functional satisfying a source balance; because of the active `x` force and external rotating command it is **not a conserved Hamiltonian**. The upstream observations are fixed at Q=550 and do not imply generality over n/Q or a physical rigid-body flip.
