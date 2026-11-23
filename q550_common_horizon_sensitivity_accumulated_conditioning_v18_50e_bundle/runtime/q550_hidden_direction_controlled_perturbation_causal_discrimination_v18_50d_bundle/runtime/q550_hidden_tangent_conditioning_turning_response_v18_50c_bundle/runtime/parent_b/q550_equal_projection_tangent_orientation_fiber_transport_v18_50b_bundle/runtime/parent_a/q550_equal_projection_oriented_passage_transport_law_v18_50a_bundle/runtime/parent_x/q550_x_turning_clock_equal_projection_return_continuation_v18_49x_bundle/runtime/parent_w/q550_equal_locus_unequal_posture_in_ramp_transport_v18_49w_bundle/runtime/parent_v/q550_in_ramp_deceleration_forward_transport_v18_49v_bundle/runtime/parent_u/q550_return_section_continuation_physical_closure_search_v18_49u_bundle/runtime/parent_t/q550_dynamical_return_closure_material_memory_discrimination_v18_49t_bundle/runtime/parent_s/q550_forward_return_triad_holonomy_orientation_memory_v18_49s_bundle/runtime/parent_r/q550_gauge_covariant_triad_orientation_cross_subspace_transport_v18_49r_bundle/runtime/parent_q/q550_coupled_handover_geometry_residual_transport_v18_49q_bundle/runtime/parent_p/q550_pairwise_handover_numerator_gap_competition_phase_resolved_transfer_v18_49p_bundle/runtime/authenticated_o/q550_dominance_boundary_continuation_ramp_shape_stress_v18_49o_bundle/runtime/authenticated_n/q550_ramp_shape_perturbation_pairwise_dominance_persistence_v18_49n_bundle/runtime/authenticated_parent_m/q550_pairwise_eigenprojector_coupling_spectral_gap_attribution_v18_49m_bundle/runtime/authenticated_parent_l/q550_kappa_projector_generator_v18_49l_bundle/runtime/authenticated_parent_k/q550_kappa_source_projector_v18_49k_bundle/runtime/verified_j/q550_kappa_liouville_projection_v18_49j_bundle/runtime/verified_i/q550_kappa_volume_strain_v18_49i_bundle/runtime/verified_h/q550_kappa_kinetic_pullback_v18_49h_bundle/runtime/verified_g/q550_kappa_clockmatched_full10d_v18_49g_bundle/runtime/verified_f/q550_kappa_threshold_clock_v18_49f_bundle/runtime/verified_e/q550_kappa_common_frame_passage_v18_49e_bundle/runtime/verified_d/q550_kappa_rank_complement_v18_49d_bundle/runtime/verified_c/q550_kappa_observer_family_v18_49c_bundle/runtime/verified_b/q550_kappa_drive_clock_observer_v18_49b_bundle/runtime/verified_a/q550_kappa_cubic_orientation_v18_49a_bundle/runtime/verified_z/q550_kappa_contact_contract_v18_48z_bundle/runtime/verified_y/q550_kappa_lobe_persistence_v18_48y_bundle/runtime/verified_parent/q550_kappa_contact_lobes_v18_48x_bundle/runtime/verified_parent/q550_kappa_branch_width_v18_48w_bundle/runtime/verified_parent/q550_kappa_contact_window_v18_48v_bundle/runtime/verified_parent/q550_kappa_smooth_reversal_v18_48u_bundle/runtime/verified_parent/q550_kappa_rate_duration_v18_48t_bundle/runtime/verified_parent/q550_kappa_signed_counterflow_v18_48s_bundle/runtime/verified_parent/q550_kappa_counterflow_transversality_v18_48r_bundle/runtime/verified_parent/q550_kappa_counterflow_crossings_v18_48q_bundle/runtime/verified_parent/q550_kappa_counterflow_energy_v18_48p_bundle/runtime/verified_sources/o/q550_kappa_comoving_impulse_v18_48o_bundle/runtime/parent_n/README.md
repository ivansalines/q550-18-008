# Q550 v18.48n — Forward/Backward Transport & Phase-Lag Audit

## Purpose

Measure the *rhythm of the transport* using the eight authentic full 11D Q550 initial-value trajectories and historically transported covectors from v18.48h, preserved through the fully authenticated v18.48m sendback. Compare the actual forward historical observer with the **instantaneously evaluated** near-cancellation subspace at every common phase-clock section. No independent Q550 integrations and no artificial state trajectories.

