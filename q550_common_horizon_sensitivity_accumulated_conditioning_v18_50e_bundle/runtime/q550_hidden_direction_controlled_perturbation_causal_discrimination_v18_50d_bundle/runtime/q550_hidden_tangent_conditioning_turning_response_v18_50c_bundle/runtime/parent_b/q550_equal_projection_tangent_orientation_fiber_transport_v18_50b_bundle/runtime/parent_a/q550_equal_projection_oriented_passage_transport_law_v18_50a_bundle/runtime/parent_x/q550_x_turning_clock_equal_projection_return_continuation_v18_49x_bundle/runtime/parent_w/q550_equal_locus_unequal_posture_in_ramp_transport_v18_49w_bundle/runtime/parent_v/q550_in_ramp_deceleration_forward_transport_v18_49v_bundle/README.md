# Q550 v18.49v — In-Ramp Deceleration & Forward Transport Audit

**Purpose:** measure actual 11D Q550 motion while the externally imposed drive clock passes from +1 through 0 to −1, rather than observing only the post-ramp interval as in v18.49u. This is an audit of *movement during braking*, not an assumption that any material speed must decrease.

## Reproduction

```bash
cd /root/elab1/hysteresis
unzip q550_in_ramp_deceleration_forward_transport_v18_49v_bundle.zip
cd q550_in_ramp_deceleration_forward_transport_v18_49v_bundle
bash run_on_server.sh --smoke 2>&1 | tee v18_49v_smoke.log
bash run_on_server.sh 2>&1 | tee v18_49v_server.log
```

Override with `--kind original --ramp-values 0.12 0.327375 --samples 121` to refine the phase grid. `--focus` chooses r=[.12,.327375] and both κ₀ kinds; `--smoke` does one Q550 case. The `--samples` count must be odd so σ=0.5 is explicitly evaluated.

## Provenance

The 2026-10-30 original v18.49u server sendback is included byte-for-byte as `inputs/q550_return_section_continuation_physical_closure_search_v18_49u_authenticated_server_sendback.zip`. `SOURCE_PINS.json` pins its SHA-256; `verify_v_parent.py` also authenticates the original v18.49t, s, r, q, p and earlier code in the nested ancestry. No original RHS, drive or energy ledger is modified. The archive contains effective Python scripts, the parent source, tests, data, charts, a report and SHA hashes.

## Key methodological rules

- In-ramp time is t=σr, σ ∈ [0,1]; at σ=0.5 the **prescribed drive clock** equals zero. Neither intrinsic 10D speed nor spatial transport is required to vanish there.
- The accumulated original 10D path is coordinate-dependent; it does not prove physical volume or forward translation. θ phase returns near its initial ramp value while other coordinates can still move.
- Projector/triad quantities require nondegenerate eigenvalues; at the exact turn start the Cauchy–Green tensor is the identity. Undefined spectral samples are explicitly recorded rather than imputed.
- The separate `cyclic_phase_quadrant_packing_rule_v10.pdf` is a proposed lens, not a dynamical assumption inserted into Q550.
- No closure or material-memory certificate is claimed.

## Outputs

`results/in_ramp_phase_resolved.csv`, `results/in_ramp_case_summary.csv`, `results/spectral_undefined_samples.csv` (if needed), `results/report.json`, `SCIENTIFIC_REPORT.md`, plots, `SHA256SUMS_OUTPUT.json`, `sendback.zip`.

## Local verification (2026-10-30)

- 8 genuine return integrations (2 κ₀ kinds × 4 ramp durations: 0.12, 0.24, 0.327375, 0.50); 488 in-ramp samples including 8 degenerate t=0 sections, no physical IVP failures.
- Material-coordinate rate at σ=0.5 remains positive in all cases; at r=0.327375 and original κ₀ it is 2.338309475 in original coordinate units per ξ. The external clock sign at σ=0.5 is exactly zero.
- At the same case the 10D coordinate path accumulates 0.770685819 by σ=1 while Θ ends at the same lifted phase at which it began the ramp. This is **not** a physical-space displacement or memory certificate.
- Initial-kinetic-frame 6–7–8 triad relative rotation at r=0.327375 (original κ₀), from fixed σ=0.1 to σ=1, is 5.653515° for 61 samples. 121-sample refinement gives 5.653566° (difference 0.0000505°), not an interval bound.
- Maximum original 11D mechanical balance error across cases: 4.39e-12; max signed clock mismatch 6.66e-16.
