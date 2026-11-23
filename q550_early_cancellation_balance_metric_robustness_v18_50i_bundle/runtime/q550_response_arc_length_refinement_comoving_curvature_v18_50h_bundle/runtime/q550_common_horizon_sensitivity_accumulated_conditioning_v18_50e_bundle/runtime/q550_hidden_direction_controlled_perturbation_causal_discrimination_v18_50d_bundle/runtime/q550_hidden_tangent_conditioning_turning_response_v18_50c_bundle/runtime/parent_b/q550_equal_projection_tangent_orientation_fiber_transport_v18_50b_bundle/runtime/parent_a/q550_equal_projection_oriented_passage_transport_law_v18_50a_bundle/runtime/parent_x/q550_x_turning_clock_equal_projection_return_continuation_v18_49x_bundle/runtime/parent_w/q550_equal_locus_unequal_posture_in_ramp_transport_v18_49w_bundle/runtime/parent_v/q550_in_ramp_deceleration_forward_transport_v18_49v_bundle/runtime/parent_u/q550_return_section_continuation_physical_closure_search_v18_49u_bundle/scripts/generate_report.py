"""Summarize genuine numerical outputs without upgrading a no-closure result."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/report.json').read_text())
a=r['best_config_candidate'];b=r['best_joint_candidate']
lines=['# v18.49u — Return-Section Continuation & Physical Closure Search',
'','## Classification',r['status'],'',
'**This is a finite numerical search, not a global no-closure theorem or a material-memory certificate.**','',
'## Genuine physical integrations',
'- Forward 11D integrations: '+str(r['counts']['physical_forward_reintegrations']),
'- Return 11D integrations: '+str(r['counts']['physical_return_reintegrations']),
'- Optimized sections: '+str(r['counts']['optimized_candidate_sections']),
'- Strict closed candidates: '+str(r['counts']['strict_closure_candidates']),
'- Evaluation failures: '+str(r['counts']['evaluation_failures']),'',
'## Minimum configuration gap',
'- κ0: '+str(a['kappa_kind'])+'; ramp: '+str(a['ramp_xi']),
'- Gap: '+format(a['config'],'.12g')+'; at forward t='+format(a['anchor_time'],'.8f')+', return t='+format(a['return_time'],'.8f'),
'- Velocity mismatch at same section: '+format(a['velocity'],'.12g'),'',
'## Minimum joint full reversed-state gap',
'- κ0: '+str(b['kappa_kind'])+'; ramp: '+str(b['ramp_xi']),
'- Joint gap: '+format(b['full'],'.12g')+'; configuration='+format(b['config'],'.12g')+'; velocity='+format(b['velocity'],'.12g'),
'- Energy difference: '+format(b['energy_difference'],'.12g'),
'- Lifted phase offset (turns): '+format(b['unwrapped_theta_turns'],'.12g'),
'- Projector gap (if selected for 10D): '+str(b['spectral_projector_distance']),'',
'## Interpretation',
'Optimization changes the two observation times and the ramp duration across a finite sampled range, but never adjusts the physical state or inserts a canonical endpoint connector.',
'Configuration and reverse-velocity minima are different criteria; energy and common-frame projector comparisons are independent gates.',
'The velocity reversal at the turning point is externally imposed. No match is automatically a spontaneous physical reversal.',
'No strict closure means no physical material-memory conclusion; a strict candidate would still require convergence and a separate causal memory test.',
'','## Methodological boundaries']+['- '+x for x in r['limitations']]
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
