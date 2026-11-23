# Q550 — v18.50d: Hidden-Direction Controlled Perturbation & Causal Discrimination Audit

Run the exact authenticated Q550 physical RHS starting from natural turning events extracted from the v18.50c original server sendback. All internal documents, comments and scripts are in English.

## Installation / reproduction

```bash
cd /root/elab1/hysteresis
unzip q550_hidden_direction_controlled_perturbation_causal_discrimination_v18_50d_bundle.zip
cd q550_hidden_direction_controlled_perturbation_causal_discrimination_v18_50d_bundle
bash run_on_server.sh 2>&1 | tee v18_50d_server.log
```

CLI examples:

```bash
python3.13 scripts/run_audit.py --smoke --fail-fast
python3.13 scripts/run_audit.py --kind original --ramps 0.18 0.24 0.327375 0.5 --amplitudes 1e-5 1e-4 1e-3
```

The run verifies and recursively unpacks parent archives in `runtime/` but does not include transient runtime in sendbacks. The input c ZIP is byte-identical to the authenticated user sendback; the output ZIP root and its filename contain the full versioned descriptive audit name.

The default run executes 10 ramp/κ0/shape cases and 180 positive/negative perturbed IVPs, plus authentic baseline replays. The primary finite-difference observable is the response of the normalized four-component hidden structural jet under one common pooled coordinate scale.

Three distinct interventions: (a) small kick of the x logit y[8], (b) angular theta1 kick y[2], (c) compensated drive-clock pulse with zero endpoint phase displacement. The interventions are not equivalent in physical units and do not imply an experimentally available control. The clock-pulse amplitude is a peak-rate scale; state-kick amplitudes are state chart coordinates.

**Do not interpret these responses as independent evidence of physical causality or material memory.** See SCIENTIFIC_DECISION_RULES.md and SCIENTIFIC_REPORT.md.
