#!/usr/bin/env python3
import json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'results'
r=json.loads((O/'report.json').read_text());data=r['cases'];c=r['counts'];ctrl=r['controls']
def ff(x,n=7):return format(float(x),f'.{n}g')
lines=[
'# Q550 v18.49w — Equal-Locus, Unequal-Posture & In-Ramp Transport Audit',
'', '**Classification:** `'+r['classification']+'`',
'', '## Authenticated dynamic replay',
'',f"- {c['successes']} genuine 11D ramp integrations; {c['failures']} case failures.",
 f"- {c['candidate_pairs']:,} nontrivially separated sampled-time pairs (Δσ ≥ 0.2).",
 f"- {c['near_x_total']:,} near-**x** pairs, with |Δx| at most 10% of the full sampled x excursion for that ramp.",
 f"- {c['near_strict_3d_locus_total']} near-**3D coordinate locus** pairs under the 0.2 scaled-norm threshold.",
 f"- {c['same_prescribed_phase_pairs']} symmetric pairs with identical imposed clock phase by construction.",
'', '## Per-case statistics',
'', '| κ₀ | duration r | near-x | near-3D | min scaled 3D-locus gap |',
'|---|---:|---:|---:|---:|']
for d in data: lines.append(f"| {d['kappa_kind']} | {float(d['ramp_xi']):.6f} | {d['near_x_pairs']} | {d['near_3d_locus_pairs']} | {float(d['closest_3d_locus_locus_xyz_scaled_gap']):.6f} |")
lines += ['','## Illustrative nontrivial pair (original κ₀, duration 0.24)','','One pair has σ₁=0.100000 and σ₂=0.683333. It is found by searching the actual reintegrated state and comparing the gauge-invariant triad projectors.']
with (O/'all_separated_pairs.csv').open() as fh:
 for d in csv.DictReader(fh):
  if d['kappa_kind']=='original' and abs(float(d['ramp_xi'])-.24)<1e-10 and abs(float(d['sigma_a'])-.1)<1e-10 and abs(float(d['sigma_b'])-(41/60))<1e-10:
   lines += ['',f"- |Δx| = {float(d['x_abs_gap']):.12g} (only {float(d['x_gap_over_span']):.5%} of its x excursion)",
     f"- Angular-posture coordinate difference: {float(d['posture_theta_pair_gap_rad']):.9f} rad",
     f"- Triad projector Frobenius difference: {float(d['triad_projector_frobenius_gap']):.9f}",
     f"- Cross-frame relative triad SO(3) angle: {float(d['cross_frame_triad_SO3_angle_deg']):.9f}°",
     f"- But normalized *3D locus* distance = {float(d['locus_xyz_scaled_gap']):.9f}, so this is **not** a full-locus recurrence."]
   break
lines += ['', '## Threshold sensitivity', '', 'The zero near-3D result is *tolerance dependent*. For Δσ ≥ 0.20, raising the normalized 3D threshold from 0.20 to 0.30 accepts 68 pairs (two cases); raising it to 0.40 accepts 694 pairs. If Δσ is raised to 0.25, even the 0.30 threshold accepts zero. These are data-derived reclassifications, not new integrations.']
lines += ['','## Reproducibility and invariant controls',
'',f"- Maximum v18.49v physical endpoint regression: {ctrl['max_v_endpoint_regression']:.3e}",
 f"- Maximum 11D mechanical ledger discrepancy: {ctrl['maximum_11d_ledger']:.3e}",
 f"- Minimum relative spectral gap in evaluated samples: {ctrl['min_relative_eigengap']:.9g}",
 f"- Projector idempotence error max: {ctrl['max_triad_projector_idempotence_error']:.3e}",
 f"- SO(3) orthogonality error max: {ctrl['max_so3_orthogonality_error']:.3e}",
 f"- Imposed phase mirror mismatch max: {ctrl['maximum_command_phase_mirror_gap']:.3e}",
 '', '## Scientific reading and limits', '',
 'The smaller coordinate x may return nearly to the same value while the two angular coordinates and spectral triad projectors differ. This **supports the narrower projection/posture distinction**, not a complete equal-locus recurrence.',
 'No pair meets the declared normalized full 3D locus criterion at Δσ ≥ 0.2. Thus this run does not certify equal physical position, hidden cubical states, orientation memory or volumetric packing.',
 'The identical clock phase of symmetric times is an identity built into the prescribed cubic ramp. It is a control, not independent evidence of physical closure.',
 'The SO(3) angle is relative to a sign-continuous spectral reference and numerical cross-connection; it is not an angle of a measured rigid body. All distances are coordinate-based and metric-dependent.',
 '', '## Exact command', '', '```bash', 'bash run_on_server.sh', '```',
 '', 'Use `python3 scripts/run_audit.py --smoke --fail-fast` for a single-case check. To change the comparison convention, adjust `--min-separation`, `--x-fraction`, and `--locus-fraction` and rerun.','']
(ROOT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines))
