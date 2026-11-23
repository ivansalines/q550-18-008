# Q550 v18.49w — Equal-Locus, Unequal-Posture & In-Ramp Transport Audit

**Classification:** `IN_RAMP_EQUAL_LOCUS_DIAGNOSTIC_NOT_SPATIAL_VOLUME_OR_MATERIAL_MEMORY_CERTIFICATE`

## Authenticated dynamic replay

- 8 genuine 11D ramp integrations; 0 case failures.
- 9,800 nontrivially separated sampled-time pairs (Δσ ≥ 0.2).
- 1,271 near-**x** pairs, with |Δx| at most 10% of the full sampled x excursion for that ramp.
- 0 near-**3D coordinate locus** pairs under the 0.2 scaled-norm threshold.
- 200 symmetric pairs with identical imposed clock phase by construction.

## Per-case statistics

| κ₀ | duration r | near-x | near-3D | min scaled 3D-locus gap |
|---|---:|---:|---:|---:|
| original | 0.120000 | 207 | 0 | 0.263969 |
| original | 0.240000 | 169 | 0 | 0.303726 |
| original | 0.327375 | 160 | 0 | 0.335364 |
| original | 0.500000 | 100 | 0 | 0.352155 |
| autonomous | 0.120000 | 206 | 0 | 0.263972 |
| autonomous | 0.240000 | 169 | 0 | 0.303755 |
| autonomous | 0.327375 | 160 | 0 | 0.335404 |
| autonomous | 0.500000 | 100 | 0 | 0.352101 |

## Illustrative nontrivial pair (original κ₀, duration 0.24)

One pair has σ₁=0.100000 and σ₂=0.683333. It is found by searching the actual reintegrated state and comparing the gauge-invariant triad projectors.

- |Δx| = 1.3393252063e-09 (only 0.00058% of its x excursion)
- Angular-posture coordinate difference: 0.223951910 rad
- Triad projector Frobenius difference: 0.312719854
- Cross-frame relative triad SO(3) angle: 3.230737568°
- But normalized *3D locus* distance = 0.890712928, so this is **not** a full-locus recurrence.

## Threshold sensitivity

The zero near-3D result is *tolerance dependent*. For Δσ ≥ 0.20, raising the normalized 3D threshold from 0.20 to 0.30 accepts 68 pairs (two cases); raising it to 0.40 accepts 694 pairs. If Δσ is raised to 0.25, even the 0.30 threshold accepts zero. These are data-derived reclassifications, not new integrations.

## Reproducibility and invariant controls

- Maximum v18.49v physical endpoint regression: 0.000e+00
- Maximum 11D mechanical ledger discrepancy: 4.389e-12
- Minimum relative spectral gap in evaluated samples: 0.00065954775
- Projector idempotence error max: 5.000e-15
- SO(3) orthogonality error max: 2.027e-15
- Imposed phase mirror mismatch max: 1.110e-16

## Scientific reading and limits

The smaller coordinate x may return nearly to the same value while the two angular coordinates and spectral triad projectors differ. This **supports the narrower projection/posture distinction**, not a complete equal-locus recurrence.
No pair meets the declared normalized full 3D locus criterion at Δσ ≥ 0.2. Thus this run does not certify equal physical position, hidden cubical states, orientation memory or volumetric packing.
The identical clock phase of symmetric times is an identity built into the prescribed cubic ramp. It is a control, not independent evidence of physical closure.
The SO(3) angle is relative to a sign-continuous spectral reference and numerical cross-connection; it is not an angle of a measured rigid body. All distances are coordinate-based and metric-dependent.

## Exact command

```bash
bash run_on_server.sh
```

Use `python3 scripts/run_audit.py --smoke --fail-fast` for a single-case check. To change the comparison convention, adjust `--min-separation`, `--x-fraction`, and `--locus-fraction` and rerun.
