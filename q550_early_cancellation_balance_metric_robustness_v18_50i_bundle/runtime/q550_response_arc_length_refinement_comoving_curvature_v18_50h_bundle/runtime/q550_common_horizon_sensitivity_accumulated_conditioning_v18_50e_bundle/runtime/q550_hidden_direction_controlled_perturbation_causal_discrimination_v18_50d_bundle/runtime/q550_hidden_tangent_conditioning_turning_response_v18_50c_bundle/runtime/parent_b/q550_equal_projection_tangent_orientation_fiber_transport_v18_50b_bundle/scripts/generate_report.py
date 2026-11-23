#!/usr/bin/env python3
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1];res=R/'results'
report=json.loads((res/'report.json').read_text());rows=list(csv.DictReader((res/'equal_projection_tangent_pairs.csv').open()))
central=next((v for v in rows if v['kappa_kind']=='original' and v['shape']=='beta:2:2' and abs(float(v['ramp_xi'])-.24)<1e-10),rows[0]);s=report['statistics'];n=report['counts']
f=lambda x:f'{float(x):.8g}'
text=f'''# v18.50b — Equal-Projection Tangent Orientation & Fiber-Transport Audit

**Classification:** `{report['classification']}`

## Execution and provenance

- Genuine Q550 11D replay using the full authenticated v18.50a input archive and its v18.49x ancestry.
- Cases succeeded: **{n['successful_cases']}**. Failed: **{n['failed_cases']}**.
- Matched equal-x passages evaluated: **{n['authenticated_equal_x_passages_replayed']}** / {n['parent_passages']}.
- Maximum authenticated parent projection difference: {f(s['max_parent_x_projection_error'])}.
- Opposing x crossing rate in all measured pairs: {s['all_opposite_x']}.

## Direct result

The two passes through the same projected x have opposing **x-direction** tangents. Their full tangent vectors remain distinct in a five-coordinate state and in the ten-coordinate dynamical chart; the angle depends strongly on the chosen chart metric. Across tested pairs, the 5D span-scaled angle ranges **{f(s['range_angle_5d_span_deg'][0])}°–{f(s['range_angle_5d_span_deg'][1])}°**; its arithmetic mean is **{f(s['mean_angle_5d_span_deg'])}°**. The same 5D directions using native coordinate scales range **{f(s['range_native_5d_angle_deg'][0])}°–{f(s['range_native_5d_angle_deg'][1])}°**.

These are **not invariant physical rotation angles**. The contrast is itself a metric-sensitivity finding.

## Example authentic passage

- κ0 choice: **{central['kappa_kind']}**; ramp r={central['ramp_xi']}; shape `{central['shape']}`.
- First and second crossings ξ = {f(central['xi_in'])}, {f(central['xi_out'])}.
- Equal-x residual: {f(central['equal_projection_residual'])}.
- x tangent dot-sign: cosine {f(central['tangent_x_cos'])}, opposed by construction of two crossing branches.
- 5D tangent angle: **{f(central['angle_5d_deg_native'])}°** native / **{f(central['angle_5d_deg_span'])}°** span-scaled.
- 10D tangent angle: **{f(central['angle_10d_deg_native'])}°** native / **{f(central['angle_10d_deg_span'])}°** span-scaled.
- Span-scaled hidden-tangent shares: **{f(central['fiber_share_5d_in_span'])}** incoming and **{f(central['fiber_share_5d_out_span'])}** outgoing.
- Triad projector distance inherited from parent v18.50a: **{f(central['triad_projector_gap_from_authenticated_parent_a'])}** (not newly integrated).

## A useful comparison with v18.50a

At the selected example the instantaneous θ2′/θ1′ ratio changes from **{f(central['instant_theta2_over_theta1_in'])}** at entry to **{f(central['instant_theta2_over_theta1_out'])}** at exit; the corresponding signed-area ratio reported by the authenticated parent is **{f(central['source_theta2_over_theta1_area_ratio'])}**. The near-uniform area ratio in v18.50a is therefore **not simply a fixed instantaneous angular-rate ratio**. It may still follow from the model's local equations and from the weighting used in the integral; no independent transport law is claimed.

Across all pairs, the instantaneous entry ratio ranges {f(s['range_instantaneous_theta2_theta1_ratio_in'][0])}–{f(s['range_instantaneous_theta2_theta1_ratio_in'][1])}, and the exit ratio ranges {f(s['range_instantaneous_theta2_theta1_ratio_out'][0])}–{f(s['range_instantaneous_theta2_theta1_ratio_out'][1])}.

## Geometry measured

For z=(x,θ1,θ2,θ1′,θ2′), the five-dimensional tangent is obtained from the 11D physical RHS and the directional Jacobian derivative JF. The derivatives are with respect to the model's evolution coordinate ξ, not physical laboratory time. The 10D chart substitutes the logistic x for its latent coordinate, applying its chain rule to the tangent.

Native Euclidean and per-case span-scaled Euclidean chart metrics are explicitly compared. The 'fiber' share means the length fraction of the four coordinates hidden when only x is projected; it is not a canonical Ehresmann connection, a global material fiber, or an intrinsic measure.

The path-turn sum is a finite-resolution sum of successive tangent-direction angles along the section; compare values after increasing `--path-samples` before treating it as numerically converged.

## Non-conclusions

1. Matching x is not matching the full radial locus or the full physical state.
2. A chart-dependent angle is not a laboratory-space body rotation or physically certified flip.
3. No discrete four/eight quadrants were assigned to Q550; the autonomous quadrant rule remains independent.
4. No closed physical return, physical holonomy, material memory, spatial volume or topology has been certified.
5. All pairs within an orbit share a dynamic history; there are not {n['authenticated_equal_x_passages_replayed']} independent experimental replicates.

## Files

`results/equal_projection_tangent_pairs.csv`, `results/case_summary.csv`, `results/tangent_trace_selected.csv`, `results/report.json`, `results/environment.json`, visualization PNGs, original Python scripts, unit tests, recursive authenticated parent ZIP, and SHA-256 manifests.
'''
(R/'SCIENTIFIC_REPORT.md').write_text(text)
print('v18.50b REPORT_DONE')
