# Q550 v18.48t — Counterflow Rate–Duration Separation & Contact Persistence Audit

**Status: FULL original-support 11D numerical preflight completed.** All scientific descriptions and source comments are in English. The user-provided **authentic server sendback** of v18.48s is embedded byte-for-byte and its r/q/p/o/j ancestry is authenticated recursively. No artificial trajectory generation, no replacement support equation, no unverified energy observable.

## Why v18.48t exists

The v18.48s result compared material velocities unchanged at the turn versus fully inverted. v18.48t samples *partial* velocity reversals while varying the drive rate independently from the **programmed return duration**, with a phase-closed control and a common external-phase comparison window. Its objective is to determine whether close **3-coordinate geometric** returns and the signs of **mechanical drive-power contributions** persist under controlled protocol changes. There is no implication that a 3D near-contact is a full 11D reunion or that a signed model power is a thermodynamic entropy flux.

## Authentic original Q550 physics

The material state has 11 coordinates, the physical support RHS remains the original model implementation, and its mechanical energy plus four power channels is obtained byte-for-byte from v18.48s. Eight physical seed paths are authenticated, from two observer families (`phaseblind`, `phasecov`), two branches, and two kappa choices (original kappa0=1/6 and the autonomous candidate). Original 41-section paths are regenerated as 8 genuine 11D IVPs for direct regression; 280 additional, genuinely integrated return IVPs use **DOP853**, default `rtol=3e-12`, `atol=3e-13`, `max_step=0.025`. Results use the full 15-component auxiliary integration for four model-mechanical work channels.

### Three independent imposed controls

1. **Drive rate** `rate`: externally imposed return drive speed is `-rate` times the original drive in the xi clock.
2. **Programmed duration** `duration`: the return is integrated for this many xi units. Stopping later **does not change the already traversed trajectory** at fixed rate and starting state; this is an explicit causality identity, not a new material phenomenon.
3. **Material preparation parameter** `alpha`: five material velocities at the turning point become `(1 - 2*alpha)*v_turn`, with samples `alpha=[0,0.25,0.5,0.75,1]`. At alpha=0 velocities remain unchanged; at alpha=1 all are reversed; alpha=0.5 sets them to zero. Other material coordinates, internal angles, and the drive phase are unchanged at the turn.

The **seven unique rate-duration protocols** are:

| Design | rate | duration | rate×duration | Intent |
|---|---:|---:|---:|---|
| phaseclosed_slow | 0.75 | 4/3 | 1.00 | fixed net phase sweep |
| phaseclosed_reference | 1.00 | 1.00 | 1.00 | original v18.48s anchor |
| phaseclosed_fast | 1.25 | 0.80 | 1.00 | fixed net phase sweep |
| durationfixed_slow | 0.75 | 1.00 | 0.75 | fixed duration |
| durationfixed_fast | 1.25 | 1.00 | 1.25 | fixed duration |
| ratefixed_short | 1.00 | 0.80 | 0.80 | fixed rate |
| ratefixed_long | 1.00 | 1.20 | 1.20 | fixed rate |

Note that the 7 controls yield **3 distinct return-drive rates**, and at fixed alpha and seed, histories with the *same* rate share their IVP prefix when expressed at matched external phase. Thus **288 solver integrations** are recorded, but the 280 reverse integrations are not 280 independent dynamical laws or unrelated historical seeds.

## Phase locking and persistence

The original forward clock is `Theta_F(s) = Theta_turn - omega*(1-s)`; the return clock is `Theta_R(u) = Theta_turn - omega*rate*duration*u`. Therefore equal **unwrapped** phase requires

```
s(u) = 1 - rate*duration*u
q = rate*duration*u
```

Here the dimensionless progress variables `u` and `s` are parameters of the separately integrated physical trajectories. We exclude the prescribed turn at `u=0` by searching only `u >= 0.25`, require `u <= 0.96`, and confine forward progress to `[0.04,0.75]`. Contact minima are resolved by sampling plus local bounded refinement on these continuous IVPs. Endpoint-selected minima are explicitly marked as *boundary* events, not physical internal intersections.

**All 7 designs** are also compared on the same common unwrapped phase interval

```
q in [0.312500001, 0.719999999], 81 samples each
```

For each `(seed,design,alpha,q)`, sample the full forward-time integrated states; measure 3D chart distance in `(log rho1,log rho2,x)`, signed mechanical energy difference, and opposite/same sign of instantaneously evaluated drive powers. Persistence uses declared 3D thresholds `[0.0025, 0.005, 0.01, 0.02]` and maximal consecutive common-phase width, rather than conflating isolated near-contacts with stable intervals.

## Critical partial-reversal energy ledger

For intermediate alpha, the *preparation itself* changes kinetic energy. This cannot be attributed to later counterflow or damping. With `c=1-2*alpha`, the exact preparation jump satisfies

```
DeltaE_prep = E(prepared_turn) - E(original_turn)
            = (c*c - 1) * T_material_velocity(original_turn).
```

The pointwise matched-clock energy gap must then satisfy

```
E_return(u) - E_forward(s) =
       [W_forward(turn) - W_forward(s)]
       + DeltaE_prep
       + W_return(u),
```

