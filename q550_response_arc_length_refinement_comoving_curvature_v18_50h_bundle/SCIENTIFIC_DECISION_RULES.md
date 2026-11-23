# v18.50h — Scientific Decision Rules

- **ANCESTRY:** All manifested members of g, f, and e must pass SHA-256 and CRC; e must recursively authenticate d and deeper solver ancestry. Fail closed on mismatch.
- **AUTHENTIC_REPLAY:** All new samples originate from the original Q550 ODE solver, with an identical state kick, base trajectory, metric, and original ramp protocol. No interpolated points count as new physical samples.
- **REGRESSION:** The 5 overlapping parent horizons must reproduce the inherited v18.50e vectors to a relative error below 2e-5. Record actual maximum error.
- **NESTED_ARC:** The 5, 9, 17, 33-point chord sums must be nondecreasing (with tolerance 1e-9) at a common horizon and metric. All values are lower bounds, not the exact continuous arc.
- **PEAK:** A maximum at the first positive dense sample is flagged as **unresolved**. A further targeted ODE sample may localize the sampled peak; a sampled bracket is not a rigorous uniqueness or stationary-point proof.
- **COORDINATE:** Gauge/metric-dependent response angles and decomposition fractions are identified explicitly. No physical attribution to one scalar, volume, hidden-state causality or energy exchange is made.
- **NEGATIVE RESULTS:** No sharp transition detected on a sampled interval is not a global nonexistence theorem.

Classification: `DENSE_Q550_SAMPLED_RESPONSE_CURVE_WITH_EARLY_PEAK_DIAGNOSTIC_NOT_CONTINUOUS_ARC_OR_PHYSICAL_MEMORY_CERTIFICATE`.
