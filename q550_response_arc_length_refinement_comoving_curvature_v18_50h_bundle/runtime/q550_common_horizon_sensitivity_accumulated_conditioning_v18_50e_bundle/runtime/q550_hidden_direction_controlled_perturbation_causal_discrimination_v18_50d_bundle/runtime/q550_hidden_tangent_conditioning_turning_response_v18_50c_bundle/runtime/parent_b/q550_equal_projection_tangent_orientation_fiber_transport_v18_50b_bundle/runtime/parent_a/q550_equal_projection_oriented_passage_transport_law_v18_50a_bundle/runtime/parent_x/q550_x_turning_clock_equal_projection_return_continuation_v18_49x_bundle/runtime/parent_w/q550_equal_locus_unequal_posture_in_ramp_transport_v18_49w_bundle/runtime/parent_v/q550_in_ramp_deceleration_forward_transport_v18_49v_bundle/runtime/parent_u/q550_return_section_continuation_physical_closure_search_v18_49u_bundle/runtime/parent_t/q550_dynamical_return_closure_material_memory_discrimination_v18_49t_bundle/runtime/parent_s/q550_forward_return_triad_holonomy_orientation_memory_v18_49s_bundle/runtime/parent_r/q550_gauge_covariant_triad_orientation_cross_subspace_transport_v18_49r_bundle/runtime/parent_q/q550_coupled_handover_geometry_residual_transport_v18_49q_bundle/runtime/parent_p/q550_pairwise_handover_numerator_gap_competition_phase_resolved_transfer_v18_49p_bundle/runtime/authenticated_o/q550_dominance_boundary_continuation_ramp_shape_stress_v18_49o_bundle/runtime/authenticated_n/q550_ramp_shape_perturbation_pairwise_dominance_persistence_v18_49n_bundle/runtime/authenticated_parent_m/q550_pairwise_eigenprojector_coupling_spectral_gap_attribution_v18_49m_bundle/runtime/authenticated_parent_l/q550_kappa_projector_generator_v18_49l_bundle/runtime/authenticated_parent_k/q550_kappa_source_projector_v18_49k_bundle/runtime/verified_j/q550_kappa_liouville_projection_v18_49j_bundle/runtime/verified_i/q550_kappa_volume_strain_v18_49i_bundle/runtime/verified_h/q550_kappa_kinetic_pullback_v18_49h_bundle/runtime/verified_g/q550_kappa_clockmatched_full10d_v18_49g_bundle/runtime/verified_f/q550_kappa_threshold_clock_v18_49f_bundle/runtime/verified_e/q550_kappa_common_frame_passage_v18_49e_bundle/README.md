# Q550 v18.49e — Common-Frame Observer Transport & Kappa0 Passage-Marker Audit

## Scientific question

The original, authenticated v18.49d server results show no direct projected observer-plane closure over `Delta xi=0.2` or `Delta xi=kappa0`. Could there nevertheless be a recognizable **oriented passage** of the contact-lobe geometry, once the historical observer family and material differences are compared in a genuinely transported common tangent frame? This audit tests that question without assuming a complete kappa0 material cycle.

## Actual executable experiment

- Reads the byte-identical original server v18.49d sendback from `inputs/v18_49d_original_server_sendback.zip`, whose SHA-256 is recorded in `inputs/SOURCE_PINS.json`. Its verifier recursively authenticates all original source ancestors back to v18.48j.
- For phaseblind/branch 0 and both original/autonomous kappa0, reintegrates the original outgoing Q550 11D IVP and **six** return ramps `[0.285,0.292,0.296333,0.300,0.305,0.309]`. The return has the original reversal of five material velocities and the same cubic smooth drive history used in v18.49d.
- For EACH of the twelve NEW returns, reintegrates five historical material cotangent observers and independently integrates the full **10x10 material tangent fundamental matrix** from the exact original Jacobian.
- Reconstructs the genuinely common frame at the material turning point using `Phi(t)^(-1)` and `g(t)Phi(t)=g0`. Contrasts a fixed Euclidean initial-frame complement with the instantaneous-chart complement. These norms refer to DIFFERENT metrics and must not be subtracted as if they had the same physical unit.
- Finds sign-bracketed entry/exit roots of physical-shape distance `d3(q)-0.01`, using continuous IVP dense output and Brent refinement. Counts the resulting subthreshold intervals and records their span divided by kappa0 and 0.2. The interval **is not** a physical 11D cycle or an intrinsic period.
- Compares the SAME material difference in the pulled-back initial reference across `q0 -> q0+kappa0` and `q0 -> q0+0.2`. Computes signed orientation cosine, norm ratios, exact drive-clock increments, and independent gauge/duality checks.

## Reproduction on the server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_common_frame_passage_v18_49e_bundle.zip
cd q550_kappa_common_frame_passage_v18_49e_bundle
bash run_on_server.sh 2>&1 | tee v18_49e_server.log
```

Python 3.13, NumPy, SciPy and Matplotlib. Override `Q550_PYTHON` if needed. For a non-delivery smoke test only: `python3.13 scripts/run_audit.py --smoke`; **rerun the complete runner afterwards**, since smoke overwrites result CSVs.

## Executable genealogy

- `scripts/verify_parent.py` — verifies original D sendback SHA, every archive member, and nested sources recursively to J.
- `scripts/run_audit.py` — actual original 11D IVPs, new cotangent/10x10 tangent IVPs, threshold roots, common-frame projections, parent regressions and reports.
- `scripts/frame_math.py` — actual tangent fundamental matrix and independent chart/metric tests.
- `tests/test_frame_math.py` — independent algebraic unit tests.
- `scripts/check_outputs.py` — failing scientific gates and event consistency checks.
- `scripts/plot_results.py` — four numerical plots, driven only from generated CSV results.
- `scripts/pack_sendback.py` — deterministic SHA-256 manifest and sendback archive.
- `results/` — CSV, report, environmental versions and source-driven figures.

## Interpretation boundaries

The term "common frame" denotes the initial turning-point material chart after linear tangent pullback. It is NOT an intrinsically selected physical metric nor the exact nonlinear transport of large finite differences. The historical family of five covectors is fixed initially but the return path is not the original forward path. The experiment does NOT demonstrate an observer-independent kappa0 period or a physical cycle, even if an individual threshold-passage interval happens to have duration close to kappa0. The object is numerical finite-dimensional model geometry on the Q550 phaseblind/branch-0 seed.

See `SCIENTIFIC_DECISION_RULES.md` for falsifiable decision gates.
