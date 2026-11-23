# v18.49q — Coupled Handover Geometry & Residual Transport Audit

## Verdict

Authentic Q550 re-integration and fixed-reference kinetic-frame numerical audit. The **6–7 / 7–8 handover is accompanied by substantial other-channel transport**, and the two adjacent rank-pair generators do not close the full material-eigenspace projector evolution. In all sampled cases the full 45-pair generator reconstructs the observed projector transport at the chosen numerical resolution far better than the selected pair-only generators.

This result does **not** establish an independently physical torsional flip, a material transfer of eigenvectors, or a new non-Abelian fundamental force. The Lie bracket is a kinematic identity inside the ordered eigenspace representation; 6–8 is also an independently measured instantaneous component.

## Phase-resolved evidence

| κ₀ | r | Handover q* | D67 at 0.65 | D78 at 0.65 | Other 43 at 0.65 | Full projector error | Two-pair-only error |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | 0.326718750 | No crossing | 30.9128% | 28.0010% | 41.0862% | 1.382e-07 | 0.114605 |
| original | 0.327375000 | 0.64987618387 | 29.3811% | 29.9292% | 40.6897% | 1.434e-07 | 0.115187 |
| original | 0.330000000 | 0.64672455062 | 23.3324% | 38.2481% | 38.4196% | 1.674e-07 | 0.117548 |
| autonomous | 0.327375000 | 0.64971888317 | 29.1002% | 30.3483% | 40.5515% | 1.446e-07 | 0.115314 |
| autonomous | 0.330000000 | 0.64656781372 | 23.0560% | 38.7156% | 38.2284% | 1.689e-07 | 0.117680 |

Events: **4** in **5** authenticated cases. These are numerical phase-bracketed roots, not formal interval enclosures.

## The geometry of the coupled channels

At fixed q and in a fixed initial kinetic frame, write `K = K67 + K78 + Kother`. Here `Kother` is the sum of **43 genuine measured pair terms**, including the directly measured `K68`, and NOT a numerical error. The generator reconstruction error is at most 6.8513061e-16; the commutator calculation is gauge-sign invariant for each eigendirection.

Because both selected channels share rank 7, `[K67,K78]` lies in the rank-6/rank-8 rotation plane. This is a Lie-algebra identity (units phase⁻²). The directly measured `K68` is a distinct rate (units phase⁻¹), **not** equal to the bracket without an independently specified phase-integration model.

Define the three-rank subspace projector `S678=P6+P7+P8`. The two selected instantaneous terms satisfy `[K67+K78,S678]=0`, whereas the other 43 generally satisfy `[Kother,S678]≠0` and can move that subspace. Over q∈[0.63,0.65], finite transports are integrated by matrix exponentials using the authentic K(q) in one common frame. The full transport accurately predicts each rank projector, whereas truncation misses part of the evolution.

Truncated finite transport is *not* uniquely decomposable into independent physical causes. `||Ufull - U2 Uother||` measures one chosen ordered splitting and non-commutative/time-order effects; it is not a unique invariant memory observable.

## Numerical and genealogy controls

- True 11D forward/return replay and 10D tangent transport: {'physical_forward_11D': 2, 'physical_return_11D': 5, 'tangent_10D': 5}.
- Parent v18.49p ZIP manifest and nested v18.49o→v18.48j genealogy verified: True.
- Maximum parent endpoint discrepancy: 3.3306691e-16.
- Minimum relative spectral gap: 0.060617804.
- Max projector derivative central-difference residual: 2.0186779e-07.
- Max full-transport step-refinement difference: 5.1398748e-07.
- Max 11D ledger error: 1.3353662e-11.

## Output and reproducibility

`results/phase_resolved_geometric_ledger.csv` lists phase-sampled instantaneous channels and commutators. `results/numerical_handover_geometry_events.csv` lists genuine phase-root replay, parent regressions and 6–8 bracket/observed measures. `results/report.json` contains all numerical controls, transport errors, limitations, and source proof. All original source is encapsulated in authenticated v18.49p ZIP, scripts regenerate all v18.49q outputs, and the archive manifest SHA-256 binds every deliverable.

## Scientific boundary

Only the registered q-window, selected durations, and inherited kinetic frame are tested; conclusions are not global over all ramp shapes, phases, observers or κ₀ values. No interval proof of all roots, physical non-Abelian connection, causal transfer or independent torsional flip follows from these numerical measurements. In particular, the instantaneous 43-pair remainder is nonzero **by measurement**; the instantaneous full reconstruction error is near zero **by algebra**.
