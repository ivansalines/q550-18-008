# Q550 v18.49w — Equal-Locus, Unequal-Posture & In-Ramp Transport Audit

An executable descendant of the **authentic v18.49v Q550 server sendback**, retaining the entire upstream embedded genealogy as source input. The scripts recalculate real physical 11D return trajectories and 10D spectral projectors during the drive ramp, then compare *non-adjacent* sections.

## Run in `/root/elab1/hysteresis`

```bash
unzip q550_equal_locus_unequal_posture_in_ramp_transport_v18_49w_bundle.zip
cd q550_equal_locus_unequal_posture_in_ramp_transport_v18_49w_bundle
bash run_on_server.sh 2>&1 | tee v18_49w_server.log
```

Python requirements: numpy, scipy, matplotlib. Python 3.13 preferred; Python 3 works if dependencies are present. The included `run_on_server.sh` runs unit tests, recomputation, figures, report and a full hashed `sendback.zip`.

For a single-case smoke test: `python3 scripts/run_audit.py --smoke --fail-fast`. Option flags: `--kind original|autonomous|both`, `--ramp-values ...`, `--samples 61`, `--min-separation 0.2`, `--x-fraction 0.1`, `--locus-fraction 0.2`.

## Main outputs

- `results/sampled_states_11d_projection.csv`: all sampled locus and posture coordinates with spectral availability markers.
- `results/all_separated_pairs.csv`: pairwise state/projection comparison, including declared coordinate thresholds.
- `results/equal_clock_phase_mirror_pairs.csv`: symmetric points with exact imposed clock-phase equality.
- `results/case_summary.csv`, `results/report.json`: numerical counts, candidate extrema and controls.
- `results/*.png`: graphics made by the bundled `scripts/plot_results.py`.
- `SCIENTIFIC_REPORT.md` and `SCIENTIFIC_DECISION_RULES.md`: limits and decision criteria.
- `SHA256SUMS_OUTPUT.json` and `sendback.zip`: source and output hashes.

**Scope:** A diagnostic of near-equal coordinate projections and unequal dynamic postures; not a physical memory or volume certification. The autonomous cube/quadrant note is not imposed on Q550.
