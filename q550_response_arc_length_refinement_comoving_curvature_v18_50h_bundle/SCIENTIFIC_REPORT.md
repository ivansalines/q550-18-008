# v18.50h — Scientific Report

## Provenance and numerical protocol

This experiment is a new physical Q550 ODE integration campaign, not a fit to the coarse v18.50g ledger. The server sendback of v18.50g is embedded byte-identically and contains nested v18.50f and v18.50e ancestry. The original v18.50e integration code was executed unchanged. We processed 10 natural-turn and 10 common-seed protocols: κ₀ original and autonomous, cubic durations 0.18, 0.24, 0.327375, and 0.50, plus quintic 0.24. The hidden response vector lives in the common normalized four-component coordinate chart inherited from v18.50c. There are 33 time observations per case, with a 0.05 evolution horizon.

Numerical run results: 20 successful protocols, 660 dense response observations, 60 short physical integration IVPs (plus a separate 6-IVP targeted early zoom), 0 integration failures. The maximum relative disagreement of the 5 overlapping original v18.50e response vectors was 5.0320e-11. The underlying linearized response-vs-centered-IVP comparison had maximum relative discrepancy 1.8664e-06.

## Actual nested polygonal arc-length

For `same_seed, original κ₀=1/6, cubic r=0.24`, measured in the declared common 4D chart:

| Integrated samples | Polygonal chord sum |
| ---: | ---: |
| 5 | 17.992327098249 |
| 9 | 17.996201394237 |
| 17 | 17.997170533435 |
| 33 | 17.997412853657 |

The 17-to-33 increment is about 0.0013464% of the 33-sample length; the 5-to-33 change is about 0.028258%. The endpoint chord is 17.915564601845 and the straightness is 0.99545222. The curve is almost, not exactly, a straight chord in this metric. These are *polygonal lower bounds* on the continuous arc-length.

## An earlier cancellation peak that five samples missed

At the five inherited v18.50g horizons, relative cancellation was 0%, 14.51%, 8.72%, 6.65%, 5.58%. At 33 samples on the same Q550 system, all 20 cases had their largest *sampled* cancellation at the first positive Δξ=0.0015625, so this grid alone did **not** resolve the true early maximum.

A separate 160-point physical refinement within Δξ in [0.000025,0.004], original κ₀, cubic r=0.24, same initial state, found its largest sampled relative cancellation **0.5793750** (57.93750%) at Δξ **0.001075**, bracketed by measured neighbors Δξ=0.00105 and 0.00110. This is an empirical finite-grid bracket in the declared vector ledger, **not** a proven continuous derivative-zero or physical clock. The early peak is not a discovered new energy source: it follows the relative opposition and changing magnitudes of inherited bookkeeping vectors L and T, where R=L+T.

## Interpretation

Increasing sampling resolution does not overturn the g's statement that the full response curve is nearly chord-like in the inherited metric. Instead it reveals that its *composition* can be sharply nonuniform at very early elapsed evolution. Almost-straight total transport and a strong, short-lived relative cancellation are compatible. The original five-point observation was not wrong at its sample times; it simply missed the earlier maximum.

## What is not shown

No physical material memory, topological cubic packing, absolute physical tangent angle, causal mechanism, new universal timing marker, continuous arc-length bound from above, or discontinuous regime boundary has been proved. The early peak's exact continuous location and robustness to alternative perturbation amplitudes, coordinate charts and deeper temporal refinement remain testable open questions.

Classification: `DENSE_Q550_SAMPLED_RESPONSE_CURVE_WITH_EARLY_PEAK_DIAGNOSTIC_NOT_CONTINUOUS_ARC_OR_PHYSICAL_MEMORY_CERTIFICATE`.
