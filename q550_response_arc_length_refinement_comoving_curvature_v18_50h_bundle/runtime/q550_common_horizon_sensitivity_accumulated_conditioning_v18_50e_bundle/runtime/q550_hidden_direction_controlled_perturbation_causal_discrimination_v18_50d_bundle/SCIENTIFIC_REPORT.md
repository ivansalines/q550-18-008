# v18.50d — Hidden-Direction Controlled Perturbation & Causal Discrimination Audit

**Classification:** `CONTROLLED_IN_MODEL_SENSITIVITY_NOT_ESTABLISHED_PHYSICAL_CAUSALITY_OR_MATERIAL_MEMORY_CERTIFICATE`

## What was actually intervened on

The authentic v18.50c cases determine the natural x-turning state. From precisely the SAME baseline state and at the SAME event, symmetric ±ε interventions are made separately to (1) the logit coordinate y[8] of x, (2) angular coordinate θ₁=y[2], or (3) the prescribed drive clock via a compact phase bump whose phase AND rate differences vanish at the endpoints. The historical physical RHS is not modified. The structural hidden jet and one pooled metric reproduce v18.50c.

The drive clock pulse is not amplitude-equivalent to a unit logit or angular-state kick, so raw gains must not be ranked as physical strengths. State kicks generally change initial energy and are mathematical interventions, not a proposed experimental actuator.

## Numerical evidence

- Source sendback SHA-256: `fee1f596db2d63de8a0278240e65c273dd0a337c00f7e8df688ce24b78d0142f`.
- Cases: 10; 11D perturbed IVPs: 180; failed cases: 0.
- Largest relative centered-derivative drift across the tested amplitudes: 0.00018598869.
- Analytic structural x→hidden RHS Jacobian versus independent physical-RHS finite difference, maximum relative discrepancy: 3.7783393e-11.
- The external drive pulse returns the prescribed phase to the baseline at its end: True.

### Original κ₀, cubic ramp (smallest perturbation ε)

| Ramp r | ∥∂ε ûh∥ from x kick | θ₁ kick | drive pulse | hidden-rate response share for x kick |
|---:|---:|---:|---:|---:|
| 0.18 | 16.494052 | 2.2758596 | 0.00084600818 | 97.07% |
| 0.24 | 17.712372 | 2.4970207 | 0.00090910263 | 98.13% |
| 0.327375 | 18.599143 | 2.6638398 | 0.00095503112 | 98.88% |
| 0.5 | 19.250373 | 2.7907611 | 0.00098868385 | 99.38% |

### Shape control at r=0.24 (original κ₀)

| Shape | x-kick gain | θ₁-kick gain | drive-pulse gain |
|---|---:|---:|---:|
| beta:2:2 | 17.712372 | 2.4970207 | 0.00090910263 |
| beta:3:3 | 17.961927 | 2.5425593 | 0.00091978015 |

## Decision: conditioning versus correlation

**Supported:** Within the authenticated Q550 model, the structural Jacobian of hidden field components with respect to x-logit is nonzero and independently checked by finite differences. Reintegrating with x-only kicks produces a nonzero hidden-direction response in all tested ramps. An independent θ₁ kick and a matched-endpoint drive pulse produce distinct response families. Local gains vary smoothly over the investigated amplitudes and ramp durations; no discontinuous regime boundary has been detected in that small range.

**Not supported:** The intervention does not prove that a physically separate x actuator exists, that x alone caused the observed natural turning, or that the spatially hidden sector is a physical fiber. Nor does the scan rule out thresholds outside the tested range or demonstrate the cubical quadrant construction. The direction response is chart- and metric-dependent.

## Figures and numerical files

- `controlled_hidden_direction_gain.png`: gain by intervention and ramp.
- `hidden_sensitivity_coordinate_partition.png`: angular versus angular-rate response.
- `sensitivity_vector_direction_continuation.png`: orientation changes of sensitivity vector.
- `amplitude_and_shape_sensitivity.png`: amplitude and quintic/cubic controls.
- `controlled_intervention_responses.csv`: full symmetric perturbation ledger.
- `source_jacobian_at_turning.csv`: local structural cross derivative and independent RHS check.
- `amplitude_linearity_checks.csv`: finite-amplitude drift.

## Next discriminating question

Can the direct x→hidden cross-Jacobian contribution be ablated or shadowed while holding the same clock and starting state, and can an independently maintained hidden response survive that change? Such an experiment must declare that it changes the model and cannot be silently called physical transport.
