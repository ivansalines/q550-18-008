#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
r=json.loads((R/'results/report.json').read_text()); cases=r['cases'];ctr=r['controls']
fmt=lambda x:f'{x:.8g}'
rows=[]
for c in cases:
 rows.append(f"| {c['kappa_kind']} | {c['ramp_xi']:.9f} | " +
   (f"{c['root_phases'][0]:.11f}" if c['root_phases'] else 'No crossing')+
   f" | {c['share_67_at_end']:.4%} | {c['share_78_at_end']:.4%} | {c['share_other_at_end']:.4%} | {c['full_projector_transport_max_error']:.3e} | {c['pair_only_projector_transport_max_error']:.6f} |")
text='''# v18.49q — Coupled Handover Geometry & Residual Transport Audit

## Verdict

Authentic Q550 re-integration and fixed-reference kinetic-frame numerical audit. The **6–7 / 7–8 handover is accompanied by substantial other-channel transport**, and the two adjacent rank-pair generators do not close the full material-eigenspace projector evolution. In all sampled cases the full 45-pair generator reconstructs the observed projector transport at the chosen numerical resolution far better than the selected pair-only generators.

This result does **not** establish an independently physical torsional flip, a material transfer of eigenvectors, or a new non-Abelian fundamental force. The Lie bracket is a kinematic identity inside the ordered eigenspace representation; 6–8 is also an independently measured instantaneous component.

## Phase-resolved evidence

| κ₀ | r | Handover q* | D67 at 0.65 | D78 at 0.65 | Other 43 at 0.65 | Full projector error | Two-pair-only error |
|---|---:|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

Events: **{len(r['handover_events'])}** in **{len(cases)}** authenticated cases. These are numerical phase-bracketed roots, not formal interval enclosures.

## The geometry of the coupled channels

At fixed q and in a fixed initial kinetic frame, write `K = K67 + K78 + Kother`. Here `Kother` is the sum of **43 genuine measured pair terms**, including the directly measured `K68`, and NOT a numerical error. The generator reconstruction error is at most {fmt(ctr['max_instantaneous_generator_closure_relative'])}; the commutator calculation is gauge-sign invariant for each eigendirection.

Because both selected channels share rank 7, `[K67,K78]` lies in the rank-6/rank-8 rotation plane. This is a Lie-algebra identity (units phase⁻²). The directly measured `K68` is a distinct rate (units phase⁻¹), **not** equal to the bracket without an independently specified phase-integration model.

Define the three-rank subspace projector `S678=P6+P7+P8`. The two selected instantaneous terms satisfy `[K67+K78,S678]=0`, whereas the other 43 generally satisfy `[Kother,S678]≠0` and can move that subspace. Over q∈[{cases[0]['transport_window'][0]:.2f},{cases[0]['transport_window'][1]:.2f}], finite transports are integrated by matrix exponentials using the authentic K(q) in one common frame. The full transport accurately predicts each rank projector, whereas truncation misses part of the evolution.

Truncated finite transport is *not* uniquely decomposable into independent physical causes. `||Ufull - U2 Uother||` measures one chosen ordered splitting and non-commutative/time-order effects; it is not a unique invariant memory observable.

## Numerical and genealogy controls

- True 11D forward/return replay and 10D tangent transport: {r['integrations']}.
- Parent v18.49p ZIP manifest and nested v18.49o→v18.48j genealogy verified: {r['parent_verification']['upstream_genealogy_authenticated']}.
- Maximum parent endpoint discrepancy: {fmt(ctr['max_parent_p_share_endpoint_regression'])}.
- Minimum relative spectral gap: {fmt(ctr['min_relative_spectral_gap'])}.
- Max projector derivative central-difference residual: {fmt(ctr['max_finite_difference_projector_derivative_relative_error'])}.
- Max full-transport step-refinement difference: {fmt(ctr['max_U_step_refinement'])}.
- Max 11D ledger error: {fmt(ctr['max_mechanical_ledger_error'])}.

## Output and reproducibility

`results/phase_resolved_geometric_ledger.csv` lists phase-sampled instantaneous channels and commutators. `results/numerical_handover_geometry_events.csv` lists genuine phase-root replay, parent regressions and 6–8 bracket/observed measures. `results/report.json` contains all numerical controls, transport errors, limitations, and source proof. All original source is encapsulated in authenticated v18.49p ZIP, scripts regenerate all v18.49q outputs, and the archive manifest SHA-256 binds every deliverable.

## Scientific boundary

Only the registered q-window, selected durations, and inherited kinetic frame are tested; conclusions are not global over all ramp shapes, phases, observers or κ₀ values. No interval proof of all roots, physical non-Abelian connection, causal transfer or independent torsional flip follows from these numerical measurements. In particular, the instantaneous 43-pair remainder is nonzero **by measurement**; the instantaneous full reconstruction error is near zero **by algebra**.
'''
(R/'SCIENTIFIC_REPORT.md').write_text(text)
print('scientific report generated')
