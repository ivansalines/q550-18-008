# Q550 v18.49g — Clock-Matched Passage Scaling & Full-10D Orientation Audit

**Source status:** authentic 11D Q550 numerical audit with a full executable and SHA-256 authenticated genealogical chain. **Scope:** one `phaseblind` branch 0, two κ₀ values and six ramp durations. The physical equations and input histories are inherited exclusively from the unchanged server-produced **v18.49f** sendback, with its certified parent ancestry back to v18.48j. This is not a universal physics proof.

## Scientific question

Does a contact passage whose selected duration is close to `6/5*kappa0` identify a threshold-independent passage, and does its full-10D transported orientation close (or keep turning) when the 2D projected orientation turns around?

## Three matched clocks / metrics

* `q` is the phase coordinate of the command; it increases against physical drive `Theta`, so `ΔTheta = -omega Δq`, `omega≈0.84436 rad/xi`.
* For each six-ramp 11D return, integrate the exact tangent propagator `Phi(q)` in the material 10D block. Pull the finite-amplitude state difference back into the common initial frame (`Phi^-1 local_lift(y_return,y_forward)`). This *linear* pullback does not turn a finite difference into an exact tangent perturbation.
* Remove the resolved historical five-covector family in the original declared Euclidean reference metric. Follow the normalized remaining 10D vector on `S^9`.
* At threshold-free geometric extrema (left minimum, central maximum, right minimum) and at **every** threshold-defined entry/exit from F, compute full-10D spherical path arclength, direct endpoint angle, and their difference.
* Compare the clock of the 2D maximum (`q≈0.525–0.560`) against the full-10D angle from `q=0.35` on the common window `q∈[0.25,0.75]`. The full-10D maximum is at the **window boundary** (`q=0.75`) in these data, *not* a newly discovered global maximum.

## Reproduction — server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_clockmatched_full10d_v18_49g_bundle.zip
cd q550_kappa_clockmatched_full10d_v18_49g_bundle
bash run_on_server.sh 2>&1 | tee v18_49g_server.log
```

Set `Q550_PYTHON` to override default `python3.13`; dependencies are in `requirements.txt`. The runner executes tests, reconstructs the authenticated ancestry and Q550 dynamics, checks science gates, writes five plots and creates `sendback.zip` with full inputs and source scripts. It is independent of the server's original orbit symlinks. The archive has exactly one root directory.

For a quick subset:

```bash
python3.13 scripts/run_audit.py --smoke
python3.13 scripts/check_outputs.py
```

The `--smoke` option overwrites current CSV results with one original-kappa case; run the complete `run_on_server.sh` afterward to restore the full result set. Never label a smoke run as a full F regression.

## Result files

* `results/threshold_free_extrema_orientation.csv`: 12 profiles, independent of contact threshold. Includes 10D arclength, chord angle, max projected phase and 10D boundary controls.
* `results/clock_matched_threshold_passages.csv`: all 121 intervals inherited from authentic F; compares selected span/kappa, endpoint/path angles, and the historic F calculation.
* `results/full10d_clock_profiles.csv`: 1,212 clock matched samples across the 12 histories.
* `results/report.json`: counts, worst regression errors, parent SHA ancestry, and negative controls.
* Five real plots: clock orientation, 6/5 scaling, extrema scaling, and arc-vs-chord geometry.

## Key negative controls

* Only **2/121** F threshold-based intervals have passage duration/kappa0 within 1% of `6/5`; their value depends on contact threshold.
* The extrema-to-extrema duration normalized by kappa0 stays around **0.462–0.915** in the twelve histories — none at `6/5`.
* In 10D, arclength exceeds endpoint displacement; the projected 2D angular maximum at around `q≈0.54` is not a return of the full 10D direction.
* All numerical statements are floating-point diagnostics with a declared metric, not rigorous interval or global period claims.

## Genealogical integrity

The full original v18.49f server sendback is embedded at `inputs/v18_49f_original_server_sendback.zip`. SHA pin: `inputs/SOURCE_PINS.json`. `scripts/verify_parent.py` authenticates **every** recorded source file of F and invokes its own ancestor verifier through E → D → C → B → A → Z → ... → J, preserving the original Python generators. New Python generators are in `scripts/`, unit tests in `tests/`, new output CSV/figures in `results/`, and generated SHA checksums in `SHA256SUMS_OUTPUT.json`. `runtime/` is an intentionally excluded, automatically rebuilt extraction cache.

**Scientific terminology and code comments are in English.**
