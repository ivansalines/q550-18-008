# Q550 — v18.50e: Common-Horizon Sensitivity & Accumulated Conditioning Audit

An executable follow-up to v18.50d. All scripts, generated reports and comments are in English. The full authenticated server sendback from v18.50d is retained byte-for-byte in `inputs/`; the nested ancestors and Python solver are authenticated recursively before integration. Regenerated `runtime/` directories are deliberately excluded from distributions.

## Execute on the original server

```bash
cd /root/elab1/hysteresis
unzip q550_common_horizon_sensitivity_accumulated_conditioning_v18_50e_bundle.zip
cd q550_common_horizon_sensitivity_accumulated_conditioning_v18_50e_bundle
bash run_on_server.sh 2>&1 | tee v18_50e_server.log
```

Or a quick smoke on the original κ₀, cubic r=0.24:

```bash
python3.13 scripts/run_audit.py --smoke --fail-fast
```

**Warning:** running `--smoke` overwrites results in the extracted directory with a 2-case subset. Run the complete audit again to regenerate the full outputs before packing. CLI: `--kind {both,original,autonomous}`, `--horizons 0.0125 0.025 0.0375 0.05`, `--epsilon 1e-4`, `--rtol`, `--atol`, `--max-step`, `--fail-fast`.

## What is controlled

A. Natural-turn comparison: authentic turning states for each of the 10 protocols from v18.50c, identical post-event elapsed horizons (not identical starting states).

B. Same-seed comparison: for each κ₀, reuse the full original 11D state at the natural turning of cubic r=0.24, fixing the absolute event instant and initial phase. Different durations and quintic shape change **only the subsequent drive prescription**. Drive phase is rebased so every case starts at the same clock phase.

The tracked scalar is the norm of the centered sensitivity of the 4D normalized hidden structural jet with respect to a symmetric logit-x state kick, computed in the **one pooled diagonal metric** from v18.50c. The linearized ledger separates an endpoint-x coordinate derivative and the component arising from transport of the perturbation through the coupled 10D state. This is **a coordinate bookkeeping decomposition**, not independent physical cause, universal bifurcation, material memory, volume, or proof of the eight-octant hypothesis.

**Reproducibility:** use `scripts/run_audit.py`, `scripts/response_math.py`, `scripts/plot_results.py`, `scripts/generate_report.py`, `scripts/pack_sendback.py`, `scripts/verify_parent_d.py`; test suite and requirements included. `SHA256SUMS_OUTPUT.json` is an explicit digest manifest. Parent ZIP byte SHA-256 is pinned inside `verify_parent_d.py`.
