#!/usr/bin/env python3
"""Generate an evidence-bounded narrative from run_audit.py output."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
rep=json.loads((OUT/'report.json').read_text())
with (OUT/'controlled_intervention_responses.csv').open() as f: rows=list(csv.DictReader(f))
with (OUT/'amplitude_linearity_checks.csv').open() as f: drift=list(csv.DictReader(f))
small=min(float(x['epsilon']) for x in rows)
def get(kind,r,intervention,shape='beta:2:2'):
 return next(a for a in rows if a['kind']==kind and abs(float(a['ramp_xi'])-r)<1e-9 and a['shape']==shape and a['intervention']==intervention and abs(float(a['epsilon'])-small)<1e-12)
def fmt(v):return f'{float(v):.8g}'
lines=['# v18.50d — Hidden-Direction Controlled Perturbation & Causal Discrimination Audit','',
'**Classification:** `'+rep['classification']+'`','',
'## What was actually intervened on','',
'The authentic v18.50c cases determine the natural x-turning state. From precisely the SAME baseline state and at the SAME event, symmetric ±ε interventions are made separately to (1) the logit coordinate y[8] of x, (2) angular coordinate θ₁=y[2], or (3) the prescribed drive clock via a compact phase bump whose phase AND rate differences vanish at the endpoints. The historical physical RHS is not modified. The structural hidden jet and one pooled metric reproduce v18.50c.','',
'The drive clock pulse is not amplitude-equivalent to a unit logit or angular-state kick, so raw gains must not be ranked as physical strengths. State kicks generally change initial energy and are mathematical interventions, not a proposed experimental actuator.','',
'## Numerical evidence','',
'- Source sendback SHA-256: `'+rep['ancestry']['v18_50c_sha256']+'`.',
'- Cases: '+str(rep['counts']['cases'])+'; 11D perturbed IVPs: '+str(rep['counts']['controlled_ivps'])+'; failed cases: '+str(rep['counts']['failed_cases'])+'.',
'- Largest relative centered-derivative drift across the tested amplitudes: '+fmt(rep['results']['maximum_linear_response_drift'])+'.',
'- Analytic structural x→hidden RHS Jacobian versus independent physical-RHS finite difference, maximum relative discrepancy: '+fmt(rep['results']['maximum_direct_jacobian_vs_physical_rhs_error'])+'.',
'- The external drive pulse returns the prescribed phase to the baseline at its end: '+str(rep['results']['all_drive_pulse_theta_endpoints_match'])+'.','',
'### Original κ₀, cubic ramp (smallest perturbation ε)','',
'| Ramp r | ∥∂ε ûh∥ from x kick | θ₁ kick | drive pulse | hidden-rate response share for x kick |','|---:|---:|---:|---:|---:|']
for r in (.18,.24,.327375,.5):
 x=get('original',r,'x_logit_kick');h=get('original',r,'theta1_kick');d=get('original',r,'compensated_drive_pulse')
 lines.append(f"| {r:g} | {fmt(x['direction_gain'])} | {fmt(h['direction_gain'])} | {fmt(d['direction_gain'])} | {100*float(x['rate_direction_fraction']):.2f}% |")
lines+=['','### Shape control at r=0.24 (original κ₀)','',
'| Shape | x-kick gain | θ₁-kick gain | drive-pulse gain |','|---|---:|---:|---:|']
for shape in ('beta:2:2','beta:3:3'):
 x=get('original',.24,'x_logit_kick',shape);h=get('original',.24,'theta1_kick',shape);d=get('original',.24,'compensated_drive_pulse',shape)
 lines.append(f"| {shape} | {fmt(x['direction_gain'])} | {fmt(h['direction_gain'])} | {fmt(d['direction_gain'])} |")
lines+=['','## Decision: conditioning versus correlation','',
'**Supported:** Within the authenticated Q550 model, the structural Jacobian of hidden field components with respect to x-logit is nonzero and independently checked by finite differences. Reintegrating with x-only kicks produces a nonzero hidden-direction response in all tested ramps. An independent θ₁ kick and a matched-endpoint drive pulse produce distinct response families. Local gains vary smoothly over the investigated amplitudes and ramp durations; no discontinuous regime boundary has been detected in that small range.','',
'**Not supported:** The intervention does not prove that a physically separate x actuator exists, that x alone caused the observed natural turning, or that the spatially hidden sector is a physical fiber. Nor does the scan rule out thresholds outside the tested range or demonstrate the cubical quadrant construction. The direction response is chart- and metric-dependent.','',
'## Figures and numerical files','',
'- `controlled_hidden_direction_gain.png`: gain by intervention and ramp.','- `hidden_sensitivity_coordinate_partition.png`: angular versus angular-rate response.','- `sensitivity_vector_direction_continuation.png`: orientation changes of sensitivity vector.','- `amplitude_and_shape_sensitivity.png`: amplitude and quintic/cubic controls.','- `controlled_intervention_responses.csv`: full symmetric perturbation ledger.','- `source_jacobian_at_turning.csv`: local structural cross derivative and independent RHS check.','- `amplitude_linearity_checks.csv`: finite-amplitude drift.','',
'## Next discriminating question','',
'Can the direct x→hidden cross-Jacobian contribution be ablated or shadowed while holding the same clock and starting state, and can an independently maintained hidden response survive that change? Such an experiment must declare that it changes the model and cannot be silently called physical transport.','']
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines))
print('Generated scientific report')
