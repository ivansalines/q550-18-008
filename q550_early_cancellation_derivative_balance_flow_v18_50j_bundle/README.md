# Q550 v18.50j — Early Cancellation Derivative Balance & Response-Flow Audit

This audit investigates the order and derivative balance of three distinct events observed in v18.50i:
(1) equality of the local and transported sensitivity norms; (2) the stationary point of their normalized cancellation; (3) the growth of the resultant response. It **does not integrate a new physical trajectory**. The authenticated v18.50i input is included in full, preserving all earlier executable genealogy.

## Reproduce

```bash
cd /root/elab1/hysteresis
unzip q550_early_cancellation_derivative_balance_flow_v18_50j_bundle.zip
cd q550_early_cancellation_derivative_balance_flow_v18_50j_bundle
bash run_on_server.sh 2>&1 | tee v18_50j_server.log
```

Python requirements: `numpy`, `scipy`, `matplotlib` (standard `csv`, `json`, `hashlib`, `zipfile`). Override Python with `Q550_PYTHON=python3.13` if appropriate. `run_on_server.sh` authenticates the embedded original v18.50i ZIP (CRC and all 18 SHA-256 manifest entries), reads its 4,890 vector records, differentiates 30 finite sampled curves, performs pure mathematical and event checks, redraws the figures, and verifies the full v18.50j file manifest.

## Results

- `results/derivative_balance_events.csv` — all 30 κ₀ × chart × ε summaries, brackets, interpolated roots, derivatives, and limitations.
- `results/derivative_balance_phase_ledger.csv` — 4,800 positive-horizon sample rows including the separately differentiated norm-ratio and angular contributions.
- `results/report.json` — automated synopsis, provenance and classification.
- `results/original_event_order.png`, `results/autonomous_event_order.png`, `results/derivative_competition_reference.png`, `results/metric_event_order.png`.
- `SCIENTIFIC_REPORT.md` and `SCIENTIFIC_DECISION_RULES.md` — scope, interpretation and precise limitations.
- `tests` and `scripts` — actual executable source used.

## Method and units

The observable is a **chart-defined four-vector sensitivity** to a small `x`-logit kick. The split `R=L+T` is the endpoint-directional plus transported-state decomposition defined in v18.50i. With `b=||T||/||L||` and `c=cos(L,T)`, cancellation is `C=1-sqrt(1+b*b+2*b*c)/(1+b)`. The derivative with respect to the **model horizon Δξ** splits exactly into a norm-balance and an orientation term (explicit formulas in `SCIENTIFIC_REPORT.md`).

Cubic-spline derivatives and event roots are **numerical interpolants of the finite v18.50i grid**, not rigorous continuous event/root certifications. In particular a cubic interpolant must not be treated as new solver data. Different charts reweight the sensitivity coordinates and give different maxima. The reference comparison with elastic/viscous/hardening stress curves of Singh–Ginzburg–Zaccone is conceptual only; the Q550 curves are neither material stresses nor validated constitutive laws.

**Classification:** `VERIFIED_PARENT_DERIVATIVE_FLOW_INTERPOLATION_NOT_CONTINUOUS_ROOT_OR_CONSTITUTIVE_PHYSICS_CERTIFICATE`.
