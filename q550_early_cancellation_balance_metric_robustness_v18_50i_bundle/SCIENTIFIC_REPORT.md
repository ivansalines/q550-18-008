# Q550 v18.50i — Early Cancellation Balance & Metric-Robustness Audit

## Scientific status

**Classification:** `IN_MODEL_EARLY_CANCELLATION_METRIC_AND_AMP_STRESS_NOT_PHYSICAL_INVARIANCE_OR_MEMORY_CERTIFICATE`.

This numerical audit was performed on the original Q550 11D driven dynamics and the structurally defined 4D hidden response jet, using the authenticated v18.50h genealogy (and its preserved v18.50e solver). The early effect is neither new physical conservation nor a certified material instability.

## Reproducibility and intervention

Both model input families were rerun: original κ₀ = 1/6 and autonomous κ₀ = 7π/132 ≈ 0.16659961041764054. Each uses its own natural x-turning state at cubic ramp duration 0.24, not a common-state parameter intervention. For each family, seven IVPs were integrated from one baseline and three symmetric pairs of x-logit interventions, amplitudes ε = 1e−5, 1e−4, 1e−3. Overall, **14 new short physical IVPs** and **4,890 ledger rows** were produced, all within the same phase-coordinate system. The early interval was Δξ = 0.000025..0.004 with 160 equally spaced samples, plus the historical checkpoints 0.0125 and 0.05 and the exact initial horizon.

At each time the response is decomposed in the declared endpoint coordinate chart as **R = L + T**. Here L is the endpoint derivative along x-logit alone, and T is the derivative along the transported full-state tangent minus that same x-logit basis. For a chart scale s, a hidden 4-vector v is represented as (v/s)/||v/s||; all component norms and angles below use its Euclidean chart norm. No decomposition term is a separately identified physical force or path mechanism.

Define

\[
C=\frac{\|L\|+\|T\|-\|L+T\|}{\|L\|+\|T\|}, \qquad b=\frac{\|T\|}{\|L\|},\qquad c=\frac{\langle L,T\rangle}{\|L\|\,\|T\|}.
\]

## Main observations

**Two κ₀ families reproduce the early cancellation in the original declared common metric.** The sampled maximum occurs at the same sampled horizon Δξ = 0.001075 for both:

| Input family | C (%) | ||L|| | ||T|| | b = ||T||/||L|| | cos(L,T) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original 1/6 | 57.937502 | 0.3258304 | 0.3306684 | 1.01485 | −0.64624 |
| Autonomous 7π/132 | 57.930145 | 0.3258896 | 0.3308550 | 1.01524 | −0.64612 |

The maximum is bracketed by neighboring sampled horizons 0.00105 and 0.00110. This is **not** an interval-certified stationary root or a uniqueness certificate. The maximum absolute regression difference from the authentic h zoom in the original common metric is 3.27e−9 over 163 shared checkpoints.

**Metric stress changes the peak markedly.** For original κ₀ (ε=1e−4):

| Declared chart | Peak C (%) | Peak Δξ | Character |
| --- | ---: | ---: | --- |
| Historical pooled common chart | 57.94 | 0.001075 | interior sampled maximum |
| Raw coordinates | 2.62 | 0.004000 | boundary maximum; no interior peak established |
| Angular coordinates weighted 2× | 57.45 | 0.001475 | interior sampled maximum |
| Angular rates weighted 2× | 64.61 | 0.000725 | interior sampled maximum |

The autonomous family closely reproduces this pattern (its pooled value is 57.93%; raw 2.62%; angles 57.44%; rates 64.61%). A uniform rescaling by 3 of every component of the pooled chart changes C by less than 1e−8 as expected, since it does not change the normalized direction.

**A narrower result is more robust:** the dot product L·T is negative in all **1,280 positive-horizon observations** across both κ₀ families and the four nonredundant charts at ε=1e−4. It is an orientation statement within the explicitly tested diagonal charts, **not** invariance under all possible metrics. The nearly equal norms at the *pooled-metric* peak are not robust under the raw-coordinate chart.

**Kick amplitude dependence is small within the tested perturbative range.** All three ε reproduce the same sampled maximum locations within each declared chart. The largest shift in C at the pooled-chart peak from ε=1e−5 to 1e−3 is below 5e−9 in absolute fraction. This finite-amplitude stability does not exclude nonlinear changes at much larger kicks.

## Numerical verification

- Five Python geometry unit tests pass.
- No physical IVP failure was registered; 14 integrations.
- The local/transport vector split is tested against the independent centered finite-kick observable. The largest relative discrepancy over all recorded rows is 2.11e−4, and over the historical h reference comparison it is not larger than the predeclared 2e−5 cancellation regression threshold.
- 163 original common-chart checkpoints reproduce the authenticated v18.50h zoom within 3.27e−9 in cancellation fraction.
- The authentic h archive is checked by SHA-256 (29/29 entries) and CRC; its nested ancestry is verified before the solver is loaded.

## Conclusion and limits

The early cancellation is reproducible under both specific κ₀ input choices and three small kick amplitudes. **Its peak magnitude and phase are not metric-robust.** The angular opposition persists under the four stated finite diagonal coordinate charts, but no metric-independent topology, physical chiral direction, material memory, or regime transition has been established. The next measurement, if wanted, should test whether a more intrinsic state-space metric and parallel-transport convention preserve the local-versus-transport opposition before claiming a stronger invariant.

Regenerate the report and figures with `bash run_on_server.sh` or `python3 scripts/run_audit.py`; use the script source and CSV ledgers as the executable record. The present report summarizes results from the corresponding authenticated run, not a substituted physical model.
