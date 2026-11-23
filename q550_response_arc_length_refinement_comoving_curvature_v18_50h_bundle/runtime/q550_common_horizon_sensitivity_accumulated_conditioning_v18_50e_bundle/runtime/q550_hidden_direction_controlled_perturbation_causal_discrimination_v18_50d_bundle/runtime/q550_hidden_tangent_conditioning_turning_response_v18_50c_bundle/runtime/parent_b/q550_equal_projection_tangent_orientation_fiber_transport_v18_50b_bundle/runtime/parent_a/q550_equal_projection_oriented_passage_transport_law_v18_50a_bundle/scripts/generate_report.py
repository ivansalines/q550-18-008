#!/usr/bin/env python3
"""Generate restrained scientific report from measured, replayed v18.50a results."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1];report=json.loads((R/'results/report.json').read_text())
with (R/'results/oriented_equal_projection_passages.csv').open() as f:P=list(csv.DictReader(f))
f=lambda z,k:float(z[k]);sample=next((z for z in P if z['kappa_kind']=='original' and abs(f(z,'ramp_xi')-.24)<1e-10 and z['shape']=='beta:2:2'),P[0])
a1=[f(z,'signed_area_x_theta1') for z in P];a2=[f(z,'signed_area_x_theta2') for z in P]
L=['# v18.50a — Equal-Projection Oriented Passage & Transport-Law Audit','',
 '## Classification',f"`{report['classification']}`",'',
 '## Authentic measurements',
 f"- Physical Q550 11D return cases replayed: {report['counts']['successful_cases']}; failed: {report['counts']['failed_cases']}.",
 f"- Matched x passages measured: {len(P)} of {report['counts']['parent_matched_passages']} authenticated parent events.",
 f"- Opposite-sign x crossing rates: {report['statistics']['opposed_x_branch_fraction']:.1%}.",
 f"- Area θ₁ range: [{min(a1):.9g}, {max(a1):.9g}] x·rad; positive share: {report['statistics']['theta1_area_positive_fraction']:.1%}.",
 f"- Area θ₂ range: [{min(a2):.9g}, {max(a2):.9g}] x·rad; positive share: {report['statistics']['theta2_area_positive_fraction']:.1%}.",
 f"- Max signed-area quadrature refinement: {report['statistics']['maximum_area_quadrature_refinement_error']:.3e} x·rad.",
 f"- Max endpoint triad projector regression against v18.49x: {report['statistics']['maximum_parent_x_projector_difference']:.3e}.",
 '','## Defining the oriented passage measure','',
 'For each solved event pair ξ₁<ξ₂ with x(ξ₁)=x(ξ₂)=x*, compute the phase-coordinate integral',
 '`A_j = ∫[ξ₁,ξ₂] (x(ξ)−x*) dθ_j/dξ dξ`, with j=1,2.',
 'The projected curve in (x,θ_j) is closed by a vertical connector at constant x=x*, whose integral contribution is zero. The sign depends on the chosen coordinate orientation; it reverses if the path orientation is reversed.',
 'The end-to-end angular transport `Δθ_j = θ_j(ξ₂)−θ_j(ξ₁)` is independently checked against the integrated RHS. The spectrum-derived triad projector gap is calculated separately in the same common kinetic frame, never called an oriented projector angle.',
 '','## Representative measured passage','',
 f"- κ₀={sample['kappa_kind']}, r={sample['ramp_xi']}, shape={sample['shape']}; ξ₁={f(sample,'xi_in'):.9f}, ξ₂={f(sample,'xi_out'):.9f}; |Δx|={abs(f(sample,'x_return_error')):.3e}.",
 f"- Δθ₁={f(sample,'theta1_transport_rad'):.9g} rad; Δθ₂={f(sample,'theta2_transport_rad'):.9g} rad.",
 f"- Signed areas: A₁={f(sample,'signed_area_x_theta1'):.9g}, A₂={f(sample,'signed_area_x_theta2'):.9g} x·rad.",
 f"- Triad projector gap={f(sample,'triad_projector_gap'):.9g}; radial locus gap={f(sample,'radial_locus_gap'):.9g}.",
 '','## Delimiting the result','']
L.extend('- '+v for v in report['limitations'])
ratio=json.loads((R/'results/co_transport_ratio_diagnostic.json').read_text())
rv=ratio['area_ratio_theta2_over_theta1']
L.extend(['','## Descriptive two-channel co-transport ratio',f"- Aθ₂/Aθ₁ mean={rv['mean']:.9g}, range [{rv['minimum']:.9g}, {rv['maximum']:.9g}] across the same matched passages.",'- The ratio is not independent of the angular RHS, does not establish universal coherence, and pairs in one ramp share a common 11D integration.'])
L.extend(['','The sign of a projected loop area is not by itself evidence of intrinsic physical handedness or a geometric eight-state lift. This audit does not claim an observer-universal physical law or a closed return of the complete state.',''])
(R/'SCIENTIFIC_REPORT.md').write_text('\n'.join(L))
print('v18.50a REPORT_DONE')