## Exact scientific separation

This study is a sampled **forward history versus moving geometry** diagnostic. The reverse-order readout **does not simulate physical motion against the flow**. The resulting discrepancies cannot establish energetic irreversibility, dissipation, or a fundamental arrow of time. The local source norms \(\|Bg\|\) and \(\|Cg\|\) are projected Hessian contractions, **not measured physical energies**.

The 41 sections per original physical path have `xi=3.5..4.5` in steps of 0.025. The lifted Theta clock evolves exactly as `dTheta/dxi=0.844357915384206 rad/xi`. This is a model phase clock, not seconds.

At each section the code reads the genuine 11D state `y(xi)` and the propagated 11D cotangent covector `g(xi)` from v18.48h; it constructs the 10D frozen-chart analytic Hessian maps `B(xi)` and `C(xi)`. Source-active and near-null projector subspaces use **exactly the numerical threshold definitions** of v18.48m. Main source thresholds 1e-6 and 1e-10; generalized cancellation threshold 1e-2.

## Measured signals

1. **Historical observer:** `R(g)=(||Bg||+||Cg||)/||Bg+Cg||`, cosine of contribution opposition, source imbalance and \(\|Bg+Cg\|/\|(Bg,Cg)\|\), with four independently transported covectors for context.
2. **Subspace rhythm:** projector Frobenius step pace `||P_{i+1}-P_i||F / Δxi`, historic cotangent line angular speed `angle([g_i],[g_{i+1}])/Δxi`, alignment mismatch `1 - ||P_i g_i||²`, and rank flags. The audit additionally checks whether the historical observer has appreciable overlap with either the source-active or near-cancellation plane; very low overlap makes the directed alignment comparison insensitive. Angles are chart-defined and different from physical body rotation.
3. **Signed forward/back anchor cost:** `D_forward = (1-||P_b g_a||²) - (1-||P_a g_a||²)` versus `D_backward = (1-||P_a g_b||²) - (1-||P_b g_b||²)`. Their difference captures the historically differing anchor covectors. They do **not** quantify physical energy expenditure.
4. **Reverse-snapshot null control:** `||P_b-P_a||F = ||P_a-P_b||F` exactly. Reversing section order changes no undirected projector gap. Thus a forward/back disagreement needs a genuinely directed reference/history or actual reverse IVP to be meaningful.
5. **Exploratory cross-lags:** for 40 per-interval measurements, scans phase shifts `-6..+6` samples (±0.15 xi, ±0.12665 rad) comparing instantaneous projector pace and history-anchored observer speed/cancellation change. Positive lag means the second signal appears *later* than the first by this signed shift. Circular shift comparisons guard against mistaking smooth short traces for detected causal delays; these are descriptive, not independent probabilistic proofs.

## Run on server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_dance_rhythm_v18_48n_bundle.zip
cd q550_kappa_dance_rhythm_v18_48n_bundle
bash run_on_server.sh 2>&1 | tee v18_48n_server.log
```

Override Python binary with `Q550_PYTHON=python3.13`; main options include `--source-cutoffs 1e-6,1e-10 --cancel-cutoff 1e-2 --max-lag-steps 6`. Needs numpy, scipy, mpmath, matplotlib. Authenticating the nested parent v18.48m→k→j→i→h ZIPs and all original source checksums is mandatory and built in. No external orbit cache links.

## Output genealogy

- `results/rhythm_states.csv`, `results/rhythm_steps.csv`, `results/lag_correlations.csv`, `results/lag_summary.csv`, `results/rhythm_events.csv`, `results/report.json`.
- `results/*.png` are made only from those CSVs.
- Complete scripts in `scripts/`, tests in `tests/`, exact nested historical parent `inputs/v18_48m_original_server_sendback.zip`, source hashes in `inputs/SOURCE_PINS.json`, environment and scientific decision rules.
- A new `sendback.zip` and `SHA256SUMS_OUTPUT.json` are produced on each authentic run. The original v18.48m source artifact is never modified.

## Interpretation boundary

Crest lag need not mean a constitutive delay: source and observer both evolve on the same 11D Q550 IVP. Numeric thresholds select the near-null subspace. Long-window/alternate-threshold stability and an **independent reverse-time physical IVP**, with a controlled material energy functional and initial/final constraints, would be required for a genuine physical anti-flow energy imbalance.
