#!/usr/bin/env python3
"""Produce evidence-led scientific note from raw v18.50e outputs."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
with (ROOT/'results/common_horizon_direction_responses.csv').open() as f: rows=list(csv.DictReader(f))
def val(kind,r,shape,mode,horizon=.05):
    return next(x for x in rows if x['kind']==kind and abs(float(x['ramp_xi'])-r)<1e-9 and x['shape']==shape and x['mode']==mode and abs(float(x['horizon_xi'])-horizon)<1e-9)
def f(x):return f'{float(x):.6f}'
lines=['# v18.50e — Common-Horizon Sensitivity & Accumulated Conditioning Audit','',
'**Classification:** `'+r['classification']+'`','',
'## Why this control is needed','',
'The v18.50d gain grows along ramps but each natural turning state is different. This audit (A) keeps identical elapsed evolution horizons for each authentic natural turning, and (B) imposes identical initial 11D state, event time, initial clock phase, pooled 4D metric and elapsed horizon while changing the future commanded ramp. These are two different counterfactual comparisons.','',
'## Measured result at Δξ = 0.05','',
'| κ₀ | r | natural turning gain | common-seed gain |','|---|---:|---:|---:|']
for kind in ('original','autonomous'):
  for rr in (.18,.24,.327375,.5):
    a=val(kind,rr,'beta:2:2','natural_turn');b=val(kind,rr,'beta:2:2','same_seed')
    lines.append(f'| {kind} | {rr:.6f} | {f(a["gain"])} | {f(b["gain"])} |')
lines.extend(['','Cubic vs quintic, r=0.24:', '', '| κ₀ | Protocol | Cubic gain | Quintic gain |','|---|---|---:|---:|'])
for kind in ('original','autonomous'):
  for mode in ('natural_turn','same_seed'):
    a=val(kind,.24,'beta:2:2',mode);b=val(kind,.24,'beta:3:3',mode)
    lines.append(f'| {kind} | {mode} | {f(a["gain"])} | {f(b["gain"])} |')
a0=val('original',.24,'beta:2:2','same_seed',0);a=val('original',.24,'beta:2:2','same_seed')
lines.extend(['','## Local-versus-transported linear response ledger','',
'For each endpoint state y(t), let g(y) be the *normalized 4D hidden structural jet*. Under a symmetric perturbation of the x-logit state at the source event, δy(t) is the transported state tangent. The endpoint derivative is decomposed, in the stated coordinate chart, as', '',
'`Dg[y(t)] δy(t) = Dg[y(t)] e_x + Dg[y(t)] (δy(t) − e_x)`.', '',
'This is a **linearized endpoint-coordinate identity**, not proof that a physical direct cause and an independent memory mechanism can be separately intervened upon. Vector magnitudes do not add and partial cancellations are possible.','',
'Example, original κ₀, cubic r=0.24, common seed:', '',
'| Δξ | total gain | frozen endpoint-x gain | accumulated component magnitude | cosine of components |',
'|---:|---:|---:|---:|---:|'])
for h in (0,.0125,.025,.0375,.05):
    v=val('original',.24,'beta:2:2','same_seed',h)
    lines.append(f'| {h:.4f} | {f(v["gain"])} | {f(v["frozen_endpoint_x_gain"])} | {f(v["transported_component_gain"])} | {float(v["split_alignment_cos"]):+.5f} |')
lines.extend(['',f'At the source event, the local direction response has gain {f(a0["gain"])}; by Δξ=0.05, the final response is {f(a["gain"])}. The larger endpoint response involves state tangent transport, but its decomposition is chart-dependent.','',
'## Verification','',
'- Original 11D Q550 RHS and structural hidden jet reused from the byte-pinned v18.50d recursive lineage.',
'- Every short-run test uses a single fixed initial state and identical elapsed horizons for the same-seed comparison.',
'- No failures among '+str(r['counts']['11D_IVPs_short'])+' short IVPs; cases '+str(r['counts']['natural_cases'])+' natural + '+str(r['counts']['same_seed_cases'])+' same seed.',
'- Maximum relative difference between the IVP-centered directional response and the transported-tangent chain rule: '+format(r['results']['max_linearized_response_relative_residual'],'.4e')+'.',
'- Maximum absolute linear split residual: '+format(r['results']['max_split_residual'],'.4e')+'.',
'',
'## Scope / nonclaims','',
'- The scalar gain depends on the chosen pooled metric and on normalization of the hidden four-jet.',
'- Source-kick amplitude is a mathematical perturbation in the logit chart, not an independently accessible physical actuator.',
'- The same-seed protocol holds the 11D initial state and initial clock phase fixed; different future ramp signs and phase excursions are deliberate counterfactual inputs.',
'- No discontinuity, bifurcation, physical memory, geometric 8-octant realization or spatial volume is established.',
'- Growth with duration may be smooth and depends on the specified horizon, metric, and source protocol.',
'',
'## Files','',
'`results/common_horizon_direction_responses.csv`, `results/report.json`, the four PNG figures, executable scripts and inherited pinned sendback with original Python solver.',
''])
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines))
print('Scientific report generated')
