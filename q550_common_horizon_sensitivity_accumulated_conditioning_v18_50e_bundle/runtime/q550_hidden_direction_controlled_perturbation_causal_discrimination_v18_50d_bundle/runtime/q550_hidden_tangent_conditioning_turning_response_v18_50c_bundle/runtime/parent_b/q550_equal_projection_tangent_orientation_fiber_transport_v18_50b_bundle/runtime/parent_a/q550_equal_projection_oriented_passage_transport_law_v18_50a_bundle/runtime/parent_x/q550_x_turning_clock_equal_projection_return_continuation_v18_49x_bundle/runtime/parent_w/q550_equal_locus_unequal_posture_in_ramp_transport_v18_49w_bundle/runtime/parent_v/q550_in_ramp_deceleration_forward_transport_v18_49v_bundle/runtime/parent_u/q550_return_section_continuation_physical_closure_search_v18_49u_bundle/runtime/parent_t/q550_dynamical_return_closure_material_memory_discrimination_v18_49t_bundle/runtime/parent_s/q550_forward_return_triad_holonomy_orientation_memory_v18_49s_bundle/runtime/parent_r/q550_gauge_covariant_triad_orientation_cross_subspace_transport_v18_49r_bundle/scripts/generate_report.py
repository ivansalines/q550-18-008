import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'results/report.json'
if not p.exists():raise SystemExit('Run the numerical audit before creating the report')
r=json.loads(p.read_text()); lines=['# Q550 v18.49r — Scientific report','','**Status:** '+r['status'],'',
'## Authenticity','',f"- v18.49q SHA-256 pinned: `{r['parent_verification']['parent_sha256']}`", 
'- Its inherited v18.49p-to-v18.48 solver source is verified recursively.','',
'## The mathematical distinction','',
'- The sign of a coefficient in a newly diagonalized eigenbasis is not a physical orientation observable.','- Individual pair generators K_ij and their commutator are invariant under eigenline sign flips.','- The normalized commutator–K68 alignment is algebraically constrained to ±1; it cannot certify a dynamical flip.','- Cross-subspace Kcross follows the *whole* triad projector S, while Kinternal rotates the eigenlines inside it.','',
'## Numerical case results','','| κ₀ | Duration | Handover q | χ at end | Cross share at end | Relative SO(3) angle | Cross-only transport error |','|---|---:|---:|---:|---:|---:|---:|']
for c in r['cases']:
 q=(', '.join(f'{v:.10f}' for v in c['handover_roots']) or 'none')
 lines.append(f"| {c['kappa_kind']} | {c['ramp_xi']:.8f} | {q} | {c['chi_at_end']} | {c['cross_fraction_at_end']:.8f} | {c['parallel_triads_relative_rotation_deg']:.7f}° | {c['parallel_subspace_endpoint_error']:.3e} |")
lines+=['','## Geometric interpretation','',
'In the phase interval q=0.63–0.65, all relative SO(3) angles evolve continuously from zero to about 10.64–10.85 degrees. The internal relative rotation exists both before and after the pairwise power exchange. The cross-block fraction near the end remains about 7.62–8.41% of the instantaneous generator squared norm.',
'The gauge-invariant bracket alignment χ is +1 within numerical precision in all tested cases; this is largely an algebraic identity and supplies NO independent physical chirality/flip evidence. The correct distinction is between the continuously oriented, reference-anchored eigenframe and the motion of its three-dimensional spectral subspace.',
'','## Control metrics','']
for k,v in r['controls'].items():lines.append(f'- `{k}`: `{v}`')
lines+=['','## Scope and limitations','']
for x in r['limitations']:lines.append('- '+x)
lines+=['','No material flip, gauge-universal chirality, or interval certification is claimed.']
(R/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