where `W` is the sum of all **four** signed mechanical-work channels (external drive power, radial damping, x damping, and active-x force). This is verified independently from direct energy evaluation at the matched points. The initial jump is an externally imposed preparation operation; there is no constructed actuator cost or assertion of passivity for the operation.

## Full-preflight results (original 8 authenticated Q550 paths)

- 288 **genuine** original-support 11D integrations; 280 equal-external-phase contact optimizations; 22,680 common-phase profile samples; **12/12 independent mathematical unit tests**.
- The **minimum** 3D matched-phase gap among declared protocols is **0.000438908818**, but the smallest observed full 11D matched-phase gap remains about **1.03645**. No full-state return is certified.
- The best 3D gap median across 56 protocol-seed combinations at each alpha changes from about **0.43830** (alpha 0), **0.22041** (alpha 0.25), **0.16474** (alpha 0.5), **0.08018** (alpha 0.75), to **0.001368** (alpha 1). These are descriptive sample medians, not an assumed monotonic law between samples.
- Opposing signed instantaneous drive power at a same-clock best near-contact occurs in **196/280** cases overall: **28/56** for each of alpha 0, 0.25, 0.5; **56/56** at alpha 0.75 and 1. The protocols share physical seeds and thus these are **not** statistically independent trials.
- The median **preparation energy jump** is approximately **-0.27274** at alpha 0.25 or 0.75, and **-0.36365** at alpha 0.5. It is zero at alpha 0 and 1; a large middle-alpha energy gap is predominantly a preparation intervention, not a demonstrated net counterflow loss.
- Maximum normalized reverse energy-balance residual **5.43e-15**; maximum absolute matched-point energy-gap ledger residual **1.84e-13**; maximum energy jump identity error **1.67e-16**.
- Maximum reproduced historical 11D section error **1.47e-11**; maximum external-phase mismatch **8.88e-16 rad**.
- Sixteen authenticated v18.48s `(rate=1,duration=1,alpha in {0,1})` original endpoint checks: maximum 3D contact-gap regression below **8e-15**; maximum signed drive-power regression below **5e-11**.
- An explicit control compares the trajectories with *equal rate and identical starting state* but differing planned duration. Among **12,960** matching matched-phase comparisons, the **maximum** 3D shape/profile gap is around **5e-16** and energy/power discrepancies around **1.1e-15**. This is the expected causal-prefix identity. Changing planned duration can affect the *accessible endpoint*, not earlier physically identical states.

**Scientific decision:** Geometrically closer near-returns are strongly associated with **fully reversed** material velocities in these samples, while the signs of drive power also depend on the reversal preparation. No universal energy law or intrinsic material time delay is inferred. The duration effect is not independent on a common elapsed phase unless the forcing profile is itself modified.

## Linux server reproduction

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_rate_duration_v18_48t_bundle.zip
cd q550_kappa_rate_duration_v18_48t_bundle
bash run_on_server.sh 2>&1 | tee v18_48t_server.log
```

The runner verifies every SHA-256 of the original unchanged v18.48s server ZIP and recursively re-verifies all authentic source ancestors, runs twelve independent unit tests, reintegrates 288 original 11D IVPs, generates original figures, tests all output numerical identities and generates `SHA256SUMS_OUTPUT.json` plus `sendback.zip`. It requires Python 3.13 / NumPy / SciPy / Matplotlib. Set `Q550_PYTHON` only if a different interpreter is desired.

Optional **partial debugging only**:

```bash
python3.13 scripts/run_audit.py --limit-groups 1 --alpha 0 0.5 1 --profile-nodes 41 --minimizer-nodes 71
```

A subset run is **not** the full audit and marks the report `limited_preflight`; the normal server command automatically uses the complete configuration.

## Executable and provenance files

- `inputs/v18_48s_original_server_sendback.zip`: exact original 2026-10-26 **server** sendback, nested authentic r/q/p/o/j ancestry.
- `inputs/SOURCE_PINS.json`: original SHA-256 pins of the server archive and unchanged source mathematical helpers.
- `reference/{physical_math,transversality_math}.py`: original physical observables and 3D geometry, byte-identical to the signed parent.
- `scripts/{verify_parent,protocol_math,run_audit,check_outputs,plot_results,pack_sendback}.py`: full original-source replay, partial velocity preparation with correct energy jump, contact refinement, shared-clock persistence and reproduction/packaging.
- `tests/test_protocol_math.py`: 12 independent pure mathematical unit tests.
- `results/protocol_contacts.csv`: per-protocol, per-seed near contacts, signed energy and power, contact classification, persistence.
- `results/common_phase_profiles.csv`: all 22,680 matched-phase states' **diagnostics** over one common external-phase interval (full original states remain accessible through the embedded historical source; new IVPs regenerated by the scripts).
- `results/historical_regression.csv`, `results/report.json`: original 11D section regression and complete scientific gates.
- `results/*.png`: four original-data figures showing partial reversal, persistence, energy-preparation jump and matched-phase geometry.
- `SCIENTIFIC_DECISION_RULES.md`: precise scope and non-claims.
- `SHA256SUMS_OUTPUT.json`, `sendback.zip`: reproducible transport with a verified archive root; `runtime/` is recreated during verification, not included to avoid duplicating nested ancestry.
